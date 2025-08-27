import json, os
from datetime import datetime
import pandas as pd

class DataManager:
    def __init__(self, data_file="finance_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(self.data_file):
                return self.get_default_data()
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # minimal schema guard
            if "transactions" not in data or "categories" not in data:
                return self.get_default_data()
            return data
        except (json.JSONDecodeError, OSError):
            return self.get_default_data()

    def get_default_data(self):
        return {
            "transactions": [],
            "budgets": {},
            "goals": [],
            "categories": {
                "income": ["Salary", "Bonus", "Investment Return", "Other Income"],
                "expense": ["Food", "Transport", "Shopping", "Entertainment", "Housing",
                            "Medical", "Education", "Other Expense"]
            }
        }

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def validate_transaction(self, t):
        try:
            for k in ["date", "type", "category", "amount", "description"]:
                if k not in t: return False
            # date
            datetime.strptime(t["date"], "%Y-%m-%d")
            # type
            if t["type"] not in {"income", "expense"}: return False
            # amount
            amt = float(t["amount"])
            if amt <= 0: return False
            # category (allow custom categories—even if not in preset lists)
            if not isinstance(t["category"], str) or not t["category"].strip():
                return False
            return True
        except Exception:
            return False

    def add_transaction(self, t):
        if not self.validate_transaction(t):
            return False
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        uid = f"txn_{int(datetime.utcnow().timestamp()*1000)}_{len(self.data['transactions'])+1}"
        record = {
            "id": uid,
            "date": t["date"],
            "type": t["type"],
            "category": t["category"],
            "amount": float(t["amount"]),
            "description": t["description"],
            "created_at": now
        }
        self.data["transactions"].append(record)
        return self.save_data()

    def get_transactions(self, start_date=None, end_date=None):
        txns = list(self.data.get("transactions", []))  # copy
        if not start_date and not end_date:
            return txns
        def to_dt(s): return datetime.strptime(s, "%Y-%m-%d")
        start = to_dt(start_date) if start_date else None
        end = to_dt(end_date) if end_date else None
        out = []
        for t in txns:
            d = to_dt(t["date"])
            if (start is None or d >= start) and (end is None or d <= end):
                out.append(t)
        return out

    def import_from_csv(self, file_path):
        result = {"success": False, "imported_count": 0, "failed_count": 0, "errors": []}
        try:
            df = pd.read_csv(file_path)
            required = ["date", "type", "category", "amount", "description"]
            for r in required:
                if r not in df.columns:
                    result["errors"].append(f"Missing column: {r}")
                    return result
            imported = 0
            failed = 0
            for idx, row in df.iterrows():
                t = {k: row[k] for k in required}
                # coerce to str for date/type/category/description
                t["date"] = str(t["date"])
                t["type"] = str(t["type"]).lower()
                t["category"] = str(t["category"])
                t["description"] = str(t["description"])
                try:
                    t["amount"] = float(row["amount"])
                except Exception:
                    t["amount"] = -1
                ok = self.add_transaction(t)
                if ok:
                    imported += 1
                else:
                    failed += 1
                    result["errors"].append(f"Row {idx+1}: invalid transaction")
            result["success"] = failed == 0
            result["imported_count"] = imported
            result["failed_count"] = failed
            return result
        except Exception as e:
            result["errors"].append(str(e))
            return result

    def export_to_csv(self, file_path):
        try:
            cols = ["date", "type", "category", "amount", "description"]
            rows = [{c: t.get(c, "") for c in cols} for t in self.data.get("transactions", [])]
            pd.DataFrame(rows, columns=cols).to_csv(file_path, index=False)
            return True
        except Exception:
            return False

    def get_data_statistics(self):
        txns = self.data.get("transactions", [])
        income = sum(1 for t in txns if t.get("type") == "income")
        expense = sum(1 for t in txns if t.get("type") == "expense")
        dates = [t["date"] for t in txns if "date" in t]
        try:
            file_size = os.path.getsize(self.data_file)
        except OSError:
            file_size = 0
        date_range = (min(dates), max(dates)) if dates else (None, None)
        return {
            "total_transactions": len(txns),
            "income_count": income,
            "expense_count": expense,
            "file_size": file_size,
            "date_range": date_range
        }
