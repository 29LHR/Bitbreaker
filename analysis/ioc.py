from tkinter import messagebox

from cipherlib import CipherBase


class ioc(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Index of Coincidence", "#e67e22")

    def decrypt(self):
        self.calculate_ioc()

    def calculate_ioc(self):
        text = self.get_cipher_text()
        if text is None:
            return

        try:
            ioc_value = self.check_ioc(text)
        except ValueError:
            messagebox.showinfo("IoC Error", "Cipher text needs at least two letters.")
            return

        self.show_ioc_result(ioc_value)

    def show_ioc_result(self, ioc_value):
        interpretation = ""
        if ioc_value > 0.065:
            interpretation = "🔍 Likely English plaintext or simple substitution cipher"
        elif ioc_value > 0.045:
            interpretation = "⚠️ Possibly polyalphabetic cipher (Vigenère, etc.)"
        else:
            interpretation = "🎲 Likely random text or strong polyalphabetic cipher"

        result_text = (
            f"Index of Coincidence: {ioc_value:.4f}\n\n"
            f"Expected values:\n"
            f"  English text:    ~0.067\n"
            f"  Random text:     ~0.038\n"
            f"  Vigenère (long): ~0.040-0.045\n\n"
            f"{interpretation}"
        )

        self.show_results([], empty_msg=result_text)
        self.root.log_activity("Index of Coincidence", f"IC = {ioc_value:.4f}")