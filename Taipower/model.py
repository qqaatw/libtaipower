from typing import Dict, Optional

class TaipowerAMI:
    """Taipower AMI.

    Parameters
    ----------
    ami : dict
        AMI.
    """

    def __init__(self, ami : dict):
        self._json : dict = ami
    
    @classmethod
    def from_amis(cls, ami_json : dict) -> Dict[str, object]:
        amis = {}
        for ami in ami_json["data"]["data"]:
            start_time = ami["startTime"]
            amis[start_time] = cls(ami)
        return amis

    @property
    def start_time(self) -> str:
        """Start time.

        Returns
        -------
        str
            In yyyymmddhhmmss format.
        """

        return self._json["startTime"]
    
    @property
    def end_time(self) -> str:
        """End time.

        Returns
        -------
        str
            In yyyymmddhhmmss format.
        """

        return self._json["endTime"]
    
    @property
    def is_missing_data(self) -> bool:
        """Whether or not the data is missing (unrecorded).

        Returns
        -------
        bool
            Return True if the data is missing.
        """

        return True if self._json["isMssingData"] == 1 else False
    
    @property
    def offpeak_kwh(self) -> Optional[float]:
        """Off-peak kw/h.

        Returns
        -------
        Optional[float]
            Off-peak kwh. Return None if the ami period is `quater`.
        """

        return self._json.get("offPeakKwh", None)
    
    @property
    def halfpeak_kwh(self) -> Optional[float]:
        """Half-peak kw/h.

        Returns
        -------
        Optional[float]
            Half-peak kwh. Return None if the ami period is `quater`.
        """

        return self._json.get("halfPeakKwh", None)

    @property
    def satpeak_kwh(self) -> Optional[float]:
        """Saturday half-peak kw/h.

        Returns
        -------
        Optional[float]
            Saturday half-peak kwh. Return None if the ami period is `quater`.
        """

        return self._json.get("satPeakKwh", None)

    @property
    def peak_kwh(self) -> Optional[float]:
        """Peak kw/h.

        Returns
        -------
        Optional[float]
            Peak kwh. Return None if the ami period is `quater`.
        """

        return self._json.get("peakTimeKwh", None)

    @property
    def total_kwh(self) -> Optional[float]:
        """Total kw/h.

        Returns
        -------
        Optional[float]
            Total kwh.
        """

        return self._json.get("totalKwh", self._json.get("kwh", None))


class TaipowerAMIBill:
    """Taipower AMI bill.

    Parameters
    ----------
    bill : dict
        Bill.
    """

    def __init__(self, bill : dict):
        self._json : dict = bill
    
    @property
    def bill_start_date(self) -> str:
        """Bill start date.

        Returns
        -------
        str
            In yyyy/mm format.
        """

        return f"{ str( 1911 + int(self._json['startDate'][0:3])) }{self._json['startDate'][3:]}"

    @property
    def bill_end_date(self) -> str:
        """Bill end date.

        Returns
        -------
        str
            In yyyy/mm format.
        """

        return f"{ str( 1911 + int(self._json['endDate'][0:3])) }{self._json['endDate'][3:]}"
    @property
    def current_amount(self) -> int:
        """Current amount.

        Returns
        -------
        int
            Current amount.
        """

        return self._json["currentAmount"]

    @property
    def kwh(self) -> int:
        """Kw/h.

        Returns
        -------
        int
            Kw/h.
        """

        return self._json["kwh"] if self._json["kwhData"] else -1
    
    @property
    def last_cycle_kwh(self) -> int:
        """Last cycle kw/h.

        Returns
        -------
        int
            Last cycle kw/h.
        """

        return self._json["theLast2Kwh"]
    
    @property
    def last_year_kwh(self) -> int:
        """The cycle in last year kw/h.

        Returns
        -------
        int
            The same cycle in last year kw/h.
        """

        return self._json["lastKwh"]


class TaipowerBillRecord:
    """Taipower bill record.

    Parameters
    ----------
    bill_record : dict
        Bill record.
    """

    def __init__(self, bill_record : dict):
        self._json : dict = bill_record
    
    @classmethod
    def from_bill_records(cls, bill_record_json : dict) -> Dict[str, object]:    
        records = {}
        for record in bill_record_json["data"]:
            issue_year_month = f"{str( 1911 + int(record['issueYM'][0:3]))}{record['issueYM'][3:]}" 
            records[issue_year_month] = cls(record)
        return records

    @property
    def charge(self) -> int:
        """The amount of the bill.

        Returns
        -------
        int
            The amount of the bill.
        """

        return int(self._json["totalCharge"].replace(",",""))
    
    @property
    def formula(self) -> str:
        """The formula of the bill.

        Returns
        -------
        str
            The formula of the bill.
        """

        return self._json["billFormula"]
    
    @property
    def kwh(self) -> int:
        """The kw/h consumed in the bill cycle.

        Returns
        -------
        int
            The kw/h consumed in the bill cycle.
        """

        return self._json["totalKwh"]
    
    @property
    def period(self) -> str:
        """The period of the bill cycle.

        Returns
        -------
        str
            In `yyy/mm/dd~yyy/mm/dd` (ROC calendar) format.
        """

        return self._json["billFromAndToDate"]
    
    @property
    def paid(self) -> bool:
        """Whether or not the bill is paid.

        Returns
        -------
        bool
            Return True if paid.
        """

        return True if self._json["hasPaid"] == "C" else False
