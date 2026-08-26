import re
import string
from tkinter import messagebox

import customtkinter as ctk

CARD_BG = ("white", "gray17")
TITLE_FG = ("gray10", "gray90")
SUBTLE_FG = ("gray30", "gray70")
PRIMARY = "#1f6aa5"
PRIMARY_HOVER = "#1a5a8a"
SECONDARY_BG = ("gray85", "gray25")
SECONDARY_HOVER = ("gray75", "gray35")
ACCENT_GREEN = "#107c41"
ACCENT_ORANGE = "#e67e22"
ACCENT_PURPLE = "#9b59b6"

class CipherBase:
    def __init__(self, root, name, accent_color=PRIMARY):
        self.root = root
        self.name = name
        self.accent_color = accent_color
        self.accent_hover = self._darken_color(accent_color)
        self.window = None
        self.decrypts_win = None
        self.decrypts_scroll = None
        self.present = []
        self.setup_window()
        self._load_cipher_text()

    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        factor = 0.8
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def setup_window(self):
        self.window = ctk.CTkToplevel(self.root)
        self.window.title(self.name)
        self.window.geometry("520x580")
        self.window.minsize(480, 520)
        self.window.transient(self.root)
        self.window.grab_set()
        
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color=("gray96", "gray10"),
            scrollbar_button_color=("gray70", "gray30")
        )
        main_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        main_frame.grid_columnconfigure(0, weight=1)
        
        card = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=16)
        card.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(card, fg_color=self.accent_color, corner_radius=16)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text=self.name,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=(20, 16))
        
        self._create_action_buttons(card)
        
        self.decrypts_display = ctk.CTkTextbox(
            card,
            font=ctk.CTkFont(family="Menlo", size=12),
            corner_radius=10,
            fg_color=("gray98", "gray12"),
            text_color=TITLE_FG,
            border_width=1,
            border_color=("gray75", "gray25"),
            height=300,
            wrap="word"
        )
        self.decrypts_display.grid(row=5, column=0, padx=20, pady=(8, 20), sticky="ew")
        self.decrypts_display.configure(state="disabled")

    def _create_action_buttons(self, parent):
        buttons = [
            ("🔓 Decrypt", self.decrypt, self.accent_color, self.accent_hover),
            ("📝 Change Cipher Text", self.change_cipher_text, SECONDARY_BG[0], SECONDARY_HOVER[0]),
            ("👁 View Cipher Text", self.view_cipher_text, SECONDARY_BG[0], SECONDARY_HOVER[0]),
            ("✕ Close", self.close, ("#e74c3c", "#c0392b"), ("#c0392b", "#a93226")),
        ]
        
        for idx, (text, cmd, fg, hover) in enumerate(buttons):
            btn = ctk.CTkButton(
                parent,
                text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=40,
                corner_radius=10,
                fg_color=fg,
                hover_color=hover,
                text_color="white" if fg not in [SECONDARY_BG[0], "gray85"] else TITLE_FG,
                command=cmd
            )
            btn.grid(row=idx + 1, column=0, padx=20, pady=8, sticky="ew")

    def _load_cipher_text(self):
        try:
            with open("cipherText.txt", "r") as f:
                self.cipher_text = f.read().strip()
        except FileNotFoundError:
            self.cipher_text = ""

    def change_cipher_text(self):
        dialog = CipherTextDialog(self.window, self.cipher_text, self.accent_color)
        self.window.wait_window(dialog)
        if dialog.result is not None:
            self.cipher_text = dialog.result
            with open("cipherText.txt", "w") as f:
                f.write(self.cipher_text)
            messagebox.showinfo("Success", "Cipher text updated successfully.")

    def view_cipher_text(self):
        if not self.cipher_text:
            messagebox.showinfo("Empty", "No cipher text loaded.")
            return
        
        view_win = ctk.CTkToplevel(self.window)
        view_win.title("Cipher Text")
        view_win.geometry("600x500")
        view_win.transient(self.window)
        view_win.grid_columnconfigure(0, weight=1)
        view_win.grid_rowconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(
            view_win,
            font=ctk.CTkFont(family="Menlo", size=13),
            fg_color=("gray98", "gray12"),
            text_color=TITLE_FG,
            wrap="word"
        )
        textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        textbox.insert("1.0", self.cipher_text)
        textbox.configure(state="disabled")

    def get_cipher_text(self):
        if not self.cipher_text:
            messagebox.showinfo("Alert", "No stored cipher text found. Please create one.")
            self.change_cipher_text()
            return None
        return self.cipher_text

    def close(self):
        if self.window:
            self.window.destroy()
        if self.decrypts_win and self.decrypts_win.winfo_exists():
            self.decrypts_win.destroy()

    def decrypt(self):
        pass

    def ensure_decrypts_window(self):
        if self.decrypts_win is None or not self.decrypts_win.winfo_exists():
            self.decrypts_win = ctk.CTkToplevel(self.window)
            self.decrypts_win.title(f"{self.name} Results")
            self.decrypts_win.geometry("600x700")
            self.decrypts_win.transient(self.window)
            self.decrypts_win.grid_columnconfigure(0, weight=1)
            self.decrypts_win.grid_rowconfigure(0, weight=1)
            
            self.decrypts_scroll = ctk.CTkScrollableFrame(
                self.decrypts_win,
                fg_color=("gray96", "gray10"),
                scrollbar_button_color=("gray70", "gray30")
            )
            self.decrypts_scroll.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
            self.decrypts_scroll.grid_columnconfigure(0, weight=1)
            self.decrypts_scroll.grid_rowconfigure(0, weight=1)
            
            self.results_card = ctk.CTkFrame(self.decrypts_scroll, fg_color=CARD_BG, corner_radius=12)
            self.results_card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
            self.results_card.grid_columnconfigure(0, weight=1)
            self.results_card.grid_rowconfigure(0, weight=1)
            
            self.decrypts_win.protocol("WM_DELETE_WINDOW", self.decrypts_win.withdraw)
            self.decrypts_win.withdraw()

    def show_results(self, results, empty_msg="No results found."):
        self.ensure_decrypts_window()
        
        for widget in self.results_card.winfo_children():
            widget.destroy()
        
        if results:
            text = "Possible Decrypts:\n\n"
            for item in results:
                if len(item) == 2:
                    key, decrypted = item
                    text += f"Key: {key}\n{decrypted}\n\n"
                elif len(item) == 3:
                    a, b, decrypted = item
                    text += f"a={a}, b={b}\n{decrypted}\n\n"
                else:
                    text += f"{item}\n\n"
        else:
            text = empty_msg
        
        label = ctk.CTkLabel(
            self.results_card,
            text=text,
            font=ctk.CTkFont(family="Menlo", size=12),
            text_color=TITLE_FG,
            justify="left",
            anchor="nw",
            wraplength=520
        )
        label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.decrypts_win.deiconify()
        self.decrypts_win.lift()

    def check_ioc(self, text):
        filtered_text = [ch.upper() for ch in text if ch.isalpha()]
        N = len(filtered_text)
        
        if N < 2:
            raise ValueError("Text must contain at least two letters to compute IC.")
        
        freq = {letter: 0 for letter in string.ascii_uppercase}
        for ch in filtered_text:
            freq[ch] += 1
        
        numerator = sum(f * (f - 1) for f in freq.values())
        denominator = N * (N - 1)
        return numerator / denominator

    def strip_text(self, text):
        stripped = text.replace(" ", "")
        stripped = stripped.upper()
        stripped = re.sub(r'[^A-Z0-9]', '', stripped)
        return stripped


class CipherTextDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_text, accent_color):
        super().__init__(parent)
        self.result = None
        self.accent_color = accent_color
        self.accent_hover = self._darken_color(accent_color)
        
        self.title("Change Cipher Text")
        self.geometry("500x380")
        self.transient(parent)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self, fg_color=accent_color, corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Change Cipher Text",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=16)
        
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Menlo", size=13),
            fg_color=("gray98", "gray12"),
            text_color=TITLE_FG,
            border_width=1,
            border_color=("gray75", "gray25"),
            wrap="word"
        )
        self.textbox.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.textbox.insert("1.0", current_text)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        btn_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=SECONDARY_BG[0],
            hover_color=SECONDARY_HOVER[0],
            text_color=TITLE_FG,
            command=self.cancel
        ).grid(row=0, column=0, padx=(0, 8), sticky="e")
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=self.accent_color,
            hover_color=self.accent_hover,
            command=self.save
        ).grid(row=0, column=1, sticky="e")
        
        self.textbox.focus_set()

    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        factor = 0.8
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def save(self):
        self.result = self.textbox.get("1.0", "end-1c")
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class FilterConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, accent_color):
        super().__init__(parent)
        self.result = None
        self.accent_color = accent_color
        self.accent_hover = self._darken_color(accent_color)
        
        self.title("Filter Configuration")
        self.geometry("420x420")
        self.transient(parent)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self, fg_color=accent_color, corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=16)
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Filter Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=16)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=20, pady=16, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            content,
            text="Enable checks for candidate filtering:",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70")
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))
        
        self.check_ioc = ctk.BooleanVar(value=True)
        self.check_the = ctk.BooleanVar(value=True)
        self.check_and = ctk.BooleanVar(value=True)
        self.check_etaoin = ctk.BooleanVar(value=False)
        
        ioc_frame = ctk.CTkFrame(content, fg_color="transparent")
        ioc_frame.grid(row=1, column=0, sticky="ew", pady=4)
        ioc_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkCheckBox(
            ioc_frame,
            text="Index of Coincidence (IoC)",
            variable=self.check_ioc,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            ioc_frame,
            text="Range:",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50")
        ).grid(row=0, column=1, sticky="e", padx=(10, 4))
        
        self.ioc_min = ctk.StringVar(value="0.06")
        self.ioc_max = ctk.StringVar(value="0.07")
        
        ctk.CTkEntry(
            ioc_frame,
            textvariable=self.ioc_min,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).grid(row=0, column=2, padx=(0, 2))
        
        ctk.CTkLabel(ioc_frame, text="-", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=2)
        
        ctk.CTkEntry(
            ioc_frame,
            textvariable=self.ioc_max,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).grid(row=0, column=4, padx=(2, 0))
        
        ctk.CTkCheckBox(
            content,
            text="Contains 'the'",
            variable=self.check_the,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=2, column=0, sticky="w", pady=4)
        
        ctk.CTkCheckBox(
            content,
            text="Contains 'and'",
            variable=self.check_and,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=3, column=0, sticky="w", pady=4)
        
        ctk.CTkCheckBox(
            content,
            text="Contains common letters (etaoin shrdlu)",
            variable=self.check_etaoin,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=4, column=0, sticky="w", pady=4)
        
        ctk.CTkLabel(
            content,
            text="At least one check must be enabled",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50")
        ).grid(row=5, column=0, sticky="w", pady=(16, 0))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        btn_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=SECONDARY_BG[0],
            hover_color=SECONDARY_HOVER[0],
            text_color=TITLE_FG,
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
        if not (self.check_ioc.get() or self.check_the.get() or self.check_and.get() or self.check_etaoin.get()):
            return
        try:
            ioc_min = float(self.ioc_min.get())
            ioc_max = float(self.ioc_max.get())
            if ioc_min >= ioc_max or ioc_min < 0 or ioc_max > 1:
                return
        except ValueError:
            return
        self.result = {
            "check_ioc": self.check_ioc.get(),
            "ioc_min": float(self.ioc_min.get()),
            "ioc_max": float(self.ioc_max.get()),
            "check_the": self.check_the.get(),
            "check_and": self.check_and.get(),
            "check_etaoin": self.check_etaoin.get(),
        }
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()


class DictionaryDialog(ctk.CTkToplevel):
    def __init__(self, parent, accent_color):
        super().__init__(parent)
        self.result = None
        self.accent_color = accent_color
        self.accent_hover = self._darken_color(accent_color)
        
        self.title("Select Dictionary")
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
            text="Select Dictionary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=16)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=20, pady=16, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            content,
            text="Choose dictionary for attack:",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        self.dict_var = ctk.StringVar(value="full")
        
        ctk.CTkRadioButton(
            content,
            text="Full Dictionary (~370k words)",
            variable=self.dict_var,
            value="full",
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=1, column=0, sticky="w", pady=4)
        
        ctk.CTkRadioButton(
            content,
            text="Short List (~5k common words)",
            variable=self.dict_var,
            value="short",
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90")
        ).grid(row=2, column=0, sticky="w", pady=4)
        
        ctk.CTkLabel(
            content,
            text="Short list is faster but may miss obscure keys",
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
            fg_color=SECONDARY_BG[0],
            hover_color=SECONDARY_HOVER[0],
            text_color=TITLE_FG,
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
        self.result = self.dict_var.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()