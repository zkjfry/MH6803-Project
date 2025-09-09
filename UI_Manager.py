# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import sys

# ===== Color constants =====
GREEN = "#2E8B57"
RED = "#CD5C5C"
BLUE = "#4169E1"
ORANGE = "#FF8C00"
SIDEBAR_BG = "#e8e8e8"
APP_BG = "#FFFFFF"
PANEL_BG = "#F6F7F9"
TEXT_BG = "#F8F9FA"

class UIManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.styles = None
        self.active_nav_btn = None
        self.pages = {}        # name -> Frame
        self.main_area = None  # main content
        self.current_page = None
        self.setup_main_window()
        self.setup_styles()

    # ===== Window Basic =====
    def setup_main_window(self):
        self.root.title("Smart Personal Finance Manager")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=APP_BG)
        self.center_window()
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # shortcut key��Ctrl/? + 1..5
        mod = "Command" if sys.platform == "darwin" else "Control"
        self.root.bind_all(f"<{mod}-1>", lambda e: self._nav_hotkey("Dashboard"))
        self.root.bind_all(f"<{mod}-2>", lambda e: self._nav_hotkey("Transactions"))
        self.root.bind_all(f"<{mod}-3>", lambda e: self._nav_hotkey("Budgets"))
        self.root.bind_all(f"<{mod}-4>", lambda e: self._nav_hotkey("Reports"))
        self.root.bind_all(f"<{mod}-5>", lambda e: self._nav_hotkey("Import/Export"))

    def _nav_hotkey(self, name):
        mapping = {
            "Dashboard":     lambda p: self.create_dashboard_layout(p, self._fake_balance(), self._fake_suggestions()),
            "Transactions":  self._build_transactions_page,
            "Budgets":       self._build_budgets_page,
            "Reports":       self._build_reports_page,
            "Import/Export": self._build_importexport_page,
        }
        self.show_page(name, mapping[name])

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ===== Styles =====
    def setup_styles(self):
        self.styles = ttk.Style()
        try:
            self.styles.theme_use("clam")
        except tk.TclError:
            pass

        self.styles.configure("Title.TLabel",
                              font=("Arial", 20, "bold"),
                              foreground="white",
                              background=GREEN)
        self.styles.configure("Heading.TLabel",
                              font=("Arial", 14, "bold"),
                              background=APP_BG)
        self.styles.configure("Nav.TButton",
                              font=("Arial", 11),
                              padding=(12, 8),
                              background=SIDEBAR_BG)
        self.styles.map("Nav.TButton",
                        background=[("active", "#dcdcdc")])
        self.styles.configure("Treeview.Heading",
                              font=("Arial", 11, "bold"))
        self.styles.configure("Top.TButton",
                              font=("Arial", 11, "bold"),
                              padding=(10, 6))
        # Active style
        self.styles.configure("NavActive.TButton",
                              background="#d0e8dc",
                              padding=(12, 8),
                              relief="groove",
                              font=("Arial", 11, "bold"))

    # ===== Header =====
    def create_header_frame(self, parent):
        header = tk.Frame(parent, height=80, bg=GREEN)
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_rowconfigure(0, weight=1)

        title = tk.Label(header, text="Smart Finance",
                         fg="white", bg=GREEN, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=16)

        right_box = tk.Frame(header, bg=GREEN)
        right_box.grid(row=0, column=1, sticky="e", padx=16)
        ttk.Button(right_box, text="Settings", style="Top.TButton").pack()

        return header

    # ===== Sidebar =====
    def create_sidebar_frame(self, parent):
        sidebar = tk.Frame(parent, width=200, bg=SIDEBAR_BG)
        sidebar.grid_propagate(False)

        btns = []
        nav_items = [
            ("Dashboard",     lambda p: self.create_dashboard_layout(p, self._fake_balance(), self._fake_suggestions())),
            ("Transactions",  self._build_transactions_page),
            ("Budgets",       self._build_budgets_page),
            ("Reports",       self._build_reports_page),
            ("Import/Export", self._build_importexport_page),
        ]

        for idx, (text, builder) in enumerate(nav_items):
            b = ttk.Button(sidebar, text=text, style="Nav.TButton")
            # Left button press to toggle
            b.bind("<Button-1>", lambda e, n=text, build=builder, bt=b: self._switch_page(n, build, bt))
            b.pack(fill="x", padx=10, pady=6)
            btns.append(b)

        # Default Dashboard Highlight
        self.set_active_nav(btns[0])
        return sidebar

    def set_active_nav(self, btn: ttk.Button):
        if self.active_nav_btn is not None:
            self.active_nav_btn.configure(style="Nav.TButton")
        btn.configure(style="NavActive.TButton")
        self.active_nav_btn = btn

    # ===== Main Content =====
    def create_main_content_frame(self, parent):
        self.main_area = tk.Frame(parent, bg=APP_BG)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        return self.main_area

    def _switch_page(self, name, builder, btn):
        self.set_active_nav(btn)
        self.show_page(name, builder)
        self.root.update_idletasks()  # Refresh the drawing immediately

    def show_page(self, name: str, builder):
        if self.current_page is not None and self.current_page.winfo_exists():
            self.current_page.pack_forget()

        page = self.pages.get(name)
        if page is None or not page.winfo_exists():
            page = builder(self.main_area)   # The builder only returns the Frame, don't pack it inside.
            self.pages[name] = page

        self.current_page = page
        self.current_page.pack(fill="both", expand=True)

    # ===== Tool: Amount Format =====
    def _fmt_money(self, x, symbol="$"):
        try:
            return f"{symbol}{float(x):,.2f}"
        except Exception:
            return str(x)

    # ===== Generic button factory (hover effect) =====
    def create_button_with_style(self, parent, text, command, bg_color="#ececec"):
        btn = tk.Button(parent,
                        text=text,
                        command=command,
                        relief="flat",
                        font=("Arial", 11),
                        padx=12, pady=6,
                        bg=bg_color,
                        activebackground="#dcdcdc")
        def on_enter(_): btn.configure(bg="#dcdcdc")
        def on_leave(_): btn.configure(bg=bg_color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # (Optional) ttk version hover button factory
    def create_ttk_button_with_hover(self, parent, text, command):
        base = "Action.TButton"
        hover = "ActionHover.TButton"
        self.styles.configure(base, font=("Arial", 11), padding=(12, 6))
        self.styles.configure(hover, font=("Arial", 11, "bold"), padding=(12, 6))
        b = ttk.Button(parent, text=text, command=command, style=base)
        b.bind("<Enter>", lambda e: b.configure(style=hover))
        b.bind("<Leave>", lambda e: b.configure(style=base))
        return b

    # ===== Dashboard =====
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, height=92, highlightthickness=0, bd=0)
        card.grid_propagate(False)
        inner = tk.Frame(card, bg=color)
        inner.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(inner, text=title, font=("Arial", 16, "bold"),
                 fg="white", bg=color).pack(anchor="center")
        tk.Label(inner, text=f"{value}", font=("Arial", 14, "bold"),
                 fg="white", bg=color).pack(anchor="center", pady=(4, 0))
        return card

    def create_dashboard_layout(self, parent, balance_info, suggestions):
        frame = tk.Frame(parent, bg=APP_BG)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Top Statistics Card
        cards = tk.Frame(frame, bg=APP_BG)
        cards.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1, uniform="cards")

        info = [
            ("Income",       self._fmt_money(balance_info.get("total_income", 0.0)), GREEN),
            ("Expense",      self._fmt_money(balance_info.get("total_expense", 0.0)), RED),
            ("Balance",      self._fmt_money(balance_info.get("balance", 0.0)), BLUE),
            ("Transactions", f"{balance_info.get('transaction_count', 0):,}", ORANGE),
        ]
        for col, (label, val, color) in enumerate(info):
            c = self.create_stat_card(cards, label, val, color)
            c.grid(row=0, column=col, sticky="nsew", padx=8)

        # suggestion area
        panel = tk.Frame(frame, bg=PANEL_BG, highlightthickness=1, highlightbackground="#E2E5E9")
        panel.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ttk.Label(panel, text="Smart Suggestions", style="Heading.TLabel",
                  background=PANEL_BG).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        text = tk.Text(panel, height=8, wrap="word",
                       bg=TEXT_BG, bd=0, highlightthickness=1, highlightbackground="#E2E5E9",
                       font=("Arial", 11))
        text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        content = "\n".join(f" {s}" for s in (suggestions or []))
        text.insert("1.0", content)
        text.tag_configure("li", spacing3=4)
        text.tag_add("li", "1.0", "end")
        text.configure(state="disabled")

        return frame

    # ===== Placeholder page (Transactions integrates the button factory example)=====
    def _build_transactions_page(self, parent):
        f = tk.Frame(parent, bg=APP_BG)
        ttk.Label(f, text="Transactions", style="Heading.TLabel", background=APP_BG)\
            .pack(anchor="w", padx=16, pady=(16, 8))

        # ！！ Toolbar: Using the button factory (hover effect) ！！
        bar = tk.Frame(f, bg=APP_BG)
        bar.pack(fill="x", padx=16, pady=(0, 8))
        self.create_button_with_style(bar, "Add",    lambda: print("Add clicked")).pack(side="left", padx=(0, 8))
        self.create_button_with_style(bar, "Import", lambda: print("Import clicked")).pack(side="left", padx=(0, 8))
        self.create_button_with_style(bar, "Export", lambda: print("Export clicked")).pack(side="left")

        # ！！ Table placeholder (can subsequently replace DataManager's real data) ！！
        host = tk.Frame(f, bg=APP_BG)
        host.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        cols = ("date","type","category","amount","description")
        tv = ttk.Treeview(host, columns=cols, show="headings", height=12)
        vs = ttk.Scrollbar(host, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=vs.set)
        for c in cols:
            tv.heading(c, text=c.capitalize())
            tv.column(c, width=120 if c != "description" else 300, anchor="w")
        tv.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        # sample data
        sample = [
            ("2025-08-01","expense","Food", self._fmt_money(12.8), "Lunch"),
            ("2025-08-01","income","Salary", self._fmt_money(3500), "Monthly"),
        ]
        for row in sample:
            tv.insert("", "end", values=row)

        return f

    def _build_budgets_page(self, parent):
        f = tk.Frame(parent, bg=APP_BG)
        ttk.Label(f, text="Budgets Page (placeholder)",
                  style="Heading.TLabel", background=APP_BG).pack(anchor="w", padx=16, pady=16)
        return f

    def _build_reports_page(self, parent):
        f = tk.Frame(parent, bg=APP_BG)
        ttk.Label(f, text="Reports Page (placeholder)",
                  style="Heading.TLabel", background=APP_BG).pack(anchor="w", padx=16, pady=16)
        return f

    def _build_importexport_page(self, parent):
        f = tk.Frame(parent, bg=APP_BG)
        ttk.Label(f, text="Import/Export Page (placeholder)",
                  style="Heading.TLabel", background=APP_BG).pack(anchor="w", padx=16, pady=16)
        return f

    # ===== fake data =====
    def _fake_balance(self):
        return {"total_income":12345.67,"total_expense":4567.89,"balance":7777.78,"transaction_count":128}

    def _fake_suggestions(self):
        return [
            "Low savings rate in last 3 months, suggest fixed transfer date.",
            "Food spending > 40%, consider weekly limit or meal prep.",
            "2 unusual high expenses detected, check if one-time purchase.",
        ]

# ===== Demo =====
def demo():
    root = tk.Tk()
    ui = UIManager(root)

    header = ui.create_header_frame(root)
    header.grid(row=0, column=0, columnspan=2, sticky="ew")

    sidebar = ui.create_sidebar_frame(root)
    sidebar.grid(row=1, column=0, sticky="ns")

    main = ui.create_main_content_frame(root)
    main.grid(row=1, column=1, sticky="nsew")

    #  Dashboard
    ui.show_page("Dashboard", lambda p: ui.create_dashboard_layout(p, ui._fake_balance(), ui._fake_suggestions()))

    root.mainloop()

if __name__ == "__main__":
    demo()
