from cipherlib import CipherBase


class caesar(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Caesar Cipher", "#1f6aa5")

    def decrypt(self):
        text = self.get_cipher_text()
        if text is None:
            return

        self.present = []

        for i in range(26):
            decrypted = ""
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shifted = chr((ord(char) - base - i) % 26 + base)
                    decrypted += shifted
                else:
                    decrypted += char

            try:
                ioc_val = self.check_ioc(decrypted)
                if 0.06 < ioc_val < 0.07 and "the" in decrypted.lower() and "and" in decrypted.lower():
                    print(f"Shift {i}: {decrypted}")
                    self.present.append([i, decrypted])
            except ValueError:
                continue

        with open("decrypts/caesar.txt", "w") as f:
            if self.present:
                for shift, decrypted in self.present:
                    f.write(f"Shift {shift}:\n {decrypted}\n\n\n")
            else:
                f.write("No possible decrypts found.\n")

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Caesar Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Caesar Cipher", "No decrypts found")