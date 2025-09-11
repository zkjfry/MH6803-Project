import tkinter as tk
from tkinter import ttk


class UIManager:
    """UI interface management class"""

    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.setup_styles()

    def setup_main_window(self):
        """Setup main window"""
        self.root.title("Smart Personal Finance Management System v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Set window icon and minimum size
        self.root.minsize(1000, 700)

        # Center window
        self.center_window()

    def center_window(self):
        """Center window display"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

    def setup_styles(self):
        """Setup UI styles"""
        style = ttk.Style()

        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Custom.TButton', font=('Arial', 10), padding=10)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def create_header_frame(self, parent):
        """Create header title frame"""
        header_frame = tk.Frame(parent, bg='#2E8B57', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Smart Personal Finance Management System",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2E8B57'
        )
        title_label.pack(expand=True)

        return header_frame

    def create_sidebar_frame(self, parent):
        """Create sidebar frame"""
        sidebar_frame = tk.Frame(parent, bg='#e8e8e8', width=200)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 2))
        sidebar_frame.pack_propagate(False)

        return sidebar_frame

    def create_main_content_frame(self, parent):
        """Create main content frame"""
        main_frame = tk.Frame(parent, bg='white')
        main_frame.pack(side='right', fill='both', expand=True, padx=(2, 0))

        return main_frame
