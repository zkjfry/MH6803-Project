# advanced_features_manager.py
# Member 7: Advanced Features & Integration (10%)
# Implement advanced features, module integration, budget reminder system

from datetime import datetime, timedelta
from typing import Dict, List
import json


class AdvancedFeaturesManager:
    """Advanced features management class"""

    def __init__(self, data_manager, calculator):
        self.data_manager = data_manager
        self.calculator = calculator
        self.notification_settings = {
            'budget_alerts': True,
            'spending_alerts': True,
            'goal_reminders': True,
            'weekly_reports': False
        }

    def setup_budget_alerts(self) -> List[Dict]:
        """Setup and check budget alerts"""
        budgets = self.data_manager.data.get('budgets', {})
        current_month = datetime.now().strftime('%Y-%m')

        alerts = []

        for category, budget_amount in budgets.items():
            # Calculate current month spending for this category
            month_start = datetime.now().replace(day=1)
            month_spending = self.get_category_spending(category, month_start)

            usage_percent = (month_spending / budget_amount) * 100 if budget_amount > 0 else 0

            # Generate alerts based on usage
            alert_level = 'info'
            if usage_percent >= 100:
                alert_level = 'critical'
            elif usage_percent >= 80:
                alert_level = 'warning'
            elif usage_percent >= 60:
                alert_level = 'info'

            if usage_percent >= 60:  # Only alert if significant usage
                alerts.append({
                    'category': category,
                    'budget': budget_amount,
                    'spent': month_spending,
                    'remaining': max(0, budget_amount - month_spending),
                    'percentage': usage_percent,
                    'level': alert_level,
                    'message': self.generate_budget_message(category, usage_percent, budget_amount, month_spending)
                })

        return alerts

    def generate_budget_message(self, category: str, usage_percent: float, budget: float, spent: float) -> str:
        """Generate contextual budget alert message"""
        remaining_days = (datetime.now().replace(month=datetime.now().month + 1, day=1) - timedelta(
            days=1)).day - datetime.now().day + 1

        if usage_percent >= 100:
            over_amount = spent - budget
            return f"Budget exceeded for {category} by ${over_amount:.2f}. Consider reducing spending."
        elif usage_percent >= 80:
            daily_remaining = (budget - spent) / max(1, remaining_days)
            return f"{category} budget 80% used. ${daily_remaining:.2f}/day remaining for {remaining_days} days."
        else:
            return f"{category} spending on track: {usage_percent:.1f}% of budget used."

    def get_category_spending(self, category: str, start_date: datetime) -> float:
        """Get spending for specified category"""
        end_date = datetime.now()
        transactions = self.data_manager.get_transactions(start_date, end_date)

        return sum(t['amount'] for t in transactions
                   if t['type'] == 'expense' and t['category'] == category)

    def create_budget_plan(self, total_budget: float, priorities: Dict[str, int]) -> Dict[str, float]:
        """Create automatic budget allocation based on priorities"""
        total_priority = sum(priorities.values())
        budget_plan = {}

        for category, priority in priorities.items():
            allocation_percentage = priority / total_priority
            allocated_amount = total_budget * allocation_percentage
            budget_plan[category] = allocated_amount

        return budget_plan

    def setup_financial_goals(self, goals: List[Dict]) -> Dict:
        """Setup and track financial goals"""
        goal_status = {
            'active_goals': [],
            'achieved_goals': [],
            'overdue_goals': []
        }

        current_balance = self.calculator.calculate_balance()['balance']

        for goal in goals:
            goal_progress = self.calculate_goal_progress(goal, current_balance)

            if goal_progress['achieved']:
                goal_status['achieved_goals'].append(goal_progress)
            elif goal_progress['overdue']:
                goal_status['overdue_goals'].append(goal_progress)
            else:
                goal_status['active_goals'].append(goal_progress)

        return goal_status

    def calculate_goal_progress(self, goal: Dict, current_balance: float) -> Dict:
        """Calculate progress towards a financial goal"""
        target_amount = goal.get('target_amount', 0)
        target_date = datetime.strptime(goal.get('target_date', '2030-01-01'), '%Y-%m-%d')
        start_date = datetime.strptime(goal.get('start_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')

        # Calculate progress
        progress_percentage = (current_balance / target_amount) * 100 if target_amount > 0 else 0
        days_total = (target_date - start_date).days
        days_remaining = (target_date - datetime.now()).days
        days_elapsed = days_total - days_remaining

        # Calculate required savings rate
        remaining_amount = max(0, target_amount - current_balance)
        monthly_requirement = remaining_amount / max(1, days_remaining / 30) if days_remaining > 0 else 0

        return {
            'goal': goal,
            'current_amount': current_balance,
            'progress_percentage': min(100, progress_percentage),
            'remaining_amount': remaining_amount,
            'days_remaining': days_remaining,
            'monthly_requirement': monthly_requirement,
            'achieved': current_balance >= target_amount,
            'overdue': days_remaining < 0 and current_balance < target_amount,
            'on_track': self.is_goal_on_track(goal, current_balance, days_elapsed, days_total)
        }

    def is_goal_on_track(self, goal: Dict, current_balance: float, days_elapsed: int, days_total: int) -> bool:
        """Determine if goal progress is on track"""
        if days_total <= 0:
            return True

        expected_progress = (days_elapsed / days_total)
        actual_progress = current_balance / goal.get('target_amount', 1)

        return actual_progress >= expected_progress * 0.8  # Allow 20% tolerance

    def generate_spending_insights(self) -> Dict:
        """Generate advanced spending insights"""
        insights = {
            'spending_patterns': {},
            'seasonal_trends': {},
            'efficiency_scores': {},
            'recommendations': []
        }

        # Analyze spending patterns
        transactions = self.data_manager.get_transactions()
        if not transactions:
            return insights

        # Weekly spending pattern
        weekly_spending = {}
        for transaction in transactions:
            if transaction['type'] == 'expense':
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                day_of_week = date.strftime('%A')

                if day_of_week not in weekly_spending:
                    weekly_spending[day_of_week] = []
                weekly_spending[day_of_week].append(transaction['amount'])

        # Calculate average spending by day
        for day, amounts in weekly_spending.items():
            insights['spending_patterns'][day] = {
                'average': sum(amounts) / len(amounts),
                'total_transactions': len(amounts),
                'max_spending': max(amounts),
                'min_spending': min(amounts)
            }

        # Generate recommendations based on patterns
        if weekly_spending:
            highest_day = max(insights['spending_patterns'].items(),
                              key=lambda x: x[1]['average'])[0]
            insights['recommendations'].append(
                f"Highest spending occurs on {highest_day}. Consider meal planning or setting daily limits."
            )

        return insights

    def generate_monthly_report(self) -> Dict:
        """Generate comprehensive monthly financial report"""
        current_month_start = datetime.now().replace(day=1)
        current_month_end = datetime.now()

        # Get data for report
        monthly_summary = self.calculator.calculate_balance(current_month_start, current_month_end)
        category_analysis = self.calculator.analyze_spending_by_category(1)
        suggestions = self.calculator.generate_smart_suggestions()
        budget_alerts = self.setup_budget_alerts()
        spending_insights = self.generate_spending_insights()

        # Calculate additional metrics
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        previous_summary = self.calculator.calculate_balance(previous_month_start, previous_month_end)

        # Month-over-month comparison
        income_change = monthly_summary['total_income'] - previous_summary['total_income']
        expense_change = monthly_summary['total_expense'] - previous_summary['total_expense']

        return {
            'report_period': {
                'start_date': current_month_start.strftime('%Y-%m-%d'),
                'end_date': current_month_end.strftime('%Y-%m-%d')
            },
            'summary': monthly_summary,
            'previous_month_comparison': {
                'income_change': income_change,
                'expense_change': expense_change,
                'income_change_percent': (income_change / previous_summary['total_income'] * 100) if previous_summary[
                                                                                                         'total_income'] > 0 else 0,
                'expense_change_percent': (expense_change / previous_summary['total_expense'] * 100) if
                previous_summary['total_expense'] > 0 else 0
            },
            'category_analysis': category_analysis,
            'spending_insights': spending_insights,
            'suggestions': suggestions,
            'budget_alerts': budget_alerts,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def export_monthly_report(self, report_data: Dict, file_path: str) -> bool:
        """Export monthly report to file"""
        try:
            report_text = self.format_report_text(report_data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            return True
        except Exception as e:
            print(f"Report export error: {e}")
            return False

    def format_report_text(self, report_data: Dict) -> str:
        """Format comprehensive report text"""
        report = f"""
PERSONAL FINANCE MONTHLY REPORT
Generated: {report_data['report_date']}
Period: {report_data['report_period']['start_date']} to {report_data['report_period']['end_date']}
{'=' * 60}

💰 EXECUTIVE SUMMARY
Total Income: ${report_data['summary']['total_income']:.2f}
Total Expense: ${report_data['summary']['total_expense']:.2f}
Net Income: ${report_data['summary']['balance']:.2f}
Transactions: {report_data['summary']['transaction_count']}

📊 MONTH-OVER-MONTH COMPARISON
Income Change: {'+' if report_data['previous_month_comparison']['income_change'] >= 0 else ''}${report_data['previous_month_comparison']['income_change']:.2f} ({report_data['previous_month_comparison']['income_change_percent']:.1f}%)
Expense Change: {'+' if report_data['previous_month_comparison']['expense_change'] >= 0 else ''}${report_data['previous_month_comparison']['expense_change']:.2f} ({report_data['previous_month_comparison']['expense_change_percent']:.1f}%)

📈 EXPENSE BREAKDOWN BY CATEGORY
"""

        # Add category breakdown
        for category, amount in sorted(report_data['category_analysis'].items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / report_data['summary']['total_expense'] * 100) if report_data['summary'][
                                                                                         'total_expense'] > 0 else 0
            report += f"{category:<15}: ${amount:>8.2f} ({percentage:5.1f}%)\n"

        # Add spending insights
        if report_data['spending_insights']['spending_patterns']:
            report += f"\n🔍 SPENDING PATTERNS\n"
            for day, pattern in report_data['spending_insights']['spending_patterns'].items():
                report += f"{day:<10}: Avg ${pattern['average']:.2f} ({pattern['total_transactions']} transactions)\n"

        # Add suggestions
        report += f"\n💡 SMART RECOMMENDATIONS\n"
        for i, suggestion in enumerate(report_data['suggestions'], 1):
            report += f"{i}. {suggestion}\n"

        # Add budget alerts
        if report_data['budget_alerts']:
            report += f"\n⚠️ BUDGET ALERTS\n"
            for alert in report_data['budget_alerts']:
                status_icon = "🔴" if alert['level'] == 'critical' else "🟡" if alert['level'] == 'warning' else "🟢"
                report += f"{status_icon} {alert['message']}\n"

        report += f"\n{'=' * 60}\nEnd of Report\n"

        return report

    def schedule_automatic_backups(self) -> bool:
        """Setup automatic data backups"""
        try:
            backup_settings = {
                'enabled': True,
                'frequency': 'weekly',
                'retention_days': 30,
                'last_backup': datetime.now().isoformat()
            }

            # Save backup settings
            self.data_manager.data['backup_settings'] = backup_settings
            return self.data_manager.save_data()
        except Exception as e:
            print(f"Backup setup error: {e}")
            return False

    def integration_health_check(self) -> Dict:
        """Check integration health between all modules"""
        health_status = {
            'overall_status': 'healthy',
            'module_status': {},
            'warnings': [],
            'errors': []
        }

        # Check data manager
        try:
            self.data_manager.get_data_statistics()
            health_status['module_status']['data_manager'] = 'healthy'
        except Exception as e:
            health_status['module_status']['data_manager'] = 'error'
            health_status['errors'].append(f"Data Manager: {str(e)}")

        # Check calculator
        try:
            self.calculator.calculate_balance()
            health_status['module_status']['calculator'] = 'healthy'
        except Exception as e:
            health_status['module_status']['calculator'] = 'error'
            health_status['errors'].append(f"Calculator: {str(e)}")

        # Overall status
        if health_status['errors']:
            health_status['overall_status'] = 'error'
        elif health_status['warnings']:
            health_status['overall_status'] = 'warning'

        return health_status


if __name__ == "__main__":
    # Test Advanced Features Manager
    class MockDataManager:
        def __init__(self):
            self.data = {
                'transactions': [
                    {'date': '2024-01-01', 'type': 'income', 'category': 'Salary', 'amount': 3000},
                    {'date': '2024-01-15', 'type': 'expense', 'category': 'Food', 'amount': 200}
                ],
                'budgets': {'Food': 300, 'Transport': 150}
            }

        def get_transactions(self, start_date=None, end_date=None):
            return self.data['transactions']

        def save_data(self):
            return True

        def get_data_statistics(self):
            return {'total_transactions': len(self.data['transactions'])}


    class MockCalculator:
        def __init__(self, data_manager):
            self.data_manager = data_manager

        def calculate_balance(self, start_date=None, end_date=None):
            return {'total_income': 3000, 'total_expense': 200, 'balance': 2800, 'transaction_count': 2}

        def analyze_spending_by_category(self, months):
            return {'Food': 200}

        def generate_smart_suggestions(self):
            return ['Your savings rate is excellent!']


    # Test the manager
    dm = MockDataManager()
    calc = MockCalculator(dm)
    advanced_manager = AdvancedFeaturesManager(dm, calc)

    # Test budget alerts
    alerts = advanced_manager.setup_budget_alerts()
    print(f"Budget alerts: {len(alerts)}")

    # Test monthly report
    report = advanced_manager.generate_monthly_report()
    print(f"Monthly report generated for period: {report['report_period']}")

    # Test health check
    health = advanced_manager.integration_health_check()
    print(f"System health: {health['overall_status']}")