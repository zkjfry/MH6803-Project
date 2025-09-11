from typing import Dict, List
from datetime import datetime, timedelta
from data_manager import DataManager
import statistics


class FinanceCalculator:
    """Finance calculation core algorithm class"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def calculate_balance(self, start_date=None, end_date=None) -> Dict:
        """Calculate income-expense balance"""
        transactions = self.data_manager.get_transactions(start_date, end_date)

        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        balance = total_income - total_expense

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transaction_count': len(transactions)
        }

    def analyze_spending_by_category(self, months=12) -> Dict:
        """Analyze spending by category"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        transactions = self.data_manager.get_transactions(start_date, end_date)
        expense_transactions = [t for t in transactions if t['type'] == 'expense']

        category_spending = {}
        for t in expense_transactions:
            category = t['category']
            if category not in category_spending:
                category_spending[category] = 0
            category_spending[category] += t['amount']

        return category_spending

    def calculate_monthly_trend(self, months=12) -> Dict:
        """Calculate monthly trends"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        transactions = self.data_manager.get_transactions(start_date, end_date)

        monthly_data = {}
        for t in transactions:
            t_date = datetime.strptime(t['date'], '%Y-%m-%d')
            month_key = t_date.strftime('%Y-%m')

            if month_key not in monthly_data:
                monthly_data[month_key] = {'income': 0, 'expense': 0}

            monthly_data[month_key][t['type']] += t['amount']

        return monthly_data

    def detect_anomalies(self, threshold_multiplier=2.0) -> List[Dict]:
        """Detect anomalous expenses"""
        transactions = self.data_manager.get_transactions()
        expense_transactions = [t for t in transactions if t['type'] == 'expense']

        if len(expense_transactions) < 10:
            return []

        amounts = [t['amount'] for t in expense_transactions]
        mean_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts)
        threshold = mean_amount + (threshold_multiplier * std_amount)

        anomalies = []
        for t in expense_transactions:
            if t['amount'] > threshold:
                anomalies.append({
                    'transaction': t,
                    'deviation': t['amount'] - mean_amount,
                    'threshold': threshold
                })

        return anomalies

    def generate_smart_suggestions(self) -> List[str]:
        """Generate smart financial advice"""
        suggestions = []

        # Analyze recent 3 months data
        monthly_data = self.calculate_monthly_trend(3)
        category_spending = self.analyze_spending_by_category(3)

        if not monthly_data:
            return ["Recommend starting to record your financial data for personalized advice."]

        # Calculate average monthly expenses
        total_expenses = sum(data['expense'] for data in monthly_data.values())
        avg_monthly_expense = total_expenses / len(monthly_data) if monthly_data else 0

        # Income-expense advice
        recent_balance = self.calculate_balance()
        if recent_balance['balance'] < 0:
            suggestions.append("Your expenses exceed income, recommend creating a budget plan to control spending.")
        elif recent_balance['balance'] > recent_balance['total_income'] * 0.3:
            suggestions.append("Your savings rate is high, consider some investment products.")

        # Category spending advice
        if category_spending:
            max_category = max(category_spending, key=category_spending.get)
            max_amount = category_spending[max_category]
            if max_amount > avg_monthly_expense * 0.4:
                suggestions.append(
                    f"⚠️ '{max_category}' category spending is relatively high, recommend moderate control.")

        # Anomaly detection advice
        anomalies = self.detect_anomalies()
        if len(anomalies) > 0:
            suggestions.append(f"Detected {len(anomalies)} anomalous large expenses, please verify.")

        return suggestions if suggestions else ["Your financial status is good, keep it up!"]