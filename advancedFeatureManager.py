from datetime import datetime
from typing import Dict
from data_manager import DataManager
from finance_calculator import FinanceCalculator


class AdvancedFeaturesManager:
    """Advanced features management class"""

    def __init__(self, data_manager: DataManager, calculator: FinanceCalculator):
        self.data_manager = data_manager
        self.calculator = calculator

    def setup_budget_alerts(self):
        """Setup budget alerts"""
        budgets = self.data_manager.data.get('budgets', {})
        current_month = datetime.now().strftime('%Y-%m')

        alerts = []
        for category, budget_amount in budgets.items():
            # Calculate current month spending for this category
            month_start = datetime.now().replace(day=1)
            month_spending = self.get_category_spending(category, month_start)

            if month_spending > budget_amount * 0.8:  # Alert when over 80% of budget
                usage_percent = (month_spending / budget_amount) * 100
                alerts.append({
                    'category': category,
                    'budget': budget_amount,
                    'spent': month_spending,
                    'percentage': usage_percent
                })

        return alerts

    def get_category_spending(self, category: str, start_date: datetime) -> float:
        """Get spending for specified category"""
        end_date = datetime.now()
        transactions = self.data_manager.get_transactions(start_date, end_date)

        return sum(t['amount'] for t in transactions
                   if t['type'] == 'expense' and t['category'] == category)

    def generate_monthly_report(self) -> Dict:
        """Generate monthly report"""
        current_month_start = datetime.now().replace(day=1)
        current_month_end = datetime.now()

        monthly_summary = self.calculator.calculate_balance(current_month_start, current_month_end)
        category_analysis = self.calculator.analyze_spending_by_category(1)
        suggestions = self.calculator.generate_smart_suggestions()
        budget_alerts = self.setup_budget_alerts()

        return {
            'summary': monthly_summary,
            'category_analysis': category_analysis,
            'suggestions': suggestions,
            'budget_alerts': budget_alerts,
            'report_date': datetime.now().strftime('%Y-%m-%d')
        }

    def export_monthly_report(self, report_data: Dict, file_path: str) -> bool:
        """Export monthly report"""
        try:
            report_text = self.format_report_text(report_data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            return True
        except Exception as e:
            print(f"Report export error: {e}")
            return False

    def format_report_text(self, report_data: Dict) -> str:
        """Format report text"""
        report = f"""
Personal Finance Monthly Report
Generated Date: {report_data['report_date']}
{'=' * 50}

Monthly Financial Summary
Total Income: ${report_data['summary']['total_income']:.2f}
Total Expense: ${report_data['summary']['total_expense']:.2f}
Net Income: ${report_data['summary']['balance']:.2f}
Transaction Count: {report_data['summary']['transaction_count']}

Expense Category Analysis
"""

        for category, amount in report_data['category_analysis'].items():
            report += f"{category}: ${amount:.2f}\n"

        report += "\nSmart Suggestions\n"
        for i, suggestion in enumerate(report_data['suggestions'], 1):
            report += f"{i}. {suggestion}\n"

        if report_data['budget_alerts']:
            report += "\n⚠️ Budget Alerts\n"
            for alert in report_data['budget_alerts']:
                report += f"{alert['category']}: Used {alert['percentage']:.1f}% (${alert['spent']:.2f}/${alert['budget']:.2f})\n"

        return report
