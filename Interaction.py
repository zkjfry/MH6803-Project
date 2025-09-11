import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from data_manager import DataManager


class UserInteractionManager:
    """User interaction management class"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def show_add_transaction_dialog(self, parent):
        """Show add transaction dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("Add Transaction Record")
        dialog.geometry("400x350")
        dialog.transient(parent)
        dialog.grab_set()

        # Center dialog
        dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create form
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Date
        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(main_frame, textvariable=date_var, width=30)
        date_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        # Type
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, sticky='w', pady=5)
        type_var = tk.StringVar(value="expense")
        type_combo = ttk.Combobox(main_frame, textvariable=type_var, width=27)
        type_combo['values'] = ('income', 'expense')
        type_combo.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Category
        ttk.Label(main_frame, text="Category:").grid(row=2, column=0, sticky='w', pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=27)
        category_combo.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Update category options
        def update_categories(*args):
            if type_var.get() == 'income':
                category_combo['values'] = self.data_manager.data['categories']['income']
            else:
                category_combo['values'] = self.data_manager.data['categories']['expense']
            category_var.set('')

        type_var.trace('w', update_categories)
        update_categories()

        # Amount
        ttk.Label(main_frame, text="Amount:").grid(row=3, column=0, sticky='w', pady=5)
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(main_frame, textvariable=amount_var, width=30)
        amount_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=4, column=0, sticky='w', pady=5)
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(main_frame, textvariable=desc_var, width=30)
        desc_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        def save_transaction():
            try:
                # Input validation
                if not all([date_var.get(), type_var.get(), category_var.get(),
                            amount_var.get(), desc_var.get()]):
                    messagebox.showerror("Error", "Please fill in all fields")
                    return

                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return

                # Validate date format
                datetime.strptime(date_var.get(), '%Y-%m-%d')

                transaction = {
                    'date': date_var.get(),
                    'type': type_var.get(),
                    'category': category_var.get(),
                    'amount': amount,
                    'description': desc_var.get()
                }

                if self.data_manager.add_transaction(transaction):
                    messagebox.showinfo("Success", "Transaction record added")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Save failed")

            except ValueError:
                messagebox.showerror("Error", "Please enter valid amount and date format (YYYY-MM-DD)")

        ttk.Button(button_frame, text="Save", command=save_transaction).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

        return dialog

    def show_import_dialog(self, parent):
        """Show import data dialog"""
        file_path = filedialog.askopenfilename(
            parent=parent,
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                if self.data_manager.import_from_csv(file_path):
                    messagebox.showinfo("Success", "Data imported successfully")
                    return True
                else:
                    messagebox.showerror("Error", "Data import failed, please check file format")
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"Import error: {str(e)}")
                return False
        return False

    def show_export_dialog(self, parent):
        """Show export data dialog"""
        file_path = filedialog.asksaveasfilename(
            parent=parent,
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                transactions = self.data_manager.get_transactions()
                if transactions:
                    df = pd.DataFrame(transactions)
                    df = df[['date', 'type', 'category', 'amount', 'description']]
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    messagebox.showinfo("Success", "Data exported successfully")
                    return True
                else:
                    messagebox.showwarning("Warning", "No data to export")
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"Export error: {str(e)}")
                return False
        return False
