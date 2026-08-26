import json
import os
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context

import customtkinter as ctk

from cipherlib import CipherBase, FilterConfigDialog


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


def _transposition_decrypt_text(text, key):
    key = [int(k) for k in str(key)]
    num_cols = len(key)
    num_rows = math.ceil(len(text) / num_cols)
    
    col_lengths = [num_rows] * num_cols
    remainder = len(text) % num_cols
    if remainder:
        sorted_key = sorted(enumerate(key), key=lambda x: x[1])
        for i in range(remainder):
            col_lengths[sorted_key[i][0]] = num_rows - 1
    
    cols = []
    idx = 0
    for length in col_lengths:
        cols.append(text[idx:idx + length])
        idx += length
    
    sorted_key = sorted(enumerate(key), key=lambda x: x[1])
    ordered_cols = [''] * num_cols
    for rank, (orig_idx, _) in enumerate(sorted_key):
        ordered_cols[orig_idx] = cols[rank]
    
    result = []
    for row in range(num_rows):
        for col in range(num_cols):
            if row < len(ordered_cols[col]):
                result.append(ordered_cols[col][row])
    
    return ''.join(result)


def _scan_key_batch(text, keys, filter_config):
    results = []
    for key in keys:
        decrypted = _transposition_decrypt_text(text, key)
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
        
        results.append([str(key), decrypted])
        print("Possible decrypt found with key:", key)
    return results


def _generate_keys(max_key_length, num_keys):
    keys = []
    for length in range(2, max_key_length + 1):
        from itertools import permutations
        for perm in permutations(range(length)):
            keys.append(''.join(map(str, perm)))
            if len(keys) >= num_keys:
                return keys
    return keys


class transposition(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Transposition Cipher", "#34495e")
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
        max_key_length = min(10, len(clean_text) // 2)
        
        if max_key_length < 2:
            self.show_results([])
            return
        
        keys = _generate_keys(max_key_length, 50000)
        if not keys:
            self.show_results([])
            return

        workers = self._worker_count()
        chunk_size = max(100, len(keys) // (workers * 4))
        chunks = list(self._chunk_keys(keys, chunk_size))
        total_chunks = len(chunks)

        with open("decrypts/transposition.txt", "w") as f:
            f.write("")

        progress_win = self._create_progress_window(total_chunks)

        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork")) as executor:
            futures = [
                executor.submit(_scan_key_batch, clean_text, batch, filter_config)
                for batch in chunks
            ]

            for completed, future in enumerate(as_completed(futures), 1):
                self.present.extend(future.result())
                self._update_progress(progress_win, completed, total_chunks)

        progress_win.destroy()

        if self.present:
            with open("decrypts/transposition.txt", "a") as f:
                f.writelines(f"Key {key}:\n {decrypted}\n\n\n" for key, decrypted in self.present)

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Transposition Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Transposition Cipher", "No decrypts found")

    def _create_progress_window(self, total):
        win = ctk.CTkToplevel(self.window)
        win.title("Transposition Cipher - Attack Progress")
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