import customtkinter as ctk

from analysis import distribution, ioc
from cipherlib import DictionaryDialog
from ciphers import adfgvx, affine, autokey, beaufort, caesar, hill, jefferson, playfair, transposition, vigenere

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class CodebreakerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Codebreaker")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()
        
        self.current_view = None
        self.activity_log = []
        self.max_activities = 20
        self.show_dashboard()
    
    def DictionaryDialog(self, parent, accent_color):
        return DictionaryDialog(parent, accent_color)

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=("gray92", "gray13"))
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 16), sticky="ew")
        
        ctk.CTkLabel(
            logo_frame,
            text="🔐 Codebreaker",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("gray10", "gray90")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            logo_frame,
            text="Cryptography Dashboard",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", pady=(2, 0))
        
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        
        nav_items = [
            ("🏠 Dashboard", "dashboard", self.show_dashboard),
            ("🔤 Classical Ciphers", "ciphers", self.show_ciphers),
            ("📊 Analysis Tools", "analysis", self.show_analysis),
            ("📁 Cipher Text", "ciphertext", self.show_cipher_text),
            ("⚙️ Settings", "settings", self.show_settings),
        ]
        
        self.nav_buttons = {}
        for idx, (label, key, cmd) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=13, weight="normal"),
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("gray78", "gray25"),
                command=lambda k=key, c=cmd: self._switch_view(k, c)
            )
            btn.grid(row=idx + 2, column=0, padx=12, pady=4, sticky="ew")
            self.nav_buttons[key] = btn
        
        version_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        version_frame.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            version_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        ).pack(anchor="w")

    def _create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray96", "gray10"))
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.content_area = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def _create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=32, corner_radius=0, fg_color=("gray90", "gray15"))
        self.status_bar.grid(row=1, column=1, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=16, sticky="w")
        
        self.cipher_status = ctk.CTkLabel(
            self.status_bar,
            text="No cipher text loaded",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="e"
        )
        self.cipher_status.grid(row=0, column=1, padx=16, sticky="e")
        self._update_cipher_status()

    def _update_cipher_status(self):
        try:
            with open("cipherText.txt", "r") as f:
                text = f.read().strip()
                if text:
                    preview = text[:50] + "..." if len(text) > 50 else text
                    self.cipher_status.configure(text=f"Loaded: {preview}")
                else:
                    self.cipher_status.configure(text="No cipher text loaded")
        except FileNotFoundError:
            self.cipher_status.configure(text="No cipher text loaded")

    def _switch_view(self, key, cmd):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=("gray78", "gray25"),
                    text_color=("gray10", "gray90")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray80")
                )
        cmd()

    def log_activity(self, tool, action):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).astimezone()
        time_str = now.strftime("%H:%M")
        self.activity_log.insert(0, (tool, action, time_str))
        if len(self.activity_log) > self.max_activities:
            self.activity_log = self.activity_log[:self.max_activities]

    def _clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self._clear_content()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nsew", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Welcome to Codebreaker",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Decrypt classical ciphers and analyze ciphertext with professional tools",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        stats_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 24))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        stats = [
            ("🔤", "Classical Ciphers", "10 Available", "Caesar, Affine, Vigenère, Beaufort, Autokey, Playfair, Transposition, Hill, ADFGVX, Jefferson"),
            ("📊", "Analysis Tools", "2 Tools", "IoC, Letter Distribution"),
            ("📁", "Cipher Text", "Ready", "Loaded from cipherText.txt"),
        ]
        
        for idx, (icon, title, value, desc) in enumerate(stats):
            card = self._create_stat_card(stats_frame, icon, title, value, desc)
            card.grid(row=0, column=idx, padx=(0, 12) if idx < 2 else 0, sticky="nsew")
        
        quick_actions = ctk.CTkFrame(self.content_area, fg_color="transparent")
        quick_actions.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
        quick_actions.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(
            quick_actions,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        actions = [
            ("🔍", "Auto-Detect Cipher", "Analyze ciphertext and suggest cipher type", self._auto_detect),
            ("📝", "Load Cipher Text", "Open or edit cipherText.txt", self.show_cipher_text),
        ]
        
        for idx, (icon, title, desc, cmd) in enumerate(actions):
            card = self._create_action_card(quick_actions, icon, title, desc, cmd)
            card.grid(row=1, column=idx, padx=(0, 12) if idx == 0 else 0, sticky="nsew")
        
        recent_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        recent_frame.grid(row=3, column=0, sticky="nsew")
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            recent_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        recent_card = ctk.CTkFrame(recent_frame, corner_radius=12)
        recent_card.grid(row=1, column=0, sticky="nsew")
        recent_card.grid_columnconfigure(0, weight=1)
        for i in range(40):
            recent_card.grid_rowconfigure(i, weight=0)
        
        activities = self.activity_log if self.activity_log else [
            ("No activity yet", "Use the tools to see history here", ""),
        ]
        
        for idx, (tool, action, time) in enumerate(activities):
            is_last = idx == len(activities) - 1
            self._create_activity_row(recent_card, tool, action, time, idx, is_last)

    def _create_stat_card(self, parent, icon, title, value, desc):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("white", "gray17"))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28)
        ).grid(row=0, column=0, padx=20, pady=(20, 8))
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=1, column=0, padx=20, sticky="w")
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1f6aa5", "#3d8bcf")
        ).grid(row=2, column=0, padx=20, sticky="w", pady=(4, 2))
        
        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        ).grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")
        
        return card

    def _create_action_card(self, parent, icon, title, desc, cmd):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("white", "gray17"))
        card.grid_columnconfigure(0, weight=1)
        card.bind("<Button-1>", lambda e: cmd())
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=0, padx=20, pady=16, sticky="ew")
        content.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            content,
            text=icon,
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, rowspan=2, padx=(0, 16))
        
        ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="gray90",
            anchor="w"
        ).grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(
            content,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        ).grid(row=1, column=1, sticky="ew")
        
        arrow = ctk.CTkLabel(
            content,
            text="→",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray40", "gray60")
        )
        arrow.grid(row=0, column=2, rowspan=2, padx=(16, 0))
        
        for widget in [card, content, arrow]:
            widget.bind("<Button-1>", lambda e: cmd())
            widget.bind("<Enter>", lambda e: card.configure(fg_color=("gray92", "gray22")))
            widget.bind("<Leave>", lambda e: card.configure(fg_color=("white", "gray17")))
        
        return card

    def _create_activity_row(self, parent, tool, action, time, idx, is_last):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=idx * 2, column=0, sticky="nsew", padx=16, pady=10)
        row.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            row,
            text=tool,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray10", "gray90"),
            width=140,
            anchor="w"
        ).grid(row=0, column=0, padx=(0, 12))
        
        ctk.CTkLabel(
            row,
            text=action,
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
            anchor="w"
        ).grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(
            row,
            text=time,
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50"),
            width=80,
            anchor="e"
        ).grid(row=0, column=2, padx=(12, 0))
        
        if not is_last:
            sep = ctk.CTkFrame(parent, height=1, fg_color=("gray80", "gray25"))
            sep.grid(row=idx * 2 + 1, column=0, sticky="ew", padx=16)

    def show_ciphers(self):
        self._clear_content()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nsew", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Classical Ciphers",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Decrypt substitution and polyalphabetic ciphers",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        ciphers = [
            ("🔄", "Caesar Cipher", "Shift cipher (ROT-N)", "Simple substitution with fixed shift", "#1f6aa5", lambda: caesar.caesar(self)),
            ("🔐", "Affine Cipher", "ax + b (mod 26)", "Multiplicative + additive substitution", "#107c41", lambda: affine.affine(self)),
            ("🗝️", "Vigenère Cipher", "Polyalphabetic", "Dictionary-based key search", "#9b59b6", lambda: vigenere.vigenere(self)),
            ("🌊", "Beaufort Cipher", "Reciprocal polyalphabetic", "Dictionary-based key search", "#8e44ad", lambda: beaufort.beaufort(self)),
            ("🔑", "Autokey Cipher", "Key = keyword + ciphertext", "Dictionary-based keyword search", "#27ae60", lambda: autokey.autokey(self)),
            ("🔤", "Playfair Cipher", "Digraph substitution", "Dictionary-based key search, all variants", "#e74c3c", lambda: playfair.playfair(self)),
            ("↔️", "Transposition Cipher", "Columnar transposition", "Permutation-based key search", "#34495e", lambda: transposition.transposition(self)),
            ("📐", "Hill Cipher", "Matrix-based (2x2/3x3)", "Linear algebra with mod 26", "#8e44ad", lambda: hill.hill(self)),
            ("📋", "ADFGVX Cipher", "Fractionating + transposition", "WW1 German field cipher", "#c0392b", lambda: adfgvx.adfgvx(self)),
            ("🔘", "Jefferson Disk", "Multi-disk mechanical", "Historical wheel cipher (36 disks)", "#2c3e50", lambda: jefferson.jefferson(self)),
        ]
        
        grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="nsew")
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        grid.grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        for idx, (icon, name, subtitle, desc, color, cmd) in enumerate(ciphers):
            row = idx // 3
            col = idx % 3
            card = self._create_cipher_card(grid, icon, name, subtitle, desc, color, cmd)
            padx = (0, 16) if col < 2 else 0
            pady = (0, 16) if row < 3 else 0
            card.grid(row=row, column=col, padx=padx, pady=pady, sticky="nsew")

    def _create_cipher_card(self, parent, icon, name, subtitle, desc, color, cmd):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=("white", "gray17"))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(4, weight=1)
        
        header = ctk.CTkFrame(card, fg_color=color, corner_radius=16)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=32),
            text_color="white"
        ).grid(row=0, column=0, pady=(20, 8))
        
        ctk.CTkLabel(
            card,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=1, column=0, padx=24, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color
        ).grid(row=2, column=0, padx=24, sticky="w")
        
        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            wraplength=260
        ).grid(row=3, column=0, padx=24, pady=(4, 16), sticky="w")
        
        btn = ctk.CTkButton(
            card,
            text="Open Tool",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=color,
            hover_color=color,
            command=cmd
        )
        btn.grid(row=4, column=0, padx=24, pady=(0, 20), sticky="ew")
        
        return card

    def show_analysis(self):
        self._clear_content()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nsew", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Analysis Tools",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Statistical analysis for cryptanalysis",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        tools = [
            ("📈", "Index of Coincidence", "Measure text randomness", "Identify cipher type by IC value\nEnglish ~0.067, Random ~0.038", "#e67e22", lambda: ioc.ioc(self)),
            ("📊", "Letter Distribution", "Frequency analysis", "Visualize letter frequency\nCompare with English distribution", "#3498db", lambda: distribution.distribution(self)),
        ]
        
        grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="nsew")
        grid.grid_columnconfigure((0, 1), weight=1)
        
        for idx, (icon, name, subtitle, desc, color, cmd) in enumerate(tools):
            card = self._create_cipher_card(grid, icon, name, subtitle, desc, color, cmd)
            card.grid(row=0, column=idx, padx=(0, 16) if idx == 0 else 0, sticky="nsew")
        
        info_card = ctk.CTkFrame(self.content_area, corner_radius=12, fg_color=("#fff3e0", "#2d2000"))
        info_card.grid(row=2, column=0, sticky="nsew", pady=(24, 0))
        info_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            info_card,
            text="💡 Tip: Load cipher text first using the sidebar or Quick Actions",
            font=ctk.CTkFont(size=13),
            text_color=("#bf8600", "#ffb300")
        ).grid(row=0, column=0, padx=20, pady=16, sticky="w")

    def show_cipher_text(self):
        self._clear_content()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nsew", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Cipher Text Manager",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Load, edit, and manage ciphertext for analysis",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        editor_card = ctk.CTkFrame(self.content_area, corner_radius=12, fg_color=("white", "gray17"))
        editor_card.grid(row=1, column=0, sticky="nsew", pady=(0, 16))
        editor_card.grid_columnconfigure(0, weight=1)
        editor_card.grid_rowconfigure(1, weight=1)
        
        toolbar = ctk.CTkFrame(editor_card, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        toolbar.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            toolbar,
            text="Current Cipher Text",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkButton(
            toolbar,
            text="Save",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=6,
            command=self._save_cipher_text
        ).grid(row=0, column=2, padx=(8, 0))
        
        ctk.CTkButton(
            toolbar,
            text="Clear",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=6,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._clear_cipher_text
        ).grid(row=0, column=3, padx=(8, 0))
        
        self.cipher_textbox = ctk.CTkTextbox(
            editor_card,
            font=ctk.CTkFont(family="Menlo", size=13),
            corner_radius=8,
            fg_color=("gray98", "gray12"),
            text_color="gray90",
            border_width=1,
            border_color=("gray75", "gray25")
        )
        self.cipher_textbox.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        
        self._load_cipher_text()
        
        info_card = ctk.CTkFrame(self.content_area, corner_radius=12, fg_color=("white", "gray17"))
        info_card.grid(row=2, column=0, sticky="nsew")
        info_card.grid_columnconfigure((0, 1), weight=1)
        info_card.grid_rowconfigure((0, 1), weight=0)
        
        info_items = [
            ("📄", "File Location", "cipherText.txt in project root"),
            ("🔄", "Auto-Load", "All tools read from this file automatically"),
            ("📝", "Format", "Plain text, any length, non-letters ignored"),
            ("💾", "Persistence", "Changes saved automatically on Save"),
        ]
        
        for idx, (icon, title, desc) in enumerate(info_items):
            row = idx // 2
            col = idx % 2
            item = ctk.CTkFrame(info_card, fg_color="transparent")
            item.grid(row=row, column=col, padx=20, pady=16, sticky="w")
            
            ctk.CTkLabel(item, text=icon, font=ctk.CTkFont(size=18)).grid(row=0, column=0, rowspan=2, padx=(0, 12))
            ctk.CTkLabel(item, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=("gray10", "gray90"), anchor="w").grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(item, text=desc, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60"), anchor="w").grid(row=1, column=1, sticky="w")

    def _load_cipher_text(self):
        try:
            with open("cipherText.txt", "r") as f:
                text = f.read()
                self.cipher_textbox.delete("1.0", "end")
                self.cipher_textbox.insert("1.0", text)
        except FileNotFoundError:
            self.cipher_textbox.delete("1.0", "end")
            self.cipher_textbox.insert("1.0", "")

    def _save_cipher_text(self):
        text = self.cipher_textbox.get("1.0", "end-1c")
        with open("cipherText.txt", "w") as f:
            f.write(text)
        self._update_cipher_status()
        self.status_label.configure(text="Cipher text saved")
        self.log_activity("Cipher Text", f"Saved ({len(text)} chars)")
        self.after(2000, lambda: self.status_label.configure(text="Ready"))

    def _clear_cipher_text(self):
        self.cipher_textbox.delete("1.0", "end")
        with open("cipherText.txt", "w") as f:
            f.write("")
        self._update_cipher_status()
        self.status_label.configure(text="Cipher text cleared")
        self.log_activity("Cipher Text", "Cleared")
        self.after(2000, lambda: self.status_label.configure(text="Ready"))

    def show_settings(self):
        self._clear_content()
        
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nsew", pady=(0, 24))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Customize Codebreaker appearance and behavior",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        
        appearance_card = ctk.CTkFrame(self.content_area, corner_radius=12, fg_color=("white", "gray17"))
        appearance_card.grid(row=1, column=0, sticky="nsew", pady=(0, 16))
        appearance_card.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            appearance_card,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 16), sticky="w")
        
        ctk.CTkLabel(
            appearance_card,
            text="Theme Mode",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70")
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            appearance_card,
            values=["System", "Light", "Dark"],
            variable=self.theme_var,
            width=180,
            height=36,
            font=ctk.CTkFont(size=12),
            command=self._change_theme
        )
        theme_menu.grid(row=1, column=1, padx=20, pady=(0, 16), sticky="e")
        
        ctk.CTkLabel(
            appearance_card,
            text="Color Theme",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70")
        ).grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
        self.color_var = ctk.StringVar(value="Blue")
        color_menu = ctk.CTkOptionMenu(
            appearance_card,
            values=["Blue", "Green", "Dark Blue"],
            variable=self.color_var,
            width=180,
            height=36,
            font=ctk.CTkFont(size=12),
            command=self._change_color_theme
        )
        color_menu.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="e")
        
        about_card = ctk.CTkFrame(self.content_area, corner_radius=12, fg_color=("white", "gray17"))
        about_card.grid(row=2, column=0, sticky="ew")
        about_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            about_card,
            text="About",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        ).grid(row=0, column=0, padx=20, pady=(20, 16), sticky="w")
        
        about_text = (
            "Codebreaker v1.0.0\n"
            "A cryptography dashboard for classical cipher decryption and analysis.\n\n"
            "Built with Python & CustomTkinter\n"
            "Designed for macOS with native look and feel"
        )
        ctk.CTkLabel(
            about_card,
            text=about_text,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

    def _change_theme(self, mode):
        ctk.set_appearance_mode(mode.lower())
        self.status_label.configure(text=f"Theme changed to {mode}")
        self.after(2000, lambda: self.status_label.configure(text="Ready"))

    def _change_color_theme(self, theme):
        theme_map = {"Blue": "blue", "Green": "green", "Dark Blue": "dark-blue"}
        ctk.set_default_color_theme(theme_map.get(theme, "blue"))
        self.status_label.configure(text=f"Color theme changed to {theme} (restart to apply fully)")
        self.after(3000, lambda: self.status_label.configure(text="Ready"))

    def _auto_detect(self):
        self.status_label.configure(text="Auto-detection not yet implemented")
        self.after(2000, lambda: self.status_label.configure(text="Ready"))

if __name__ == "__main__":
    app = CodebreakerDashboard()
    app.mainloop()