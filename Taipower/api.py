import time
import datetime
from typing import Optional, List, Union, Dict

from . import connection
from . import model


class TaipowerElectricMeter:
    """Taipower electric meter information.

    Parameters
    ----------
    electric_meter_json : dict
        Electric meter json of a specific meter.
    """

    def __init__(self, electric_meter_json):
        self._json : dict = electric_meter_json
        self._ami = None
        self._ami_bill = None
        self._bill_records = None
    
    def __repr__(self) -> str:
        ret = (
            f"name: {self.name}\n"
            f"number: {self.number}\n"
            f"ami: {self.ami}\n"
            f"main_addr: {self.main_addr}\n"
        )
        return ret
    
    @classmethod
    def from_electric_meter_list(
        cls,
        electric_meter_json : dict,
        electric_numbers : Optional[Union[List[str], str]]
    ) -> Dict[str, object]:
        """Use electric numbers to pick electric_meter_json accordingly.

        Parameters
        ----------
        electric_meter_json : dict
            electric_meter_json retrieved from connection.GetMember.
        electric_numbers : Optional[Union[List[str], str]]
            Electric numbers. If None is given, all ami enabled meters will be included, by default None.

        Returns
        -------
        dict
            A dict of TaipowerElectricMeter instances with electric number key.
        """

        electric_meters = {}

        if isinstance(electric_numbers, str):
            electric_numbers = [electric_numbers]
        
        for meter in electric_meter_json["data"]["electricList"]:
            electric_number = meter["electricNumber"]
            ami = True if meter["ami"] == "true" else False
            if ami and (electric_numbers is None or electric_number in electric_numbers):
                electric_meters[electric_number] = cls(meter)
        
        assert electric_numbers is None or len(electric_numbers) == len(electric_meters), \
            "Some of electric_numbers are not available from the API."
        
        return electric_meters
    
    @property
    def ami(self):
        return self._ami
    
    @ami.setter
    def ami(self, x):
        self._ami = x
    
    @property
    def ami_bill(self):
        return self._ami_bill
    
    @ami_bill.setter
    def ami_bill(self, x):
        self._ami_bill = x
    
    @property
    def bill_records(self):
        return self._bill_records
    
    @bill_records.setter
    def bill_records(self, x):
        self._bill_records = x
    

    @property
    def user_id(self) -> str:
        return self._json["userID"]

    @property
    def name(self) -> str:
        return self._json["electricName"]
    
    @property
    def number(self) -> str:
        return self._json["electricNumber"]
    
    @property
    def type(self) -> bool:
        return "AMI" if self._json["ami"] == "true" else "unknown"
    
    @property
    def main_addr(self) -> str:
        return self._json["electricAddr"]


class TaipowerAPI:
    """Taipower API.

    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    electric_numbers : list of str or str or None, optional
        Electric numbers. If None is given, all available AMI enabled electric meters will be included, by default None.
    max_retries : int, optional
        Maximum number of retries when setting status, by default 5.
    print_response : bool, optional
        If set, all responses of httpx and MQTT will be printed, by default False.
    """

    def __init__(self, 
        account : str,
        password : str,
        electric_numbers : Optional[Union[List[str], str]] = None,
        max_retries : int = 5,
        print_response : bool = False
    ) -> None:

        self.account : str = account
        self.password : str = password
        self.electric_numbers : Optional[Union[List[str], str]] = electric_numbers
        self.max_retries : int = max_retries
        self.print_response : bool = print_response

        self._meters : Dict[str, TaipowerElectricMeter] = {}
        self._taipower_tokens : Optional[connection.TaipowerTokens] = None
    
    @property
    def meters(self) -> Dict[str, TaipowerElectricMeter]:
        """Picked Taipower electric meters.

        Returns
        -------
        Dict[str, TaipowerElectricMeter]
            A dict of TaipowerElectricMeter instances.
        """
    
        return self._meters
    
    def _check_before_publish(self) -> None:
        # Reauthenticate 30 secs before TaipowerTokens expiration.
        current_time = time.time()
        if self._taipower_tokens.expiration - current_time <= 30:
            self.reauth()
    
    def login(self) -> None:
        """Login API.

        Raises
        ------
        RuntimeError
            If a login error occurs, RuntimeError will be raised.
        """

        conn = connection.GetMember(
            account=self.account,
            password=self.password,
            print_response=self.print_response,
        )
        self._taipower_tokens = conn._taipower_tokens
        conn_status, conn_json = conn.get_data()

        if conn_status == "OK":
            self._meters = TaipowerElectricMeter.from_electric_meter_list(
                conn_json,
                self.electric_numbers
            )
        else:
            raise RuntimeError(f"An error occurred when retrieving electric meters: {conn_status}")

    def reauth(self, use_refresh_token : bool = False) -> None:
        conn = connection.TaipowerConnection(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, self._aws_tokens = conn.login(use_refresh_token=use_refresh_token)
        if conn_status != "OK":
            raise RuntimeError(f"An error occurred when reauthenticating with Taipower API: {conn_status}")
    
    def get_hour_ami(self, electric_number : str, year : Optional[int] = None, month : Optional[int] = None, day : Optional[int] = None) -> dict:
        dt = datetime.datetime.now()
        dt.year = year if year is not None else dt.year
        dt.month = month if month is not None else dt.month
        dt.day = day if day is not None else dt.day
        
        conn = connection.GetAMI(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = conn.get_data("hour", dt, electric_number)
        if conn_status == "OK":
            return conn_json
        else:
            raise RuntimeError(f"An error occurred when retrieving AMI: {conn_status}")

    def get_ami_bill(self, electric_number : str) -> model.TaipowerAMIBill:
        conn = connection.GetAMIBill(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = conn.get_data(electric_number)

        if conn_status == "OK":
            return model.TaipowerAMIBill(conn_json)
        else:
            raise RuntimeError(f"An error occurred when retrieving AMI bill: {conn_status}")

    def get_bill_records(self, electric_number : int) -> Dict[str, model.TaipowerBillRecord]:
        conn = connection.GetBillRecords(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = conn.get_data(electric_number)

        if conn_status == "OK":
            return model.TaipowerBillRecord.from_bill_records(conn_json)
        else:
            raise RuntimeError(f"An error occurred when retrieving bill records: {conn_status}")

    def refresh_status(self, 
        electric_number : str = None,
        refresh_ami : bool = True,
        refresh_ami_bill : bool = True,
        refresh_bill_records : bool = True,
    ):

        self._check_before_publish()

        for number, meter in self._meters.items():
            if electric_number and number != electric_number:
                continue
            
            if refresh_ami:
                meter.ami = self.get_hour_ami(number)
            elif refresh_ami_bill:
                meter.ami_bill = self.get_ami_bill(number)
            elif refresh_bill_records:
                meter.bill_records = self.get_bill_records(number)
    
    def get_status(self, electric_number : str = None):
        statuses = {}
        for number, meter in self._meters.items():
            if electric_number and number != electric_number:
                continue
            statuses[number] = meter.ami_bill
        return statuses
        
            
