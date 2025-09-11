from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from finance_calculator import FinanceCalculator
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class VisualizationManager:
    """Data visualization management class"""

    def __init__(self, calculator: FinanceCalculator):
        self.calculator = calculator
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def create_category_pie_chart(self, frame) -> FigureCanvasTkAgg:
        """Create category expense pie chart"""
        category_data = self.calculator.analyze_spending_by_category(6)

        fig, ax = plt.subplots(figsize=(8, 6))

        if category_data:
            categories = list(category_data.keys())
            amounts = list(category_data.values())

            colors = plt.cm.Set3(range(len(categories)))
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors)
            ax.set_title('Expense Category Analysis (Last 6 Months)', fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', fontsize=16)
            ax.set_title('Expense Category Analysis', fontsize=14)

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

            x = range(len(months))
            width = 0.35

            ax.bar([i - width / 2 for i in x], incomes, width, label='Income', color='#2E8B57')
            ax.bar([i + width / 2 for i in x], expenses, width, label='Expense', color='#CD5C5C')

            ax.set_xlabel('Month')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Monthly Income-Expense Trends', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([m.split('-')[1] for m in months])
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', fontsize=16)
            ax.set_title('Monthly Income-Expense Trends', fontsize=14)

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

            ax.plot(months, balances, marker='o', linewidth=2, markersize=6, color='#4169E1')
            ax.fill_between(months, balances, alpha=0.3, color='#4169E1')
            ax.set_xlabel('Month')
            ax.set_ylabel('Cumulative Balance ($)')
            ax.set_title('Cumulative Balance Change Trends', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Rotate x-axis labels
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', fontsize=16)
            ax.set_title('Cumulative Balance Change Trends', fontsize=14)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas