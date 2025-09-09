# visualization_manager.py
# Member 4: Visualization Module (15%)
# Create chart components, data visualization, report generation functions

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

class VisualizationManager:
    """Data visualization management class"""
    
    def __init__(self, calculator):
        self.calculator = calculator
        # Configure matplotlib for better font support
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        plt.style.use('default')
    
    def create_category_pie_chart(self, frame) -> FigureCanvasTkAgg:
        """Create category expense pie chart"""
        category_data = self.calculator.analyze_spending_by_category(6)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if category_data:
            categories = list(category_data.keys())
            amounts = list(category_data.values())
            
            # Create color palette
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            
            # Create pie chart with improved styling
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%', 
                colors=colors,
                startangle=90,
                explode=[0.05] * len(categories)  # Slight separation
            )
            
            # Improve text styling
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Expense Category Analysis (Last 6 Months)', 
                        fontsize=14, fontweight='bold', pad=20)
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title('Expense Category Analysis', fontsize=14)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas
    
    def create_monthly_trend_chart(self, frame) -> FigureCanvasTkAgg:
        """Create monthly trend chart"""
        monthly_data = self.calculator.calculate_monthly_trend(12)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if monthly_data:
            months = sorted(monthly_data.keys())
            incomes = [monthly_data[month]['income'] for month in months]
            expenses = [monthly_data[month]['expense'] for month in months]
            
            x = np.arange(len(months))
            width = 0.35
            
            # Create bars with improved styling
            bars1 = ax.bar(x - width/2, incomes, width, label='Income', 
                          color='#2E8B57', alpha=0.8)
            bars2 = ax.bar(x + width/2, expenses, width, label='Expense', 
                          color='#CD5C5C', alpha=0.8)
            
            # Add value labels on bars
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'${height:.0f}', ha='center', va='bottom', fontsize=8)
            
            add_value_labels(bars1)
            add_value_labels(bars2)
            
            ax.set_xlabel('Month', fontweight='bold')
            ax.set_ylabel('Amount ($)', fontweight='bold')
            ax.set_title('Monthly Income-Expense Trends', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([m.split('-')[1] + '/' + m.split('-')[0][-2:] for m in months])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add net income line
            net_income = [incomes[i] - expenses[i] for i in range(len(incomes))]
            ax2 = ax.twinx()
            ax2.plot(x, net_income, color='#4169E1', marker='o', linewidth=2, 
                    label='Net Income', markersize=4)
            ax2.set_ylabel('Net Income ($)', color='#4169E1', fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='#4169E1')
            
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title('Monthly Income-Expense Trends', fontsize=14)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas
    
    def create_balance_line_chart(self, frame) -> FigureCanvasTkAgg:
        """Create balance change line chart"""
        monthly_data = self.calculator.calculate_monthly_trend(12)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if monthly_data:
            months = sorted(monthly_data.keys())
            balances = []
            cumulative_balance = 0
            
            for month in months:
                monthly_balance = monthly_data[month]['income'] - monthly_data[month]['expense']
                cumulative_balance += monthly_balance
                balances.append(cumulative_balance)
            
            # Create line chart with area fill
            ax.plot(months, balances, marker='o', linewidth=3, markersize=6, 
                   color='#4169E1', markerfacecolor='white', markeredgewidth=2)
            ax.fill_between(months, balances, alpha=0.3, color='#4169E1')
            
            # Add horizontal line at zero
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            
            # Add value annotations for key points
            for i, (month, balance) in enumerate(zip(months, balances)):
                if i == 0 or i == len(balances) - 1 or balance == max(balances) or balance == min(balances):
                    ax.annotate(f'${balance:.0f}', 
                               (month, balance), 
                               textcoords="offset points", 
                               xytext=(0,10), 
                               ha='center',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            ax.set_xlabel('Month', fontweight='bold')
            ax.set_ylabel('Cumulative Balance ($)', fontweight='bold')
            ax.set_title('Cumulative Balance Change Trends', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Color the area differently for positive and negative balances
            ax.fill_between(months, 0, balances, where=[b >= 0 for b in balances], 
                           color='green', alpha=0.3, interpolate=True, label='Positive')
            ax.fill_between(months, 0, balances, where=[b < 0 for b in balances], 
                           color='red', alpha=0.3, interpolate=True, label='Negative')
            
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title('Cumulative Balance Change Trends', fontsize=14)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas
    
    def create_spending_heatmap(self, frame) -> FigureCanvasTkAgg:
        """Create spending intensity heatmap by day of week and hour"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get transaction data
        transactions = self.calculator.data_manager.get_transactions()
        expense_transactions = [t for t in transactions if t['type'] == 'expense']
        
        if not expense_transactions:
            ax.text(0.5, 0.5, 'No Expense Data Available', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title('Spending Pattern Heatmap', fontsize=14)
            plt.tight_layout()
            return FigureCanvasTkAgg(fig, frame)
        
        # Create spending matrix (7 days x 24 hours)
        spending_matrix = np.zeros((7, 24))
        
        for transaction in expense_transactions:
            try:
                # Parse date and get day of week
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
                
                # For demo, assume random hour distribution
                hour = hash(transaction.get('id', transaction['description'])) % 24
                spending_matrix[day_of_week][hour] += transaction['amount']
            except:
                continue
        
        # Create heatmap
        im = ax.imshow(spending_matrix, cmap='YlOrRd', aspect='auto')
        
        # Set labels
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [f'{h:02d}:00' for h in range(24)]
        
        ax.set_xticks(np.arange(len(hours))[::4])  # Show every 4th hour
        ax.set_xticklabels([hours[i] for i in range(0, 24, 4)])
        ax.set_yticks(np.arange(len(days)))
        ax.set_yticklabels(days)
        
        ax.set_xlabel('Hour of Day', fontweight='bold')
        ax.set_ylabel('Day of Week', fontweight='bold')
        ax.set_title('Spending Pattern Heatmap', fontsize=14, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Spending Amount ($)', rotation=270, labelpad=15)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas
    
    def create_budget_comparison_chart(self, frame, budget_data) -> FigureCanvasTkAgg:
        """Create budget vs actual spending comparison chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not budget_data:
            ax.text(0.5, 0.5, 'No Budget Data Available', ha='center', va='center', 
                   fontsize=16, transform=ax.transAxes)
            ax.set_title('Budget vs Actual Spending', fontsize=14)
            plt.tight_layout()
            return FigureCanvasTkAgg(fig, frame)
        
        categories = list(budget_data.keys())
        budgets = [budget_data[cat]['budget'] for cat in categories]
        actuals = [budget_data[cat]['spent'] for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar(x - width/2, budgets, width, label='Budget', 
                      color='lightblue', alpha=0.8)
        bars2 = ax.bar(x + width/2, actuals, width, label='Actual', 
                      color='orange', alpha=0.8)
        
        # Color over-budget categories differently
        for i, (budget, actual) in enumerate(zip(budgets, actuals)):
            if actual > budget:
                bars2[i].set_color('red')
        
        # Add percentage labels
        for i, (budget, actual) in enumerate(zip(budgets, actuals)):
            if budget > 0:
                percentage = (actual / budget) * 100
                ax.text(x[i], max(budget, actual) + max(budgets) * 0.02,
                       f'{percentage:.0f}%', ha='center', va='bottom',
                       fontweight='bold' if percentage > 100 else 'normal',
                       color='red' if percentage > 100 else 'black')
        
        ax.set_xlabel('Category', fontweight='bold')
        ax.set_ylabel('Amount ($)', fontweight='bold')
        ax.set_title('Budget vs Actual Spending Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas
    
    def export_chart_as_image(self, canvas, filename):
        """Export chart as image file"""
        try:
            canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

if __name__ == "__main__":
    # Test Visualization Manager
    import tkinter as tk
    
    class MockCalculator:
        def analyze_spending_by_category(self, months):
            return {'Food': 500, 'Transport': 200, 'Entertainment': 150}
        
        def calculate_monthly_trend(self, months):
            return {
                '2024-01': {'income': 3000, 'expense': 2000},
                '2024-02': {'income': 3200, 'expense': 2200},
                '2024-03': {'income': 2800, 'expense': 1800}
            }
    
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)
    
    viz_manager = VisualizationManager(MockCalculator())
    canvas = viz_manager.create_category_pie_chart(frame)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    
    root.mainloop()