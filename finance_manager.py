"""
Smart Personal Finance Management System
MH6803 Mini Project - Group Project
7-member team complete implementation

Team Assignment:
- Member 1: Project Manager & UI Design (15%)
- Member 2: Core Algorithm Development (20%)
- Member 3: Data Management Module (15%)
- Member 4: Visualization Module (15%)
- Member 5: User Interaction Features (15%)
- Member 6: Testing & Documentation (10%)
- Member 7: Advanced Features & Integration (10%)
"""

from datetime import datetime
import os
from data_manager import DataManager
from finance_calculator import FinanceCalculator
from UI_Manager import UIManager
from Interaction import UserInteractionManager
from visualization import VisualizationManager
from advancedFeatureManager import AdvancedFeaturesManager
from test_manager import TestManager
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class FinanceManagerApp:
    """Main application class"""

    def __init__(self):
        self.root = tk.Tk()

        # Initialize all managers
        self.data_manager = DataManager()
        self.calculator = FinanceCalculator(self.data_manager)
        self.ui_manager = UIManager(self.root)
        self.interaction_manager = UserInteractionManager(self.data_manager)
        self.visualization_manager = VisualizationManager(self.calculator)
        self.advanced_features = AdvancedFeaturesManager(self.data_manager, self.calculator)
        self.test_manager = TestManager(self.data_manager, self.calculator)

        # Setup interface
        self.setup_ui()
        self.current_view = "dashboard"
        self.show_dashboard()

    def setup_ui(self):
        """Setup user interface"""
        # Create main frames
        self.header_frame = self.ui_manager.create_header_frame(self.root)

        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.sidebar_frame = self.ui_manager.create_sidebar_frame(self.main_container)
        self.main_content_frame = self.ui_manager.create_main_content_frame(self.main_container)

        # Setup sidebar
        self.setup_sidebar()

    def setup_sidebar(self):
        """Setup sidebar menu"""
        # Menu title
        menu_title = tk.Label(
            self.sidebar_frame,
            text="Function Menu",
            font=('Arial', 14, 'bold'),
            bg='#e8e8e8'
        )
        menu_title.pack(pady=(20, 10))

        # Menu buttons
        menu_buttons = [
            ("Financial Overview", self.show_dashboard),
            ("Transaction Management", self.show_transactions),
            ("Data Analysis", self.show_analytics),
            ("Monthly Report", self.show_reports),
            ("System Test", self.show_system_test),
            ("Data Management", self.show_data_management)
        ]

        for text, command in menu_buttons:
            btn = tk.Button(
                self.sidebar_frame,
                text=text,
                command=command,
                font=('Arial', 11),
                bg='white',
                fg='#333',
                relief='flat',
                padx=20,
                pady=10,
                anchor='w',
                width=18
            )
            btn.pack(fill='x', padx=10, pady=2)

            # Mouse hover effect
            def on_enter(e, button=btn):
                button.config(bg='#e3f2fd')

            def on_leave(e, button=btn):
                button.config(bg='white')

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show financial overview"""
        self.clear_main_content()
        self.current_view = "dashboard"

        # Create overview frame
        dashboard_frame = tk.Frame(self.main_content_frame, bg='white')
        dashboard_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            dashboard_frame,
            text="Financial Overview",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(pady=(0, 20))

        # Create summary cards
        summary_frame = tk.Frame(dashboard_frame, bg='white')
        summary_frame.pack(fill='x', pady=10)

        # Get financial data
        balance_info = self.calculator.calculate_balance()
        suggestions = self.calculator.generate_smart_suggestions()

        # Summary cards
        cards_data = [
            ("Total Income", f"${balance_info['total_income']:.2f}", "#2E8B57"),
            ("Total Expense", f"${balance_info['total_expense']:.2f}", "#CD5C5C"),
            ("Net Income", f"${balance_info['balance']:.2f}", "#4169E1"),
            ("Transaction Count", str(balance_info['transaction_count']), "#FF8C00")
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = tk.Frame(summary_frame, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='both', expand=True, padx=5)

            tk.Label(card, text=title, font=('Arial', 10), bg=color, fg='white').pack(pady=(10, 5))
            tk.Label(card, text=value, font=('Arial', 14, 'bold'), bg=color, fg='white').pack(pady=(0, 10))

        # Smart suggestions
        suggestions_frame = tk.LabelFrame(dashboard_frame, text="Smart Suggestions", font=('Arial', 12, 'bold'),
                                          bg='white')
        suggestions_frame.pack(fill='x', pady=20)

        suggestions_text = tk.Text(suggestions_frame, height=6, wrap='word', bg='#f8f9fa', relief='flat')
        suggestions_text.pack(fill='x', padx=10, pady=10)

        for suggestion in suggestions:
            suggestions_text.insert('end', f"• {suggestion}\n\n")

        suggestions_text.config(state='disabled')

        # Quick actions
        actions_frame = tk.LabelFrame(dashboard_frame, text="⚡ Quick Actions", font=('Arial', 12, 'bold'), bg='white')
        actions_frame.pack(fill='x', pady=10)

        action_buttons = [
            ("Add Income", lambda: self.quick_add_transaction('income')),
            ("Add Expense", lambda: self.quick_add_transaction('expense')),
            ("View Analysis", self.show_analytics),
            ("Generate Report", self.show_reports)
        ]

        for i, (text, command) in enumerate(action_buttons):
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                font=('Arial', 10),
                bg='#4169E1',
                fg='white',
                relief='flat',
                padx=20,
                pady=5
            )
            btn.pack(side='left', padx=10, pady=10, fill='x', expand=True)

    def quick_add_transaction(self, transaction_type):
        """Quick add transaction"""
        dialog = self.interaction_manager.show_add_transaction_dialog(self.root)
        # Refresh current view
        self.root.after(100, self.refresh_current_view)

    def show_transactions(self):
        """Show transaction record management"""
        self.clear_main_content()
        self.current_view = "transactions"

        # Create transaction management frame
        trans_frame = tk.Frame(self.main_content_frame, bg='white')
        trans_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title and buttons
        header_frame = tk.Frame(trans_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="Transaction Record Management",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(side='left')

        # Action buttons
        btn_frame = tk.Frame(header_frame, bg='white')
        btn_frame.pack(side='right')

        add_btn = tk.Button(
            btn_frame,
            text="Add Transaction",
            command=lambda: self.interaction_manager.show_add_transaction_dialog(self.root),
            bg='#2E8B57',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        add_btn.pack(side='left', padx=5)

        refresh_btn = tk.Button(
            btn_frame,
            text="Refresh",
            command=self.show_transactions,
            bg='#4169E1',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        refresh_btn.pack(side='left', padx=5)

        # Transaction record table
        tree_frame = tk.Frame(trans_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)

        # Create Treeview
        columns = ('Date', 'Type', 'Category', 'Amount', 'Description')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Set column headers
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Load transaction data
        transactions = self.data_manager.get_transactions()
        transactions.sort(key=lambda x: x['date'], reverse=True)  # Sort by date descending

        for trans in transactions[-50:]:  # Show last 50 records
            tree.insert('', 'end', values=(
                trans['date'],
                'Income' if trans['type'] == 'income' else 'Expense',
                trans['category'],
                f"${trans['amount']:.2f}",
                trans['description']
            ))

    def show_analytics(self):
        """Show data analysis"""
        self.clear_main_content()
        self.current_view = "analytics"

        # Create analysis frame
        analytics_frame = tk.Frame(self.main_content_frame, bg='white')
        analytics_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            analytics_frame,
            text="Data Analysis",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(pady=(0, 20))

        # Create chart tabs
        notebook = ttk.Notebook(analytics_frame)
        notebook.pack(fill='both', expand=True)

        # Category expense pie chart
        pie_frame = tk.Frame(notebook, bg='white')
        notebook.add(pie_frame, text='Expense Category Analysis')

        pie_canvas = self.visualization_manager.create_category_pie_chart(pie_frame)
        pie_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # Monthly trend chart
        trend_frame = tk.Frame(notebook, bg='white')
        notebook.add(trend_frame, text='Monthly Income-Expense Trends')

        trend_canvas = self.visualization_manager.create_monthly_trend_chart(trend_frame)
        trend_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # Balance change chart
        balance_frame = tk.Frame(notebook, bg='white')
        notebook.add(balance_frame, text='Balance Change Trends')

        balance_canvas = self.visualization_manager.create_balance_line_chart(balance_frame)
        balance_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def show_reports(self):
        """Show monthly reports"""
        self.clear_main_content()
        self.current_view = "reports"

        # Create report frame
        report_frame = tk.Frame(self.main_content_frame, bg='white')
        report_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title and buttons
        header_frame = tk.Frame(report_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="Monthly Financial Report",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(side='left')

        # Export button
        export_btn = tk.Button(
            header_frame,
            text="Export Report",
            command=self.export_report,
            bg='#FF8C00',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        export_btn.pack(side='right')

        # Generate report
        report_data = self.advanced_features.generate_monthly_report()

        # Report content
        report_text = tk.Text(report_frame, wrap='word', bg='#f8f9fa', font=('Arial', 11))
        report_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Format and display report
        formatted_report = self.advanced_features.format_report_text(report_data)
        report_text.insert('end', formatted_report)
        report_text.config(state='disabled')

        # Add scrollbar
        scrollbar_report = ttk.Scrollbar(report_frame, orient='vertical', command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar_report.set)
        scrollbar_report.pack(side='right', fill='y')

    def show_system_test(self):
        """Show system test"""
        self.clear_main_content()
        self.current_view = "test"

        # Create test frame
        test_frame = tk.Frame(self.main_content_frame, bg='white')
        test_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title and buttons
        header_frame = tk.Frame(test_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="System Function Test",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(side='left')

        # Run test button
        test_btn = tk.Button(
            header_frame,
            text="Run Tests",
            command=self.run_system_tests,
            bg='#2E8B57',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        test_btn.pack(side='right')

        # Test result display area
        self.test_result_text = tk.Text(test_frame, wrap='word', bg='#f8f9fa', font=('Courier', 10))
        self.test_result_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Initial display
        self.test_result_text.insert('end', "Click 'Run Tests' button to start system function testing...\n\n")
        self.test_result_text.insert('end', "Tests will verify the following functions:\n")
        self.test_result_text.insert('end', "• Data addition and saving\n")
        self.test_result_text.insert('end', "• Financial calculation accuracy\n")
        self.test_result_text.insert('end', "• Error handling mechanisms\n")

    def run_system_tests(self):
        """Run system tests"""
        self.test_result_text.delete(1.0, 'end')
        self.test_result_text.insert('end', "Running system tests...\n\n")
        self.test_result_text.update()

        # Run tests
        test_results = self.test_manager.run_all_tests()

        # Display test results
        self.test_result_text.insert('end', f"Testing completed!\n")
        self.test_result_text.insert('end', f"Total tests: {test_results['total_tests']}\n")
        self.test_result_text.insert('end', f"Passed: {test_results['passed']}\n")
        self.test_result_text.insert('end', f"Failed: {test_results['failed']}\n\n")

        self.test_result_text.insert('end', "Detailed test results:\n")
        self.test_result_text.insert('end', "=" * 50 + "\n")

        for result in test_results['results']:
            status_symbol = "✅" if result['status'] == 'PASS' else "❌"
            self.test_result_text.insert('end', f"{status_symbol} {result['test_name']}: {result['message']}\n")

        self.test_result_text.insert('end', "\n" + "=" * 50 + "\n")

        if test_results['failed'] == 0:
            self.test_result_text.insert('end', "All tests passed! System is running normally.\n")
        else:
            self.test_result_text.insert('end', f"{test_results['failed']} tests failed, please check system.\n")

    def show_data_management(self):
        """Show data management"""
        self.clear_main_content()
        self.current_view = "data_management"

        # Create data management frame
        data_frame = tk.Frame(self.main_content_frame, bg='white')
        data_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            data_frame,
            text="Data Management",
            font=('Arial', 18, 'bold'),
            bg='white'
        )
        title_label.pack(pady=(0, 30))

        # Data statistics
        stats_frame = tk.LabelFrame(data_frame, text="Data Statistics", font=('Arial', 12, 'bold'), bg='white')
        stats_frame.pack(fill='x', padx=20, pady=10)

        transactions = self.data_manager.get_transactions()
        stats_text = f"""
