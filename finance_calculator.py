import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class FinanceCalculator:

    def __init__(self, data_manager):

        self.data_manager = data_manager

    def calculate_balance(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, float]:

        try:
            # Get transactions from data manager
            transactions = self.data_manager.get_transactions(start_date, end_date)

            total_income = 0.0
            total_expense = 0.0
            transaction_count = len(transactions)

            # Sum transactions by type
            for transaction in transactions:
                amount = float(transaction.get('amount', 0))
                transaction_type = transaction.get('type', '').lower()

                if transaction_type == 'income':
                    total_income += amount
                elif transaction_type == 'expense':
                    total_expense += amount

            balance = total_income - total_expense

            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
                'transaction_count': transaction_count
            }

        except Exception as e:
            print(f"Error calculating balance: {e}")
            return {
                'total_income': 0.0,
                'total_expense': 0.0,
                'balance': 0.0,
                'transaction_count': 0
            }

    def analyze_spending_by_category(self, months: int = 12) -> Dict[str, float]:

        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            # Get transactions for the period
            transactions = self.data_manager.get_transactions(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            category_spending = {}

            # Group expense transactions by category
            for transaction in transactions:
                if transaction.get('type', '').lower() == 'expense':
                    category = transaction.get('category', 'Unknown')
                    amount = float(transaction.get('amount', 0))

                    if category in category_spending:
                        category_spending[category] += amount
                    else:
                        category_spending[category] = amount

            return category_spending

        except Exception as e:
            print(f"Error analyzing spending by category: {e}")
            return {}

    def calculate_monthly_trend(self, months: int = 12) -> Dict[str, Dict[str, float]]:

        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            # Get transactions for the period
            transactions = self.data_manager.get_transactions(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            monthly_data = {}

            # Process each transaction
            for transaction in transactions:
                try:
                    # Extract month from date
                    transaction_date = datetime.strptime(transaction.get('date', ''), '%Y-%m-%d')
                    month_key = transaction_date.strftime('%Y-%m')

                    # Initialize month if not exists
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'income': 0.0, 'expense': 0.0}

                    # Add amount to appropriate category
                    amount = float(transaction.get('amount', 0))
                    transaction_type = transaction.get('type', '').lower()

                    if transaction_type == 'income':
                        monthly_data[month_key]['income'] += amount
                    elif transaction_type == 'expense':
                        monthly_data[month_key]['expense'] += amount

                except (ValueError, TypeError) as e:
                    print(f"Error processing transaction date: {e}")
                    continue

            return monthly_data

        except Exception as e:
            print(f"Error calculating monthly trend: {e}")
            return {}

    def detect_anomalies(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:

        try:
            # Get all expense transactions
            all_transactions = self.data_manager.get_transactions()
            expense_transactions = [t for t in all_transactions if t.get('type', '').lower() == 'expense']

            if len(expense_transactions) < 3:  # Need minimum data for statistical analysis
                return []

            # Extract amounts
            amounts = [float(t.get('amount', 0)) for t in expense_transactions]

            if not amounts:
                return []

            # Calculate statistics
            mean_amount = statistics.mean(amounts)
            if len(amounts) == 1:
                std_dev = 0
            else:
                std_dev = statistics.stdev(amounts)

            threshold = mean_amount + (threshold_multiplier * std_dev)
            anomalies = []

            # Find anomalous transactions
            for transaction in expense_transactions:
                amount = float(transaction.get('amount', 0))
                if amount > threshold:
                    deviation = (amount - mean_amount) / std_dev if std_dev > 0 else 0
                    anomalies.append({
                        'transaction': transaction,
                        'deviation': round(deviation, 2),
                        'threshold': round(threshold, 2)
                    })

            # Sort by deviation (highest first)
            anomalies.sort(key=lambda x: x['deviation'], reverse=True)

            return anomalies

        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []

    def generate_smart_suggestions(self) -> List[str]:

        try:
            suggestions = []

            # Analyze recent 3 months data
            balance_info = self.calculate_balance(
                (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            )
            category_spending = self.analyze_spending_by_category(3)
            monthly_trends = self.calculate_monthly_trend(3)
            anomalies = self.detect_anomalies()

            # 1. Savings rate analysis
            total_income = balance_info['total_income']
            total_expense = balance_info['total_expense']

            if total_income > 0:
                savings_rate = (total_income - total_expense) / total_income

                if savings_rate < 0:
                    suggestions.append(
                        "Warning: You're spending more than you earn. Review your expenses immediately and identify areas to cut back.")
                elif savings_rate < 0.10:
                    suggestions.append(
                        "Try to save at least 10% of your income. Consider reducing discretionary spending like dining out or entertainment.")
                elif savings_rate < 0.20:
                    suggestions.append(
                        "Good progress! Aim to increase your savings rate to 20% by optimizing your largest expense categories.")
                else:
                    suggestions.append(
                        "Excellent savings rate! Consider investing your surplus or building an emergency fund.")

            # 2. Category spending analysis
            if category_spending:
                total_category_spending = sum(category_spending.values())

                for category, amount in category_spending.items():
                    if total_category_spending > 0:
                        percentage = amount / total_category_spending
                        if percentage > 0.40:  # 40% threshold
                            suggestions.append(
                                f"{category} accounts for {percentage:.1%} of your spending. Consider budgeting or finding alternatives in this area.")

                # Find highest spending category
                if category_spending:
                    highest_category = max(category_spending, key=category_spending.get)
                    suggestions.append(
                        f"Your highest spending category is {highest_category}. Review these transactions for potential savings.")

            # 3. Anomaly analysis
            if anomalies:
                recent_anomalies = [a for a in anomalies[:3]]  # Top 3 anomalies
                if recent_anomalies:
                    suggestions.append(
                        f"Detected {len(anomalies)} unusually high expenses. Review large transactions like '{recent_anomalies[0]['transaction'].get('description', 'Unknown')}' for accuracy.")

            # 4. Trend analysis
            if len(monthly_trends) >= 2:
                months = sorted(monthly_trends.keys())
                if len(months) >= 2:
                    recent_month = monthly_trends[months[-1]]
                    previous_month = monthly_trends[months[-2]]

                    expense_change = recent_month['expense'] - previous_month['expense']
                    if expense_change > 0:
                        change_percent = (expense_change / previous_month['expense']) * 100 if previous_month[
                                                                                                   'expense'] > 0 else 0
                        if change_percent > 20:
                            suggestions.append(
                                f"Your expenses increased by {change_percent:.1f}% last month. Identify what drove this increase.")
                    else:
                        change_percent = abs(expense_change / previous_month['expense']) * 100 if previous_month[
                                                                                                      'expense'] > 0 else 0
                        if change_percent > 10:
                            suggestions.append(
                                f"Great job! You reduced expenses by {change_percent:.1f}% last month. Keep up the good work!")

            # 5. General financial health suggestions
            if balance_info['transaction_count'] < 10:
                suggestions.append(
                    "Track more transactions to get better insights. Consider logging smaller daily expenses too.")

            # Ensure we have at least 3 suggestions
            if len(suggestions) < 3:
                suggestions.extend([
                    "Set up monthly budgets for your top spending categories.",
                    "Create specific savings goals to stay motivated.",
                    "Consider using automatic savings transfers to reach your goals."
                ])

            # Return maximum 5 suggestions
            return suggestions[:5]

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return [
                "Start by tracking all your income and expenses regularly.",
                "Set monthly budgets for different spending categories.",
                "Aim to save at least 20% of your income each month."
            ]

    def calculate_financial_health_score(self) -> Dict[str, Any]:

        try:
            score = 0
            max_score = 100
            factors = {}

            # Get recent data (6 months)
            balance_info = self.calculate_balance(
                (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            )
            category_spending = self.analyze_spending_by_category(6)
            anomalies = self.detect_anomalies()

            # 1. Savings Rate Score (30 points max)
            total_income = balance_info['total_income']
            total_expense = balance_info['total_expense']

            if total_income > 0:
                savings_rate = (total_income - total_expense) / total_income
                if savings_rate >= 0.30:  # 30% or more
                    savings_score = 30
                elif savings_rate >= 0.20:  # 20-30%
                    savings_score = 25
                elif savings_rate >= 0.10:  # 10-20%
                    savings_score = 20
                elif savings_rate >= 0:  # 0-10%
                    savings_score = 10
                else:  # Negative savings
                    savings_score = 0
            else:
                savings_score = 0

            score += savings_score
            factors['savings_rate'] = {
                'score': savings_score,
                'max': 30,
                'rate': f"{savings_rate:.1%}" if total_income > 0 else "0%"
            }

            # 2. Spending Consistency Score (25 points max)
            monthly_trends = self.calculate_monthly_trend(6)
            if len(monthly_trends) >= 3:
                monthly_expenses = [data['expense'] for data in monthly_trends.values()]
                if len(monthly_expenses) > 1:
                    expense_std = statistics.stdev(monthly_expenses)
                    expense_mean = statistics.mean(monthly_expenses)

                    # Lower variation is better
                    if expense_mean > 0:
                        coefficient_of_variation = expense_std / expense_mean
                        if coefficient_of_variation <= 0.15:  # Very consistent
                            consistency_score = 25
                        elif coefficient_of_variation <= 0.25:  # Moderately consistent
                            consistency_score = 20
                        elif coefficient_of_variation <= 0.35:  # Somewhat consistent
                            consistency_score = 15
                        else:  # Inconsistent
                            consistency_score = 10
                    else:
                        consistency_score = 25
                else:
                    consistency_score = 15
            else:
                consistency_score = 15  # Neutral score for insufficient data

            score += consistency_score
            factors['spending_consistency'] = {
                'score': consistency_score,
                'max': 25,
                'description': "Based on monthly spending variation"
            }

            # 3. Category Balance Score (25 points max)
            if category_spending:
                total_spending = sum(category_spending.values())
                category_balance_score = 25

                # Penalize if any single category dominates spending
                for category, amount in category_spending.items():
                    percentage = amount / total_spending if total_spending > 0 else 0
                    if percentage > 0.50:  # More than 50%
                        category_balance_score -= 10
                    elif percentage > 0.40:  # More than 40%
                        category_balance_score -= 5

                category_balance_score = max(0, category_balance_score)
            else:
                category_balance_score = 15  # Neutral score for no data

            score += category_balance_score
            factors['category_balance'] = {
                'score': category_balance_score,
                'max': 25,
                'description': "Diversification of spending categories"
            }

            # 4. Anomaly Control Score (20 points max)
            transaction_count = balance_info['transaction_count']
            if transaction_count > 0:
                anomaly_rate = len(anomalies) / transaction_count
                if anomaly_rate <= 0.02:  # 2% or less anomalies
                    anomaly_score = 20
                elif anomaly_rate <= 0.05:  # 5% or less
                    anomaly_score = 15
                elif anomaly_rate <= 0.10:  # 10% or less
                    anomaly_score = 10
                else:  # More than 10%
                    anomaly_score = 5
            else:
                anomaly_score = 20  # Perfect score for no transactions

            score += anomaly_score
            factors['anomaly_control'] = {
                'score': anomaly_score,
                'max': 20,
                'anomaly_count': len(anomalies),
                'description': "Control over unusual spending"
            }

            # Determine health level
            percentage = (score / max_score) * 100
            if percentage >= 85:
                health_level = "Excellent"
            elif percentage >= 70:
                health_level = "Good"
            elif percentage >= 55:
                health_level = "Fair"
            elif percentage >= 40:
                health_level = "Poor"
            else:
                health_level = "Critical"

            return {
                'score': score,
                'max_score': max_score,
                'health_level': health_level,
                'factors': factors
            }

        except Exception as e:
            print(f"Error calculating financial health score: {e}")
            return {
                'score': 0,
                'max_score': 100,
                'health_level': "Unknown",
                'factors': {}
            }
