import json
import os
from math import gcd
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context

import customtkinter as ctk
import numpy as np

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


def _mod_inverse_matrix(matrix, mod=26):
    try:
        det = int(round(np.linalg.det(matrix))) % mod
        if gcd(det, mod) != 1:
            return None
        
        det_inv = None
        for x in range(1, mod):
            if (det * x) % mod == 1:
                det_inv = x
                break
        
        if det_inv is None:
            return None
        
        matrix_mod = matrix % mod
        adj = np.round(det * np.linalg.inv(matrix_mod)).astype(int) % mod
        inv = (det_inv * adj) % mod
        return inv
    except:
        return None


def _hill_decrypt_text(text, key_matrix, block_size):
    key_matrix = np.array(key_matrix).reshape(block_size, block_size)
    inv_matrix = _mod_inverse_matrix(key_matrix)
    if inv_matrix is None:
        return ""
    
    clean = ''.join(c.upper() for c in text if c.isalpha())
    if len(clean) % block_size != 0:
        clean += 'X' * (block_size - len(clean) % block_size)
    
    result = []
    for i in range(0, len(clean), block_size):
        block = [ord(c) - ord('A') for c in clean[i:i+block_size]]
        vec = np.array(block)
        dec = (inv_matrix @ vec) % 26
        result.extend(chr(int(c) + ord('A')) for c in dec)
    
    return ''.join(result)


def _generate_hill_keys(block_size, max_keys):
    keys = []
    if block_size == 2:
        for a in range(1, 26):
            for b in range(26):
                for c in range(26):
                    for d in range(1, 26):
                        mat = [[a, b], [c, d]]
                        det = (a * d - b * c) % 26
                        if gcd(det, 26) == 1:
                            keys.append(mat)
                            if len(keys) >= max_keys:
                                return keys
    elif block_size == 3:
        for a in range(1, 26):
            for b in range(26):
                for c in range(26):
                    for d in range(26):
                        for e in range(1, 26):
                            for f in range(26):
                                for g in range(26):
                                    for h in range(26):
                                        for i in range(1, 26):
                                            mat = [[a, b, c], [d, e, f], [g, h, i]]
                                            try:
                                                det = int(round(np.linalg.det(mat))) % 26
                                                if gcd(det, 26) == 1:
                                                    keys.append(mat)
                                                    if len(keys) >= max_keys:
                                                        return keys
                                            except:
                                                pass
    return keys


def _scan_key_batch(text, keys, filter_config, block_size):
    results = []
    for key_matrix in keys:
        decrypted = _hill_decrypt_text(text, key_matrix, block_size)
        if not decrypted:
            continue
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
        
        key_str = str(key_matrix).replace('\n', ' ')
        results.append([key_str, decrypted])
        print("Possible decrypt found with key:", key_str)
    return results


class hill(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Hill Cipher", "#8e44ad")
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

        block_dialog = HillBlockDialog(self.window, self.accent_color)
        self.window.wait_window(block_dialog)
        if block_dialog.result is None:
            return
        
        block_size = block_dialog.result
        
        filter_dialog = FilterConfigDialog(self.window, self.accent_color)
        self.window.wait_window(filter_dialog)
        if filter_dialog.result is None:
            return
        
        filter_config = filter_dialog.result
        
        clean_text = ''.join(c for c in text if c.isalpha())
        
        keys = _generate_hill_keys(block_size, 10000)
        if not keys:
            self.show_results([])
            return

        workers = self._worker_count()
        chunk_size = max(50, len(keys) // (workers * 4))
        chunks = list(self._chunk_keys(keys, chunk_size))
        total_chunks = len(chunks)

        with open("decrypts/hill.txt", "w") as f:
            f.write("")

        progress_win = self._create_progress_window(total_chunks)

        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork")) as executor:
            futures = [
                executor.submit(_scan_key_batch, clean_text, batch, filter_config, block_size)
                for batch in chunks
            ]

            for completed, future in enumerate(as_completed(futures), 1):
                self.present.extend(future.result())
                self._update_progress(progress_win, completed, total_chunks)

        progress_win.destroy()

        if self.present:
            with open("decrypts/hill.txt", "a") as f:
                f.writelines(f"Key {key}:\n {decrypted}\n\n\n" for key, decrypted in self.present)

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Hill Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Hill Cipher", "No decrypts found")

    def _create_progress_window(self, total):
        win = ctk.CTkToplevel(self.window)
        win.title("Hill Cipher - Attack Progress")
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


class HillBlockDialog(ctk.CTkToplevel):
    def __init__(self, parent, accent_color):
        super().__init__(parent)
        self.result = None
        self.accent_color = accent_color
        self.accent_hover = self._darken_color(accent_color)
        
        self.title("Hill Cipher Block Size")
        self.geometry("400x280")
        self.transient(parent)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self, fg_color=accent_color, corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Select Block Size",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=16)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=20, pady=16, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            content,
            text="Choose matrix block size:",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        self.block_var = ctk.StringVar(value="2")
        
        ctk.CTkRadioButton(
            content,
            text="2x2 Matrix (digraphs)",
            variable=self.block_var,
            value="2",
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=1, column=0, sticky="w", pady=4)
        
        ctk.CTkRadioButton(
            content,
            text="3x3 Matrix (trigraphs)",
            variable=self.block_var,
            value="3",
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=2, column=0, sticky="w", pady=4)
        
        ctk.CTkLabel(
            content,
            text="3x3 is much slower but handles longer keys",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50")
        ).grid(row=3, column=0, sticky="w", pady=(12, 0))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        btn_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"),
            command=self.cancel
        ).grid(row=0, column=0, padx=(0, 8), sticky="e")
        
        ctk.CTkButton(
            btn_frame,
            text="Start Attack",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=self.accent_color,
            hover_color=self.accent_hover,
            command=self.start
        ).grid(row=0, column=1, sticky="e")
    
    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        factor = 0.8
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def start(self):
        self.result = int(self.block_var.get())
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()