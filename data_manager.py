import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


DATE_FMT = "%Y-%m-%d"


class DataManager:
    """Data Management Class - Responsible for data storage, reading/writing and validation"""

    def __init__(self, data_file: str = "finance_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    # Core data file operations
    def load_data(self) -> Dict:
        """Load data from JSON file, or return default structure if missing/corrupted."""
        try:
            if not os.path.exists(self.data_file):
                return self.get_default_data()

            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Minimal schema guard / backfill defaults
            defaults = self.get_default_data()
            if not isinstance(data, dict):
                return defaults
            data.setdefault("transactions", [])
            data.setdefault("budgets", {})
            data.setdefault("goals", [])
            data.setdefault("categories", defaults["categories"])
            data.setdefault("settings", defaults["settings"])
            return data

        except (json.JSONDecodeError, OSError, ValueError) as e:
            print(f"Data loading error: {e}")
            return self.get_default_data()

    def get_default_data(self) -> Dict:
        """Default data structure."""
        return {
            "transactions": [],
            "budgets": {},
            "goals": [],
            "categories": {
                "income": ["Salary", "Bonus", "Investment Return", "Other Income"],
                "expense": [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Entertainment",
                    "Housing",
                    "Medical",
                    "Education",
                    "Other Expense",
                ],
            },
            "settings": {
                "currency": "USD",
                "date_format": DATE_FMT,
                "backup_enabled": True,
            },
        }

    def save_data(self) -> bool:
        """Persist in-memory data to disk (UTF-8, indent=2). Creates a backup if enabled."""
        try:
            if self.data.get("settings", {}).get("backup_enabled", True):
                self.create_backup()
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            print(f"Data saving error: {e}")
            return False

    def create_backup(self) -> bool:
        """Create a timestamped backup of the current JSON file (if it exists)."""
        try:
            if os.path.exists(self.data_file):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.data_file}.backup_{ts}"
                with open(self.data_file, "r", encoding="utf-8") as src, open(
                    backup_filename, "w", encoding="utf-8"
                ) as dst:
                    dst.write(src.read())
                return True
        except OSError as e:
            print(f"Backup creation error: {e}")
        return False

    # Transaction operations
    def validate_transaction(self, transaction: Dict) -> bool:
        """
        Validate a transaction object.

        Required fields: 'date' (YYYY-MM-DD), 'type' in {'income','expense'},
        'category' (non-empty str), 'amount' (float > 0), 'description' (str).
        """
        required = ["date", "type", "category", "amount", "description"]
        if not all(k in transaction for k in required):
            return False

        try:
            # Date format
            datetime.strptime(str(transaction["date"]), DATE_FMT)

            # Type
            if transaction["type"] not in {"income", "expense"}:
                return False

            # Amount
            amt = float(transaction["amount"])
            if amt <= 0:
                return False

            # Category must be a non-empty string (allow custom categories)
            cat = str(transaction["category"]).strip()
            if not cat:
                return False

            # Description must be a string (allow empty but present)
            _ = str(transaction["description"])

            return True

        except (ValueError, TypeError):
            return False

    def _new_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        return f"TXN_{uuid.uuid4().hex}"

    def add_transaction(self, transaction: Dict) -> bool:
        """Validate and append a transaction, adding id and created_at metadata."""
        try:
            if not self.validate_transaction(transaction):
                return False

            record = {
                "id": self._new_transaction_id(),
                "date": str(transaction["date"]),
                "type": transaction["type"],
                "category": str(transaction["category"]),
                "amount": float(transaction["amount"]),
                "description": str(transaction["description"]),
                "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            self.data["transactions"].append(record)
            return self.save_data()
        except Exception as e:
            print(f"Add transaction error: {e}")
            return False

    def update_transaction(self, transaction_id: str, updated_data: Dict) -> bool:
        """Update an existing transaction by id (re-validates merged record)."""
        try:
            for i, t in enumerate(self.data.get("transactions", [])):
                if t.get("id") == transaction_id:
                    merged = {**t, **updated_data}
                    if not self.validate_transaction(merged):
                        return False
                    merged["amount"] = float(merged["amount"])
                    merged["last_modified"] = datetime.utcnow().strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                    self.data["transactions"][i] = merged
                    return self.save_data()
            return False
        except Exception as e:
            print(f"Update transaction error: {e}")
            return False

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction by id."""
        try:
            before = len(self.data.get("transactions", []))
            self.data["transactions"] = [
                t for t in self.data.get("transactions", []) if t.get("id") != transaction_id
            ]
            if len(self.data["transactions"]) < before:
                return self.save_data()
            return False
        except Exception as e:
            print(f"Delete transaction error: {e}")
            return False

    def get_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """
        Return transactions filtered by optional bounds and attributes.
        - start_date/end_date may be YYYY-MM-DD strings or datetime objects.
        - Filtering is inclusive.
        """
        txns = list(self.data.get("transactions", []))  # copy for safety

        def to_dt(val: Optional[object]) -> Optional[datetime]:
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            return datetime.strptime(str(val), DATE_FMT)

        start = to_dt(start_date)
        end = to_dt(end_date)

        out: List[Dict] = []
        for t in txns:
            try:
                d = datetime.strptime(t["date"], DATE_FMT)
                if start is not None and d < start:
                    continue
                if end is not None and d > end:
                    continue
                if transaction_type and t.get("type") != transaction_type:
                    continue
                if category and t.get("category") != category:
                    continue
                out.append(t.copy())
            except Exception:
                # Skip malformed records quietly
                continue

        # Optional: sort by date ascending
        out.sort(key=lambda x: x.get("date", ""))
        return out

    # CSV import/export
    def import_from_csv(self, file_path: str) -> Dict:
        """
        Import transactions from a CSV with columns:
        date, type, category, amount, description

        Returns:
          {'success': bool, 'imported_count': int, 'failed_count': int, 'errors': [str]}
        """
        results = {
            "success": False,
            "imported_count": 0,
            "failed_count": 0,
            "errors": [],
        }
        try:
            df = pd.read_csv(file_path)
            required = ["date", "type", "category", "amount", "description"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                results["errors"].append(f"Missing required columns: {missing}")
                return results

            for idx, row in df.iterrows():
                try:
                    txn = {
                        "date": str(row["date"]),
                        "type": str(row["type"]).lower(),
                        "category": str(row["category"]),
                        "amount": float(row["amount"]),
                        "description": str(row["description"]),
                    }
                    ok = self.add_transaction(txn)
                    if ok:
                        results["imported_count"] += 1
                    else:
                        results["failed_count"] += 1
                        results["errors"].append(
                            f"Row {idx + 1}: invalid transaction data"
                        )
                except Exception as e:
                    results["failed_count"] += 1
                    results["errors"].append(f"Row {idx + 1}: {str(e)}")

            results["success"] = results["imported_count"] > 0 and results["failed_count"] == 0
            return results

        except Exception as e:
            results["errors"].append(f"File processing error: {str(e)}")
            return results

    def export_to_csv(
        self,
        file_path: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> bool:
        """
        Export transactions to CSV.
        Per spec, include only headers:
        date, type, category, amount, description
        """
        try:
            txns = self.get_transactions(start_date=start_date, end_date=end_date)
            rows = [
                {
                    "date": t.get("date", ""),
                    "type": t.get("type", ""),
                    "category": t.get("category", ""),
                    "amount": t.get("amount", ""),
                    "description": t.get("description", ""),
                }
                for t in txns
            ]
            df = pd.DataFrame(rows, columns=["date", "type", "category", "amount", "description"])
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    # Categories & statistics
    def add_category(self, category_type: str, category_name: str) -> bool:
        """Add a new income/expense category (idempotent)."""
        try:
            if category_type not in {"income", "expense"}:
                return False
            category_name = str(category_name).strip()
            if not category_name:
                return False
            lst = self.data["categories"].setdefault(category_type, [])
            if category_name not in lst:
                lst.append(category_name)
                return self.save_data()
            return True
        except Exception as e:
            print(f"Add category error: {e}")
            return False

    def remove_category(self, category_type: str, category_name: str) -> bool:
        """Remove a category if it is not used by any transaction."""
        try:
            if category_type not in {"income", "expense"}:
                return False
            used = any(
                t.get("category") == category_name
                for t in self.data.get("transactions", [])
            )
            if used:
                return False
            if category_name in self.data["categories"].get(category_type, []):
                self.data["categories"][category_type].remove(category_name)
                return self.save_data()
            return False
        except Exception as e:
            print(f"Remove category error: {e}")
            return False

    def get_data_statistics(self) -> Dict:
        """
        Return summary statistics:
          total_transactions, income_count, expense_count, file_size, date_range
        """
        txns = self.data.get("transactions", [])
        income = sum(1 for t in txns if t.get("type") == "income")
        expense = sum(1 for t in txns if t.get("type") == "expense")
        dates = []
        for t in txns:
            try:
                dates.append(datetime.strptime(t["date"], DATE_FMT))
            except Exception:
                pass
        date_range = (
            None if not dates else {"earliest": min(dates).strftime(DATE_FMT), "latest": max(dates).strftime(DATE_FMT)}
        )
        try:
            file_size = os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
        except OSError:
            file_size = 0
        return {
            "total_transactions": len(txns),
            "income_count": income,
            "expense_count": expense,
            "file_size": file_size,
            "date_range": date_range,
        }


# Simple test
if __name__ == "__main__":
    dm = DataManager("test_finance_data.json")

    sample = {
        "date": "2024-01-01",
        "type": "expense",
        "category": "Food",
        "amount": 50.0,
        "description": "Lunch at restaurant",
    }
    print("Add txn:", dm.add_transaction(sample))
    print("Txns:", len(dm.get_transactions()))
    print("Stats:", dm.get_data_statistics())

    try:
        os.remove("test_finance_data.json")
    except Exception:
        pass
