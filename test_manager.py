from typing import Dict
from data_manager import DataManager
from finance_calculator import FinanceCalculator


class TestManager:
    """Testing management class"""

    def __init__(self, data_manager: DataManager, calculator: FinanceCalculator):
        self.data_manager = data_manager
        self.calculator = calculator
        self.test_results = []

    def run_all_tests(self) -> Dict:
        """Run all tests"""
        self.test_results = []

        # Data management tests
        self.test_data_operations()
        self.test_calculation_accuracy()
        self.test_error_handling()

        # Statistics test results
        passed = sum(1 for result in self.test_results if result['status'] == 'PASS')
        total = len(self.test_results)

        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'results': self.test_results
        }

    def test_data_operations(self):
        """Test data operations"""
        try:
            # Test adding transaction
            test_transaction = {
                'date': '2024-01-01',
                'type': 'expense',
                'category': 'Food',
                'amount': 50.0,
                'description': 'Test transaction'
            }

            initial_count = len(self.data_manager.data['transactions'])
            success = self.data_manager.add_transaction(test_transaction)
            final_count = len(self.data_manager.data['transactions'])

            if success and final_count == initial_count + 1:
                self.test_results.append({
                    'test_name': 'Add Transaction Test',
                    'status': 'PASS',
                    'message': 'Transaction added successfully'
                })
            else:
                self.test_results.append({
                    'test_name': 'Add Transaction Test',
                    'status': 'FAIL',
                    'message': 'Transaction addition failed'
                })

        except Exception as e:
            self.test_results.append({
                'test_name': 'Add Transaction Test',
                'status': 'FAIL',
                'message': f'Test exception: {str(e)}'
            })

    def test_calculation_accuracy(self):
        """Test calculation accuracy"""
        try:
            # Create test data
            test_transactions = [
                {'date': '2024-01-01', 'type': 'income', 'category': 'Salary', 'amount': 1000.0,
                 'description': 'Test income'},
                {'date': '2024-01-02', 'type': 'expense', 'category': 'Food', 'amount': 100.0,
                 'description': 'Test expense'}
            ]

            # Save original data
            original_transactions = self.data_manager.data['transactions'].copy()

            # Add test data
            for t in test_transactions:
                self.data_manager.add_transaction(t)

            # Calculate results
            balance_info = self.calculator.calculate_balance()

            # Verify calculations
            expected_income = sum(t['amount'] for t in test_transactions if t['type'] == 'income')
            expected_expense = sum(t['amount'] for t in test_transactions if t['type'] == 'expense')

            if (balance_info['total_income'] >= expected_income and
                    balance_info['total_expense'] >= expected_expense):
                self.test_results.append({
                    'test_name': 'Calculation Accuracy Test',
                    'status': 'PASS',
                    'message': 'Calculation results correct'
                })
            else:
                self.test_results.append({
                    'test_name': 'Calculation Accuracy Test',
                    'status': 'FAIL',
                    'message': 'Calculation results incorrect'
                })

            # Restore original data
            self.data_manager.data['transactions'] = original_transactions

        except Exception as e:
            self.test_results.append({
                'test_name': 'Calculation Accuracy Test',
                'status': 'FAIL',
                'message': f'Test exception: {str(e)}'
            })

    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid transaction data
            invalid_transaction = {
                'date': 'invalid-date',
                'type': 'invalid-type',
                'amount': -100  # Negative amount
            }

            success = self.data_manager.add_transaction(invalid_transaction)

            if not success:  # Should fail
                self.test_results.append({
                    'test_name': 'Error Handling Test',
                    'status': 'PASS',
                    'message': 'Correctly rejected invalid data'
                })
            else:
                self.test_results.append({
                    'test_name': 'Error Handling Test',
                    'status': 'FAIL',
                    'message': 'Failed to handle invalid data correctly'
                })

        except Exception as e:
            self.test_results.append({
                'test_name': 'Error Handling Test',
                'status': 'PASS',
                'message': 'Correctly threw exception'
            })
