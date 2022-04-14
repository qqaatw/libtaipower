from typing import Dict

class TaipowerAMIBill:
    def __init__(self, bill : dict):
        self._bill = bill
    
    @property
    def bill_start_date(self) -> str:
        return f"{ str( 1911 + int(self._bill['startDate'][0:3])) }{self._bill['startDate'][3:]}"

    @property
    def bill_end_date(self) -> str:
        return f"{ str( 1911 + int(self._bill['endDate'][0:3])) }{self._bill['endDate'][3:]}"
    @property
    def current_amount(self) -> int:
        return self._bill["currentAmount"]

    @property
    def kwh(self) -> int:
        return self._bill["kwh"] if self._bill["kwhData"] else -1
    
    @property
    def last_cycle_kwh(self) -> int:
        return self._bill["theLast2Kwh"]
    
    @property
    def last_year_kwh(self) -> int:
        return self._bill["lastKwh"]
    

class TaipowerBillRecord:
    def __init__(self, bill_record : dict):
        self._bill_record = bill_record
    
    @classmethod
    def from_bill_records(cls, bill_record_json : dict) -> Dict[str, object]:    
        records = {}
        for record in bill_record_json["data"]:
            issue_year_month = f"{str( 1911 + int(record['issueYM'][0:3]))}{record['issueYM'][3:]}" 
            records[issue_year_month] = cls(record)
        return records

    @property
    def charge(self) -> int:
        return int(self._bill_record["totalCharge"].replace(",",""))
    
    @property
    def formula(self) -> str:
        return self._bill_record["billFormula"]
    
    @property
    def kwh(self) -> int:
        return self._bill_record["totalKwh"]
    
    @property
    def period(self) -> str:
        return self._bill_record["billFromAndToDate"]
    
    @property
    def paid(self) -> bool:
        return True if self._bill_record["hasPaid"] == "C" else False
    

    