import json
import os
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context

import customtkinter as ctk

from cipherlib import CipherBase, FilterConfigDialog


DISK_COUNT = 36
DISK_LETTERS = 26


def _check_ioc(text):
    filtered_text = [ch.upper() for ch in text if ch.isalpha()]
    n = len(filtered_text)
    if n < 2:
        return 0.0

    freq = {chr(i): 0 for i in range(ord("A"), ord("Z") + 1)}
    for ch in filtered_text:
        freq[ch] += 1

    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = n * (n - 1)
    return numerator / denominator


def _check_etaoin(text):
    lowered = text.lower()
    common = "etaoinshrdlu"
    count = sum(1 for ch in common if ch in lowered)
    return count >= 8


def _generate_standard_disks():
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    disks = []
    for i in range(DISK_COUNT):
        disk = list(base)
        random.seed(i * 12345)
        random.shuffle(disk)
        disks.append(''.join(disk))
    return disks


def _jefferson_decrypt_text(text, disk_order, disk_offsets):
    disks = _generate_standard_disks()
    ordered_disks = [disks[i] for i in disk_order]
    
    clean = ''.join(c.upper() for c in text if c.isalpha())
    result = []
    
    for i, ch in enumerate(clean):
        disk_idx = i % DISK_COUNT
        disk = ordered_disks[disk_idx]
        offset = disk_offsets[disk_idx]
        
        pos = disk.find(ch)
        if pos == -1:
            result.append('?')
            continue
        
        plain_pos = (pos - offset) % DISK_LETTERS
        result.append(disk[plain_pos])
    
    return ''.join(result).lower()


def _generate_disk_orders(max_orders):
    from itertools import permutations, islice
    base_order = list(range(min(6, DISK_COUNT)))
    orders = list(islice(permutations(base_order), max_orders))
    return [list(o) for o in orders]


def _generate_disk_offsets(num_disks, max_offsets):
    offsets_list = []
    for _ in range(max_offsets):
        offsets = [random.randint(0, 25) for _ in range(num_disks)]
        offsets_list.append(offsets)
    return offsets_list


def _scan_key_batch(text, disk_orders, disk_offsets_list, filter_config):
    results = []
    for disk_order in disk_orders:
        num_disks = len(disk_order)
        for offsets in disk_offsets_list:
            decrypted = _jefferson_decrypt_text(text, disk_order, offsets)
            lowered = decrypted.lower()
            
            if filter_config["check_ioc"]:
                ioc = _check_ioc(decrypted)
                if not (filter_config["ioc_min"] < ioc < filter_config["ioc_max"]):
                    continue
            
            if filter_config["check_the"] and "the" not in lowered:
                continue
            
            if filter_config["check_and"] and "and" not in lowered:
                continue
            
            if filter_config["check_etaoin"] and not _check_etaoin(decrypted):
                continue
            
            key_desc = f"Order:{disk_order} Offsets:{offsets}"
            results.append([key_desc, decrypted])
            print("Possible decrypt found with key:", key_desc)
    return results


class jefferson(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Jefferson Disk Cipher", "#2c3e50")
        self.cpu_target = 0.9

    def _worker_count(self):
        cpu_count = os.cpu_count() or 2
        return max(2, int(cpu_count * self.cpu_target))

    def _chunk_keys(self, keys, chunk_size):
        for i in range(0, len(keys), chunk_size):
            yield keys[i:i + chunk_size]

    def decrypt(self):
        self.present = []
        text = self.get_cipher_text()
        if text is None:
            return

        dict_dialog = self.root.DictionaryDialog(self.window, self.accent_color)
        self.window.wait_window(dict_dialog)
        if dict_dialog.result is None:
            return
        
        filter_dialog = FilterConfigDialog(self.window, self.accent_color)
        self.window.wait_window(filter_dialog)
        if filter_dialog.result is None:
            return
        
        filter_config = filter_dialog.result
        
        clean_text = ''.join(c for c in text if c.isalpha())
        if len(clean_text) < 10:
            self.show_results([])
            return
        
        disk_orders = _generate_disk_orders(500)
        disk_offsets_list = _generate_disk_offsets(6, 100)
        
        if not disk_orders or not disk_offsets_list:
            self.show_results([])
            return

        workers = self._worker_count()
        chunk_size = max(10, len(disk_orders) // workers)
        chunks = list(self._chunk_keys(disk_orders, chunk_size))
        total_chunks = len(chunks)

        with open("decrypts/jefferson.txt", "w") as f:
            f.write("")

        progress_win = self._create_progress_window(total_chunks)

        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork")) as executor:
            futures = [
                executor.submit(_scan_key_batch, clean_text, batch, disk_offsets_list, filter_config)
                for batch in chunks
            ]

            for completed, future in enumerate(as_completed(futures), 1):
                self.present.extend(future.result())
                self._update_progress(progress_win, completed, total_chunks)

        progress_win.destroy()

        if self.present:
            with open("decrypts/jefferson.txt", "a") as f:
                f.writelines(f"Key {key}:\n {decrypted}\n\n\n" for key, decrypted in self.present)

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Jefferson Disk Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Jefferson Disk Cipher", "No decrypts found")

    def _create_progress_window(self, total):
        win = ctk.CTkToplevel(self.window)
        win.title("Jefferson Disk Cipher - Attack Progress")
        win.geometry("450x200")
        win.transient(self.window)
        win.grab_set()
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            win,
            text="Dictionary Attack in Progress...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, pady=(20, 10))

        self.progress_bar = ctk.CTkProgressBar(win, width=380, height=20)
        self.progress_bar.grid(row=1, column=0, padx=30, pady=10)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            win,
            text=f"0 / {total} chunks completed",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.progress_label.grid(row=2, column=0, pady=(0, 10))

        self.progress_found = ctk.CTkLabel(
            win,
            text="Matches found: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.accent_color
        )
        self.progress_found.grid(row=3, column=0, pady=(0, 20))

        win.update()
        return win

    def _update_progress(self, win, completed, total):
        if not win.winfo_exists():
            return
        progress = completed / total
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{completed} / {total} chunks completed")
        self.progress_found.configure(text=f"Matches found: {len(self.present)}")
        win.update()