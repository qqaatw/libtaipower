from typing import Dict, Optional

class TaipowerAMI:
    def __init__(self, ami : dict):
        self._json = ami
    
    @classmethod
    def from_amis(cls, ami_json : dict) -> Dict[str, object]:
        amis = {}
        for ami in ami_json["data"]["data"]:
            start_time = ami["startTime"]
            amis[start_time] = cls(ami)
        return amis

    @property
    def start_time(self) -> str:
        return self._json["startTime"]
    
    @property
    def end_time(self) -> str:
        return self._json["endTime"]
    
    @property
    def is_missing_data(self) -> bool:
        return True if self._json["isMssingData"] == 1 else False
    
    @property
    def offpeak_kwh(self) -> Optional[float]:
        return self._json.get("offPeakKwh", None)
    
    @property
    def halfpeak_kwh(self) -> Optional[float]:
        return self._json.get("halfPeakKwh", None)

    @property
    def satpeak_kwh(self) -> Optional[float]:
        return self._json.get("satPeakKwh", None)

    @property
    def peak_kwh(self) -> Optional[float]:
        return self._json.get("peakTimeKwh", None)

    @property
    def total_kwh(self) -> Optional[float]:
        return self._json.get("totalKwh", self._json.get("kwh", None))


class TaipowerAMIBill:
    def __init__(self, bill : dict):
        self._json = bill
    
    @property
    def bill_start_date(self) -> str:
        return f"{ str( 1911 + int(self._json['startDate'][0:3])) }{self._json['startDate'][3:]}"

    @property
    def bill_end_date(self) -> str:
        return f"{ str( 1911 + int(self._json['endDate'][0:3])) }{self._json['endDate'][3:]}"
    @property
    def current_amount(self) -> int:
        return self._json["currentAmount"]

    @property
    def kwh(self) -> int:
        return self._json["kwh"] if self._json["kwhData"] else -1
    
    @property
    def last_cycle_kwh(self) -> int:
        return self._json["theLast2Kwh"]
    
    @property
    def last_year_kwh(self) -> int:
        return self._json["lastKwh"]
    

class TaipowerBillRecord:
    def __init__(self, bill_record : dict):
        self._json = bill_record
    
    @classmethod
    def from_bill_records(cls, bill_record_json : dict) -> Dict[str, object]:    
        records = {}
        for record in bill_record_json["data"]:
            issue_year_month = f"{str( 1911 + int(record['issueYM'][0:3]))}{record['issueYM'][3:]}" 
            records[issue_year_month] = cls(record)
        return records

    @property
    def charge(self) -> int:
        return int(self._json["totalCharge"].replace(",",""))
    
    @property
    def formula(self) -> str:
        return self._json["billFormula"]
    
    @property
    def kwh(self) -> int:
        return self._json["totalKwh"]
    
    @property
    def period(self) -> str:
        return self._json["billFromAndToDate"]
    
    @property
    def paid(self) -> bool:
        return True if self._json["hasPaid"] == "C" else False
