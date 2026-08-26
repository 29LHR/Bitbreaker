from tkinter import messagebox

import customtkinter as ctk
import matplotlib

from cipherlib import CipherBase

matplotlib.use("Agg")
import io

import matplotlib.pyplot as plt
from PIL import Image


class distribution(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Letter Distribution", "#3498db")

    def decrypt(self):
        text = self.get_cipher_text()
        if text is None:
            return

        frequency = self.calculate_frequency(text)
        if not frequency:
            messagebox.showinfo("Distribution Error", "Cipher text has no letters to analyze.")
            return

        self.plot_distribution(frequency)

    def calculate_frequency(self, text):
        frequency = {}
        for char in text:
            if char.isalpha():
                char = char.lower()
                frequency[char] = frequency.get(char, 0) + 1
        return frequency

    def plot_distribution(self, frequency):
        self.ensure_decrypts_window()
        
        for widget in self.results_card.winfo_children():
            widget.destroy()
        
        self.results_card.grid_rowconfigure(0, weight=0)
        self.results_card.grid_rowconfigure(1, weight=0)
        
        letters = sorted(frequency.keys())
        counts = [frequency[ch] for ch in letters]
        
        english_freq = {
            'a': 8.17, 'b': 1.49, 'c': 2.78, 'd': 4.25, 'e': 12.70,
            'f': 2.23, 'g': 2.02, 'h': 6.09, 'i': 6.97, 'j': 0.15,
            'k': 0.77, 'l': 4.03, 'm': 2.41, 'n': 6.75, 'o': 7.51,
            'p': 1.93, 'q': 0.10, 'r': 5.99, 's': 6.33, 't': 9.06,
            'u': 2.76, 'v': 0.98, 'w': 2.36, 'x': 0.15, 'y': 1.97, 'z': 0.07
        }
        
        total = sum(counts)
        observed_pct = [c / total * 100 for c in counts]
        expected_pct = [english_freq.get(ch, 0) for ch in letters]
        
        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#f0f0f0' if ctk.get_appearance_mode() == "Light" else '#1e1e1e')
        ax.set_facecolor('white' if ctk.get_appearance_mode() == "Light" else '#2b2b2b')
        
        bar_color = '#1f6aa5'
        expected_color = '#e74c3c'
        
        ax.bar(letters, observed_pct, color=bar_color, alpha=0.8, label='Observed', width=0.6)
        ax.plot(letters, expected_pct, color=expected_color, marker='o', linewidth=2, markersize=5, label='English Expected')
        
        ax.set_xlabel('Letters', fontsize=12, color='#333' if ctk.get_appearance_mode() == "Light" else '#ddd')
        ax.set_ylabel('Frequency (%)', fontsize=12, color='#333' if ctk.get_appearance_mode() == "Light" else '#ddd')
        ax.set_title('Letter Frequency Distribution', fontsize=14, weight='bold', color='#333' if ctk.get_appearance_mode() == "Light" else '#ddd')
        ax.legend(fontsize=11, facecolor='white' if ctk.get_appearance_mode() == "Light" else '#2b2b2b')
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(colors='#333' if ctk.get_appearance_mode() == "Light" else '#ddd')
        
        for spine in ax.spines.values():
            spine.set_color('#ccc' if ctk.get_appearance_mode() == "Light" else '#444')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        
        img = Image.open(buf)
        img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        
        img_label = ctk.CTkLabel(self.results_card, image=img_tk, text="")
        img_label.image = img_tk
        img_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        stats_text = "Frequency Analysis:\n\n"
        for ch, cnt in zip(letters, counts):
            stats_text += f"  {ch.upper()}: {cnt} ({cnt/total*100:.1f}%)\n"
        
        stats_label = ctk.CTkLabel(
            self.results_card,
            text=stats_text,
            font=ctk.CTkFont(family="Menlo", size=11),
            text_color=("gray30", "gray70"),
            justify="left",
            anchor="nw"
        )
        stats_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        if self.decrypts_win is None:
            return

        self.decrypts_win.deiconify()
        self.decrypts_win.lift()
        self.root.log_activity("Letter Distribution", f"Analyzed {len(frequency)} unique letters")