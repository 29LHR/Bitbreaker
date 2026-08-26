import json
import os
import string
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context

from cipherlib import CipherBase

PLAYFAIR_SHIFTS = [
    ('RD', 'Right', 'Down'),
    ('RU', 'Right', 'Up'),
    ('RR', 'Right', 'Right'),
    ('LD', 'Left', 'Down'),
    ('LU', 'Left', 'Up'),
    ('LR', 'Left', 'Right'),
    ('LL', 'Left', 'Left'),
    ('DD', 'Down', 'Down'),
    ('DU', 'Down', 'Up'),
    ('DR', 'Down', 'Right'),
    ('UD', 'Up', 'Down'),
    ('UU', 'Up', 'Up'),
    ('UR', 'Up', 'Right'),
]


def _generate_playfair_matrix(key):
    key = key.upper().replace("J", "I")
    matrix = []
    used = set()

    for char in key:
        if char not in used and char.isalpha():
            used.add(char)
            matrix.append(char)

    for char in string.ascii_uppercase:
        if char not in used and char != 'J':
            used.add(char)
            matrix.append(char)

    result = [matrix[i:i+5] for i in range(0, 25, 5)]
    pos_cache = {}
    for i, row in enumerate(result):
        for j, c in enumerate(row):
            pos_cache[c] = (i, j)
    return result, pos_cache


def _decrypt_pair(matrix, pos_cache, a, b, row_shift, col_shift):
    a = a.upper().replace("J", "I")
    b = b.upper().replace("J", "I")

    pos_a = pos_cache.get(a)
    pos_b = pos_cache.get(b)

    if pos_a is None or pos_b is None:
        return ("", "")

    row1, col1 = pos_a
    row2, col2 = pos_b

    if row1 == row2:
        match row_shift:
            case 'Left':
                return (matrix[row1][(col1 - 1) % 5], matrix[row2][(col2 - 1) % 5])
            case 'Right':
                return (matrix[row1][(col1 + 1) % 5], matrix[row2][(col2 + 1) % 5])
            case 'Down':
                return (matrix[(row1 + 1) % 5][col1], matrix[(row2 + 1) % 5][col2])
            case 'Up':
                return (matrix[(row1 - 1) % 5][col1], matrix[(row2 - 1) % 5][col2])
            case _:
                return (matrix[row1][(col1 + 1) % 5], matrix[row2][(col2 + 1) % 5])

    elif col1 == col2:
        match col_shift:
            case 'Left':
                return (matrix[row1][(col1 - 1) % 5], matrix[row2][(col2 - 1) % 5])
            case 'Right':
                return (matrix[row1][(col1 + 1) % 5], matrix[row2][(col2 + 1) % 5])
            case 'Down':
                return (matrix[(row1 + 1) % 5][col1], matrix[(row2 + 1) % 5][col2])
            case 'Up':
                return (matrix[(row1 - 1) % 5][col1], matrix[(row2 - 1) % 5][col2])
            case _:
                return (matrix[(row1 + 1) % 5][col1], matrix[(row2 + 1) % 5][col2])

    return (matrix[row1][col2], matrix[row2][col1])


def _playfair_decrypt_text(text, key, row_shift, col_shift):
    matrix, pos_cache = _generate_playfair_matrix(key)
    print(key, row_shift, col_shift)
    text = text.upper().replace("J", "I").replace(" ", "")
    plaintext = ""
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else 'X'
        i += 2
        p1, p2 = _decrypt_pair(matrix, pos_cache, a, b, row_shift, col_shift)
        plaintext += p1 + p2
    return plaintext.lower()


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


def _scan_key_batch(text, keys):
    results = []
    for key in keys:
        for shift_name, row_shift, col_shift in PLAYFAIR_SHIFTS:
            decrypted = _playfair_decrypt_text(text, key, row_shift, col_shift)
            ioc = _check_ioc(decrypted)
            lowered = decrypted.lower()
            if 0.06 < ioc < 0.07 and "the" in lowered and "and" in lowered:
                results.append([f"{key} ({shift_name})", decrypted])
                print(f"Possible decrypt found with key: {key} ({shift_name})")
    return results


class playfair(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Playfair Cipher", "#e74c3c")
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
        
        dict_file = "shortwords.json" if dict_dialog.result == "short" else "words.json"
        
        with open(dict_file, "r") as f:
            words = json.load(f)

        keys = list(words.keys())
        if not keys:
            self.show_results([])
            return

        workers = self._worker_count()
        chunk_size = max(500, len(keys) // (workers * 12))
        chunks = list(self._chunk_keys(keys, chunk_size))
        total_chunks = len(chunks)

        with open("decrypts/playfair.txt", "w") as f:
            f.write("")

        progress_win = self._create_progress_window(total_chunks)
        
        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork")) as executor:
            futures = [
                executor.submit(_scan_key_batch, text, batch)
                for batch in chunks
            ]

            for completed, future in enumerate(as_completed(futures), 1):
                self.present.extend(future.result())
                self._update_progress(progress_win, completed, total_chunks)

        progress_win.destroy()

        if self.present:
            with open("decrypts/playfair.txt", "a") as f:
                f.writelines(f"Key {key}:\n {decrypted}\n\n\n" for key, decrypted in self.present)

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Playfair Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Playfair Cipher", "No decrypts found")

    def _create_progress_window(self, total):
        import customtkinter as ctk
        win = ctk.CTkToplevel(self.window)
        win.title("Playfair Cipher - Attack Progress")
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