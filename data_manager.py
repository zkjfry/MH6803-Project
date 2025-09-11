import os
import json
from datetime import datetime
from typing import Dict, List
import pandas as pd
class DataManager:
    """Data Management Class - Responsible for data storage, reading/writing and validation"""

    def __init__(self, data_file="finance_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self) -> Dict:
        """Load data file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_data()
        except Exception as e:
            print(f"Data loading error: {e}")
            return self.get_default_data()

    def get_default_data(self) -> Dict:
        """Get default data structure"""
        return {
            "transactions": [],
            "budgets": {},
            "goals": [],
            "categories": {
                "income": ["Salary", "Bonus", "Investment Return", "Other Income"],
                "expense": ["Food", "Transport", "Shopping", "Entertainment", "Housing", "Medical", "Education",
                            "Other Expense"]
            }
        }

    def save_data(self) -> bool:
        """Save data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Data saving error: {e}")
            return False

    def add_transaction(self, transaction: Dict) -> bool:
        """Add transaction record"""
        try:
            # Data validation
            required_fields = ['date', 'type', 'category', 'amount', 'description']
            if not all(field in transaction for field in required_fields):
                return False

            # Add timestamp
            transaction['timestamp'] = datetime.now().isoformat()
            self.data["transactions"].append(transaction)
            return self.save_data()
        except Exception as e:
            print(f"Add transaction error: {e}")
            return False

    def get_transactions(self, start_date=None, end_date=None) -> List[Dict]:
        """Get transaction records"""
        transactions = self.data["transactions"]

        if start_date and end_date:
            filtered = []
            for t in transactions:
                t_date = datetime.strptime(t['date'], '%Y-%m-%d')
                if start_date <= t_date <= end_date:
                    filtered.append(t)
            return filtered

        return transactions

    def import_from_csv(self, file_path: str) -> bool:
        """Import data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            required_columns = ['date', 'type', 'category', 'amount', 'description']

            if not all(col in df.columns for col in required_columns):
                return False

            for _, row in df.iterrows():
                transaction = {
                    'date': str(row['date']),
                    'type': str(row['type']),
                    'category': str(row['category']),
                    'amount': float(row['amount']),
                    'description': str(row['description'])
                }
                self.add_transaction(transaction)

            return True
        except Exception as e:
            print(f"CSV import error: {e}")
            return False

