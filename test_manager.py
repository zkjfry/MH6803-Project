# test_manager.py
# Member 6: Testing & Documentation (10%)
# Write test cases, system testing, documentation writing and maintenance

import unittest
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, List

class TestManager:
    """Testing management class

    This class orchestrates automated tests across modules. It follows the
    development specification by providing reversible tests, comprehensive error
    handling (including file operations), and a professional report generator.
    """
    
    def __init__(self, data_manager, calculator) -> None:
        """Initialize with references to data and calculation components."""
        self.data_manager = data_manager
        self.calculator = calculator
        self.test_results: List[Dict] = []
    
    def run_all_tests(self) -> Dict:
        """Run all automated tests and return aggregated statistics."""
        self.test_results = []
        
        print("Starting comprehensive system tests...")
        
        # Data management tests
        self.test_data_operations()
        self.test_data_validation()
        self.test_csv_operations()
        
        # Calculation accuracy tests
        self.test_calculation_accuracy()
        self.test_financial_analysis()
        
        # Error handling tests
        self.test_error_handling()
        self.test_edge_cases()
        
        # Performance tests
        self.test_performance()
        
        # Statistics test results
        passed = sum(1 for result in self.test_results if result['status'] == 'PASS')
        total = len(self.test_results)
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_data_operations(self) -> None:
        """Test basic data operations (reversible)."""
        test_name = "Data Operations Test"
        
        try:
            # Snapshot original data to ensure reversibility
            original_transactions = list(self.data_manager.get_transactions())
            # Test adding transaction
            test_transaction = {
                'date': '2024-01-01',
                'type': 'expense',
                'category': 'Food',
                'amount': 50.0,
                'description': 'Test transaction'
            }
            
            initial_count = len(self.data_manager.get_transactions())
            success = self.data_manager.add_transaction(test_transaction)
            final_count = len(self.data_manager.get_transactions())
            
            if success and final_count == initial_count + 1:
                self._add_test_result(test_name, 'PASS', 'Transaction added successfully')
            else:
                self._add_test_result(test_name, 'FAIL', 'Transaction addition failed')
                
        except Exception as e:
            self._add_test_result(test_name, 'FAIL', f'Exception: {str(e)}')
        finally:
            # Restore original data to avoid side effects
            try:
                self.data_manager.data['transactions'] = original_transactions
            except Exception:
                pass
    
    def test_data_validation(self) -> None:
        """Test data validation mechanisms."""
        test_cases = [
            {
                'name': 'Invalid Date Format',
                'data': {'date': 'invalid-date', 'type': 'expense', 'category': 'Food', 'amount': 50, 'description': 'Test'},
                'should_fail': True
            },
            {
                'name': 'Negative Amount',
                'data': {'date': '2024-01-01', 'type': 'expense', 'category': 'Food', 'amount': -50, 'description': 'Test'},
                'should_fail': True
            },
            {
                'name': 'Missing Required Field',
                'data': {'date': '2024-01-01', 'type': 'expense', 'amount': 50, 'description': 'Test'},
                'should_fail': True
            },
            {
                'name': 'Valid Transaction',
                'data': {'date': '2024-01-01', 'type': 'expense', 'category': 'Food', 'amount': 50, 'description': 'Test'},
                'should_fail': False
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.data_manager.validate_transaction(test_case['data'])
                
                if test_case['should_fail'] and not result:
                    self._add_test_result(f"Validation - {test_case['name']}", 'PASS', 
                                        'Correctly rejected invalid data')
                elif not test_case['should_fail'] and result:
                    self._add_test_result(f"Validation - {test_case['name']}", 'PASS', 
                                        'Correctly accepted valid data')
                else:
                    self._add_test_result(f"Validation - {test_case['name']}", 'FAIL', 
                                        'Validation logic failed')
                    
            except Exception as e:
                self._add_test_result(f"Validation - {test_case['name']}", 'FAIL', 
                                    f'Exception: {str(e)}')
    
    def test_csv_operations(self) -> None:
        """Test CSV import/export functionality (reversible)."""
        try:
            # Snapshot original data to ensure reversibility
            original_transactions = list(self.data_manager.get_transactions())
            # Create temporary CSV file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write('date,type,category,amount,description\n')
                f.write('2024-01-01,income,Salary,1000.00,Monthly salary\n')
                f.write('2024-01-02,expense,Food,50.00,Lunch\n')
                temp_csv = f.name
            
            try:
                # Test import
                initial_count = len(self.data_manager.get_transactions())
                result = self.data_manager.import_from_csv(temp_csv)
                final_count = len(self.data_manager.get_transactions())
                
                if result['success'] and result['imported_count'] == 2:
                    self._add_test_result('CSV Import Test', 'PASS', 
                                        f'Successfully imported {result["imported_count"]} transactions')
                else:
                    self._add_test_result('CSV Import Test', 'FAIL', 
                                        f'Import failed: {result.get("errors", [])}')
                
                # Test export
                with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as export_file:
                    export_success = self.data_manager.export_to_csv(export_file.name)
                    
                    if export_success and os.path.exists(export_file.name):
                        self._add_test_result('CSV Export Test', 'PASS', 'Export successful')
                    else:
                        self._add_test_result('CSV Export Test', 'FAIL', 'Export failed')
                    
                    # Clean up export file
                    if os.path.exists(export_file.name):
                        os.unlink(export_file.name)
                        
            finally:
                # Clean up import file
                if os.path.exists(temp_csv):
                    os.unlink(temp_csv)
                # Restore original data to avoid pollution
                try:
                    self.data_manager.data['transactions'] = original_transactions
                except Exception:
                    pass
                    
        except Exception as e:
            self._add_test_result('CSV Operations Test', 'FAIL', f'Exception: {str(e)}')
    
    def test_calculation_accuracy(self) -> None:
        """Test financial calculation accuracy (reversible)."""
        try:
            # Create test data
            test_transactions = [
                {'date': '2024-01-01', 'type': 'income', 'category': 'Salary', 'amount': 1000.0, 'description': 'Test income'},
                {'date': '2024-01-02', 'type': 'expense', 'category': 'Food', 'amount': 100.0, 'description': 'Test expense'},
                {'date': '2024-01-03', 'type': 'expense', 'category': 'Transport', 'amount': 50.0, 'description': 'Test transport'}
            ]
            
            # Save original data
            original_transactions = self.data_manager.data['transactions'].copy()
            
            # Add test data
            for t in test_transactions:
                self.data_manager.add_transaction(t)
            
            # Test balance calculation
            balance_info = self.calculator.calculate_balance()
            expected_income = 1000.0
            expected_expense = 150.0
            expected_balance = 850.0
            
            # Allow for small floating point differences
            income_correct = abs(balance_info['total_income'] - expected_income) < 0.01
            expense_correct = abs(balance_info['total_expense'] - expected_expense) < 0.01
            balance_correct = abs(balance_info['balance'] - expected_balance) < 0.01
            
            if income_correct and expense_correct and balance_correct:
                self._add_test_result('Balance Calculation Test', 'PASS', 
                                    f'Calculations correct: Income=${balance_info["total_income"]}, '
                                    f'Expense=${balance_info["total_expense"]}, '
                                    f'Balance=${balance_info["balance"]}')
            else:
                self._add_test_result('Balance Calculation Test', 'FAIL', 
                                    f'Calculation error: Expected Balance=${expected_balance}, '
                                    f'Got=${balance_info["balance"]}')
            
            # Restore original data
            self.data_manager.data['transactions'] = original_transactions
            
        except Exception as e:
            self._add_test_result('Calculation Accuracy Test', 'FAIL', f'Exception: {str(e)}')
    
    def test_financial_analysis(self) -> None:
        """Test financial analysis functions."""
        try:
            # Test category analysis
            category_data = self.calculator.analyze_spending_by_category(12)
            
            if isinstance(category_data, dict):
                self._add_test_result('Category Analysis Test', 'PASS', 
                                    f'Analysis returned {len(category_data)} categories')
            else:
                self._add_test_result('Category Analysis Test', 'FAIL', 
                                    'Category analysis failed to return dict')
            
            # Test monthly trends
            monthly_data = self.calculator.calculate_monthly_trend(12)
            
            if isinstance(monthly_data, dict):
                self._add_test_result('Monthly Trend Test', 'PASS', 
                                    f'Trend analysis returned {len(monthly_data)} months')
            else:
                self._add_test_result('Monthly Trend Test', 'FAIL', 
                                    'Monthly trend analysis failed')
            
            # Test anomaly detection
            anomalies = self.calculator.detect_anomalies()
            
            if isinstance(anomalies, list):
                self._add_test_result('Anomaly Detection Test', 'PASS', 
                                    f'Detected {len(anomalies)} anomalies')
            else:
                self._add_test_result('Anomaly Detection Test', 'FAIL', 
                                    'Anomaly detection failed')
                
        except Exception as e:
            self._add_test_result('Financial Analysis Test', 'FAIL', f'Exception: {str(e)}')
    
    def test_error_handling(self) -> None:
        """Test error handling mechanisms, including file operations."""
        try:
            # Test invalid transaction data
            invalid_transactions = [
                {'date': 'invalid', 'type': 'invalid', 'amount': -100},
                {'date': '2024-01-01'},  # Missing fields
                None,  # Null transaction
                {}  # Empty transaction
            ]
            
            error_handled_count = 0
            
            for invalid_tx in invalid_transactions:
                try:
                    result = self.data_manager.add_transaction(invalid_tx)
                    if not result:  # Should fail
                        error_handled_count += 1
                except:
                    error_handled_count += 1  # Exception is also proper error handling
            
            if error_handled_count == len(invalid_transactions):
                self._add_test_result('Error Handling Test', 'PASS', 
                                    'All invalid inputs properly handled')
            else:
                self._add_test_result('Error Handling Test', 'FAIL', 
                                    f'Only {error_handled_count}/{len(invalid_transactions)} errors handled')

            # File operation error tests
            # Import from non-existent file should fail or raise
            try:
                result = self.data_manager.import_from_csv('/non/existent/path/file.csv')
                if isinstance(result, dict) and not result.get('success', False):
                    self._add_test_result('File Error - CSV Import Nonexistent', 'PASS', 'Properly handled missing file')
                else:
                    self._add_test_result('File Error - CSV Import Nonexistent', 'FAIL', 'Did not report failure for missing file')
            except Exception:
                self._add_test_result('File Error - CSV Import Nonexistent', 'PASS', 'Exception properly raised for missing file')

            # Export to an invalid directory path should fail or raise
            try:
                export_ok = self.data_manager.export_to_csv('/non/existent/path/out.csv')
                if export_ok is False:
                    self._add_test_result('File Error - CSV Export Invalid Path', 'PASS', 'Properly reported failure')
                else:
                    self._add_test_result('File Error - CSV Export Invalid Path', 'FAIL', 'Did not report failure for invalid path')
            except Exception:
                self._add_test_result('File Error - CSV Export Invalid Path', 'PASS', 'Exception properly raised for invalid path')
                
        except Exception as e:
            self._add_test_result('Error Handling Test', 'FAIL', f'Test exception: {str(e)}')
    
    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        edge_cases = [
            {
                'name': 'Zero Amount Transaction',
                'data': {'date': '2024-01-01', 'type': 'expense', 'category': 'Food', 'amount': 0, 'description': 'Zero'},
                'should_pass': False
            },
            {
                'name': 'Very Large Amount',
                'data': {'date': '2024-01-01', 'type': 'income', 'category': 'Salary', 'amount': 999999999, 'description': 'Large'},
                'should_pass': True
            },
            {
                'name': 'Future Date',
                'data': {'date': '2030-01-01', 'type': 'expense', 'category': 'Food', 'amount': 50, 'description': 'Future'},
                'should_pass': True
            },
            {
                'name': 'Very Old Date',
                'data': {'date': '1900-01-01', 'type': 'expense', 'category': 'Food', 'amount': 50, 'description': 'Old'},
                'should_pass': True
            }
        ]
        
        for case in edge_cases:
            try:
                result = self.data_manager.validate_transaction(case['data'])
                
                if result == case['should_pass']:
                    self._add_test_result(f"Edge Case - {case['name']}", 'PASS', 
                                        'Boundary condition handled correctly')
                else:
                    self._add_test_result(f"Edge Case - {case['name']}", 'FAIL', 
                                        'Boundary condition not handled properly')
                    
            except Exception as e:
                self._add_test_result(f"Edge Case - {case['name']}", 'FAIL', f'Exception: {str(e)}')
    
    def test_performance(self) -> None:
        """Test system performance with larger datasets (reversible)."""
        try:
            start_time = datetime.now()
            
            # Snapshot original data
            original_transactions = list(self.data_manager.get_transactions())
            # Add multiple transactions to test performance
            for i in range(100):
                test_transaction = {
                    'date': f'2024-01-{(i % 30) + 1:02d}',
                    'type': 'expense' if i % 2 == 0 else 'income',
                    'category': 'Food' if i % 2 == 0 else 'Salary',
                    'amount': float(50 + (i % 100)),
                    'description': f'Performance test transaction {i}'
                }
                self.data_manager.add_transaction(test_transaction)
            
            # Test calculation performance
            self.calculator.calculate_balance()
            self.calculator.analyze_spending_by_category(12)
            self.calculator.calculate_monthly_trend(12)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if execution_time < 5.0:  # Should complete within 5 seconds
                self._add_test_result('Performance Test', 'PASS', 
                                    f'100 transactions processed in {execution_time:.2f} seconds')
            else:
                self._add_test_result('Performance Test', 'FAIL', 
                                    f'Performance too slow: {execution_time:.2f} seconds')
                
        except Exception as e:
            self._add_test_result('Performance Test', 'FAIL', f'Exception: {str(e)}')
        finally:
            # Restore original data
            try:
                self.data_manager.data['transactions'] = original_transactions
            except Exception:
                pass
    
    def _add_test_result(self, test_name: str, status: str, message: str) -> None:
        """Add a structured test result to the results list."""
        self.test_results.append({
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_test_report(self, test_results: Dict, output_file: str = None) -> str:
        """Generate comprehensive test report as a formatted string."""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
AUTOMATED TEST REPORT
Generated: {report_time}
{'=' * 50}

TEST SUMMARY
Total Tests: {test_results['total_tests']}
Passed: {test_results['passed']}
Failed: {test_results['failed']}
Success Rate: {test_results['success_rate']:.1f}%

OVERALL STATUS: {'PASS' if test_results['success_rate'] >= 80 else 'FAIL'}

{'=' * 50}
DETAILED TEST RESULTS

"""
        
        # Group results by category
        categories = {}
        for result in test_results['results']:
            category = result['test_name'].split(' - ')[0] if ' - ' in result['test_name'] else 'General'
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, results in categories.items():
            report += f"\n{category.upper()} TESTS\n{'-' * 30}\n"
            
            for result in results:
                status_symbol = "✓" if result['status'] == 'PASS' else "✗"
                report += f"{status_symbol} {result['test_name']}: {result['message']}\n"
        
        report += f"\n{'=' * 50}\n"
        
        if test_results['failed'] > 0:
            report += "RECOMMENDATIONS:\n"
            if test_results['success_rate'] < 60:
                report += "- Critical issues detected. Immediate attention required.\n"
            elif test_results['success_rate'] < 80:
                report += "- Some issues detected. Review and fix recommended.\n"
            else:
                report += "- Minor issues detected. Consider addressing when convenient.\n"
        else:
            report += "EXCELLENT: All tests passed successfully!\n"
        
        report += f"\nEnd of Report\n{'=' * 50}\n"
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            except Exception as e:
                print(f"Failed to save report: {e}")
        
        return report
    
    def create_unit_test_suite(self):
        """Create unit test suite using unittest framework.

        Fixes closure to correctly reference outer `data_manager` and `calculator`.
        """
        outer_data_manager = self.data_manager
        outer_calculator = self.calculator

        class FinanceSystemTests(unittest.TestCase):
            
            def setUp(self):
                """Set up test fixtures."""
                self.test_data_manager = outer_data_manager
                self.test_calculator = outer_calculator
            
            def test_transaction_validation(self):
                """Test transaction validation."""
                valid_transaction = {
                    'date': '2024-01-01',
                    'type': 'expense',
                    'category': 'Food',
                    'amount': 50.0,
                    'description': 'Test'
                }
                self.assertTrue(self.test_data_manager.validate_transaction(valid_transaction))
                
                invalid_transaction = {
                    'date': 'invalid',
                    'type': 'expense',
                    'category': 'Food',
                    'amount': -50.0,
                    'description': 'Test'
                }
                self.assertFalse(self.test_data_manager.validate_transaction(invalid_transaction))
            
            def test_balance_calculation(self):
                """Test balance calculation accuracy."""
                balance = self.test_calculator.calculate_balance()
                self.assertIsInstance(balance, dict)
                self.assertIn('total_income', balance)
                self.assertIn('total_expense', balance)
                self.assertIn('balance', balance)
            
            def test_category_analysis(self):
                """Test category analysis."""
                analysis = self.test_calculator.analyze_spending_by_category(1)
                self.assertIsInstance(analysis, dict)
        
        return FinanceSystemTests

if __name__ == "__main__":
    # Test the TestManager itself
    class MockDataManager:
        def __init__(self):
            self.data = {'transactions': []}
        
        def get_transactions(self):
            return self.data['transactions']
        
        def add_transaction(self, transaction):
            if self.validate_transaction(transaction):
                self.data['transactions'].append(transaction)
                return True
            return False
        
        def validate_transaction(self, transaction):
            required = ['date', 'type', 'category', 'amount', 'description']
            return (all(field in transaction for field in required) and 
                   transaction['amount'] > 0)
        
        def import_from_csv(self, file_path):
            return {'success': True, 'imported_count': 2, 'failed_count': 0, 'errors': []}
        
        def export_to_csv(self, file_path):
            return True
    
    class MockCalculator:
        def __init__(self, data_manager):
            self.data_manager = data_manager
        
        def calculate_balance(self):
            return {'total_income': 1000, 'total_expense': 150, 'balance': 850}
        
        def analyze_spending_by_category(self, months):
            return {'Food': 100, 'Transport': 50}
        
        def calculate_monthly_trend(self, months):
            return {'2024-01': {'income': 1000, 'expense': 150}}
        
        def detect_anomalies(self):
            return []
    
    # Run tests
    dm = MockDataManager()
    calc = MockCalculator(dm)
    test_manager = TestManager(dm, calc)
    
    results = test_manager.run_all_tests()
    print(f"Test Results: {results['passed']}/{results['total_tests']} passed")
    
    report = test_manager.generate_test_report(results)
    print("\nTest Report:")
    print(report)