Total transaction records: {len(transactions)}
Data file size: {os.path.getsize(self.data_manager.data_file) if os.path.exists(self.data_manager.data_file) else 0} bytes
Last update time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        stats_label = tk.Label(stats_frame, text=stats_text, bg='white', font=('Arial', 11), justify='left')
        stats_label.pack(padx=20, pady=15)

        # Data operations
        operations_frame = tk.LabelFrame(data_frame, text="Data Operations", font=('Arial', 12, 'bold'), bg='white')
        operations_frame.pack(fill='x', padx=20, pady=10)

        # Button container
        btn_container = tk.Frame(operations_frame, bg='white')
        btn_container.pack(pady=20)

        # Import/Export buttons
        import_btn = tk.Button(
            btn_container,
            text="Import CSV",
            command=lambda: self.interaction_manager.show_import_dialog(self.root),
            bg='#2E8B57',
            fg='white',
            font=('Arial', 12),
            padx=20,
            pady=10,
            width=15
        )
        import_btn.pack(side='left', padx=10)

        export_btn = tk.Button(
            btn_container,
            text="Export CSV",
            command=lambda: self.interaction_manager.show_export_dialog(self.root),
            bg='#4169E1',
            fg='white',
            font=('Arial', 12),
            padx=20,
            pady=10,
            width=15
        )
        export_btn.pack(side='left', padx=10)

        backup_btn = tk.Button(
            btn_container,
            text="Backup Data",
            command=self.backup_data,
            bg='#FF8C00',
            fg='white',
            font=('Arial', 12),
            padx=20,
            pady=10,
            width=15
        )
        backup_btn.pack(side='left', padx=10)

        # CSV format instructions
        format_frame = tk.LabelFrame(data_frame, text="CSV Format Instructions", font=('Arial', 12, 'bold'),
                                     bg='white')
        format_frame.pack(fill='x', padx=20, pady=10)

        format_text = """
CSV file should contain the following columns (in order):
• date: Date (format: YYYY-MM-DD)
• type: Type (income or expense)
• category: Category (e.g., Food, Transport, Salary, etc.)
• amount: Amount (number, greater than 0)
• description: Description (text explanation)

Example:
2024-01-01,income,Salary,5000.00,Monthly salary
2024-01-02,expense,Food,50.00,Lunch
        """

        format_label = tk.Label(format_frame, text=format_text, bg='white', font=('Courier', 10), justify='left')
        format_label.pack(padx=20, pady=15)

    def backup_data(self):
        """Backup data"""
        try:
            backup_filename = f"finance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = filedialog.asksaveasfilename(
                title="Save Backup File",
                defaultextension=".json",
                initialfile=backup_filename,
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )

            if backup_path:
                import shutil
                shutil.copy2(self.data_manager.data_file, backup_path)
                messagebox.showinfo("Success", "Data backup successful!")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def export_report(self):
        """Export monthly report"""
        try:
            report_data = self.advanced_features.generate_monthly_report()
            filename = f"Monthly_Report_{datetime.now().strftime('%Y%m')}.txt"

            file_path = filedialog.asksaveasfilename(
                title="Save Report",
                defaultextension=".txt",
                initialfile=filename,
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )

            if file_path:
                if self.advanced_features.export_monthly_report(report_data, file_path):
                    messagebox.showinfo("Success", "Report exported successfully!")
                else:
                    messagebox.showerror("Error", "Report export failed")
        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")

    def refresh_current_view(self):
        """Refresh current view"""
        if self.current_view == "dashboard":
            self.show_dashboard()
        elif self.current_view == "transactions":
            self.show_transactions()
        elif self.current_view == "analytics":
            self.show_analytics()
        elif self.current_view == "reports":
            self.show_reports()

    def run(self):
        """Run application"""
        self.root.mainloop()


# ================================
# Program Entry Point
# ================================
if __name__ == "__main__":
    # Create and run application
    import pathlib, re

    bad = re.compile(r'[\U00010000-\U0010FFFF]')

    for p in pathlib.Path(".").rglob("*.py"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if bad.search(line):
                print(f"{p}:{i}: {bad.findall(line)} :: {line}")

    try:
        app = FinanceManagerApp()
        app.run()
    except Exception as e:
        print(f"Application startup failed: {e}")
        input("Press Enter to exit...")