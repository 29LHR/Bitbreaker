import os
from math import gcd

from cipherlib import CipherBase


class affine(CipherBase):
    def __init__(self, root):
        super().__init__(root, "Affine Cipher", "#107c41")

    def close(self):
        super().close()
        file = "decrypts/temp_affine.txt"
        if os.path.exists(file):
            os.remove(file)

    def _mod_inverse(self, a, m):
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None

    def _affine_decrypt_text(self, text, a_inv, b):
        decrypted = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                y = ord(char) - base
                x = (a_inv * (y - b)) % 26
                decrypted += chr(x + base)
            else:
                decrypted += char
        with open("decrypts/temp_affine.txt", "a") as f:
            f.write(f"{a_inv}, {b}:\n {decrypted}\n\n\n")
        return decrypted

    def decrypt(self):
        text = self.get_cipher_text()
        if text is None:
            return

        self.present = []

        for a in range(1, 26):
            if gcd(a, 26) != 1:
                continue

            a_inv = self._mod_inverse(a, 26)
            if a_inv is None:
                continue

            for b in range(26):
                decrypted = self._affine_decrypt_text(text, a_inv, b)
                try:
                    _ = self.check_ioc(decrypted)
                except ValueError:
                    continue

                if "the" in decrypted.lower() and "and" in decrypted.lower():
                    print(f"a={a}, b={b}: {decrypted}")
                    self.present.append([a, b, decrypted])

        with open("decrypts/affine.txt", "w") as f:
            if self.present:
                for a, b, decrypted in self.present:
                    f.write(f"a={a}, b={b}:\n {decrypted}\n\n\n")
            else:
                f.write("No possible decrypts found.\n")

        self.show_results(self.present)
        if self.present:
            self.root.log_activity("Affine Cipher", f"Found {len(self.present)} possible decrypt(s)")
        else:
            self.root.log_activity("Affine Cipher", "No decrypts found")