import time
import datetime
import asyncio
import httpx
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

    def __init__(self, electric_meter_json) -> None:
        self._json : dict = electric_meter_json
        self._ami : Optional[Dict[str, model.TaipowerAMI]] = None
        self._ami_bill : Optional[model.TaipowerAMIBill] = None
        self._bill_records : Optional[Dict[str, model.TaipowerBillRecord]] = None
    
    def __repr__(self) -> str:
        ret = (
            f"name: {self.name}\n"
            f"number: {self.number}\n"
            f"main_addr: {self.main_addr}\n"
        )

        if self.nickname:
            ret += f"nickname: {self.nickname}"

        return ret
    
    @classmethod
    def from_electric_meter_list(
        cls,
        electric_meter_json : dict,
        electric_numbers : Optional[Union[List[str], str]] = None
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
    def ami(self) -> Optional[Dict[str, model.TaipowerAMI]]:
        return self._ami
    
    @ami.setter
    def ami(self, x : Dict[str, model.TaipowerAMI]):
        self._ami = x
    
    @property
    def ami_bill(self) -> Optional[model.TaipowerAMIBill]:
        return self._ami_bill
    
    @ami_bill.setter
    def ami_bill(self, x : model.TaipowerAMIBill):
        self._ami_bill = x
    
    @property
    def bill_records(self) -> Optional[Dict[str, model.TaipowerBillRecord]]:
        return self._bill_records
    
    @bill_records.setter
    def bill_records(self, x : Dict[str, model.TaipowerBillRecord]):
        self._bill_records = x

    @property
    def user_id(self) -> str:
        """The user id of the electric number.

        Returns
        -------
        str
            The user id of the electric number.
        """

        return str(self._json["userID"])

    @property
    def name(self) -> str:
        """The user name of the electric number.

        Returns
        -------
        str
            The user name of the electric number.
        """

        return self._json["electricName"]
    
    @property
    def nickname(self) -> Optional[str]:
        """The nickname of the electric number, which can be changed in the Taipower app.

        Returns
        -------
        Optional[str]
            The nickname, if not set in the app, None will be returned.
        """

        return self._json["nickname"] if len(self._json["nickname"]) != 0 else None
    
    @property
    def number(self) -> str:
        """Electric number.

        Returns
        -------
        str
            Electric number.
        """

        return self._json["electricNumber"]
    
    @property
    def type(self) -> str:
        """Electric meter type.

        Returns
        -------
        str
            `AMI` or `unknown`.
        """

        return "AMI" if self._json["ami"] == "true" else "unknown"
    
    @property
    def main_addr(self) -> str:
        """The main address of the electric number.

        Returns
        -------
        str
            The main address of the electric number.
        """

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
    ami_period : str, optional
        The retrieved AMI period. Available options: `quater`, `hour`, `daily`, `monthly`, by default `daily`.
    max_retries : int, optional
        Maximum number of retries when setting status, by default 5.
    print_response : bool, optional
        If set, all responses of httpx and MQTT will be printed, by default False.
    """

    def __init__(self, 
        account : str,
        password : str,
        electric_numbers : Optional[Union[List[str], str]] = None,
        ami_period : str = "daily",
        max_retries : int = 5,
        print_response : bool = False
    ) -> None:

        if ami_period not in ["quater", "hour", "daily", "monthly"]:
            raise ValueError("ami_period accepts either `quater`, `hour`, `daily`, `monthly`.")

        self.account : str = account
        self.password : str = password
        self.electric_numbers : Optional[Union[List[str], str]] = electric_numbers
        self.ami_period : str = ami_period
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
        # Reauthenticate 5 mins before TaipowerTokens expiration.
        current_time = time.time()
        if self._taipower_tokens.expiration - current_time <= 300:
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
        conn_status, conn_json = asyncio.run(conn.async_get_data())

        if conn_status == "OK":
            self._meters = TaipowerElectricMeter.from_electric_meter_list(
                conn_json,
                self.electric_numbers
            )
        else:
            raise RuntimeError(f"An error occurred when retrieving electric meters: {conn_status}")
        
        try:
            self.refresh_status() # suppress errors when login
        except:
            pass

    def reauth(self, use_refresh_token : bool = False) -> None:
        """Reauthenticate with Taipower API to retrieve new tokens.

        Parameters
        ----------
        use_refresh_token : bool, optional
            Whether or not to use refresh token, by default False

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """

        conn = connection.TaipowerConnection(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, self._taipower_tokens = conn.login(use_refresh_token=use_refresh_token)
        if conn_status != "OK":
            raise RuntimeError(f"An error occurred when reauthenticating with Taipower API: {conn_status}")
    
    def get_ami(self, electric_number : str, dt: datetime.datetime = None) -> Dict[str, model.TaipowerAMI]:
        """Get AMI.

        Parameters
        ----------
        electric_number : str
            Electric number.
        dt : datetime.datetime, optional
            The retrieved AMI date and time, by default None

        Returns
        -------
        Dict[str, model.TaipowerAMI]
            AMI.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """

        return asyncio.run(self.async_get_ami(electric_number, dt))

    async def async_get_ami(self, electric_number : str, dt: Optional[datetime.datetime] = None, client : Optional[httpx.AsyncClient] = None) -> Dict[str, model.TaipowerAMI]:
        """Asynchronously get AMI.

        Parameters
        ----------
        electric_number : str
            Electric number.
        dt : datetime.datetime, optional
            The retrieved AMI date and time. If None is given, current date and time will be used, by default None
        client : httpx.AsyncClient, optional
            AsyncClient for requests, by default None

        Returns
        -------
        Dict[str, model.TaipowerAMI]
            AMI.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """

        if dt is None:
            dt = datetime.datetime.now()
        
        conn = connection.GetAMI(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = await conn.async_get_data(self.ami_period, dt, electric_number, client=client)
        if conn_status == "OK":
            return model.TaipowerAMI.from_amis(conn_json)
        else:
            raise RuntimeError(f"An error occurred when retrieving AMI: {conn_status}")

    def get_ami_bill(self, electric_number : str) -> model.TaipowerAMIBill:
        """Get AMI bill.

        Parameters
        ----------
        electric_number : str
            Electric number.

        Returns
        -------
        model.TaipowerAMIBill
            AMI bill.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """

        return asyncio.run(self.async_get_ami_bill(electric_number))

    async def async_get_ami_bill(self, electric_number : str, client : httpx.AsyncClient = None) -> model.TaipowerAMIBill:
        """Asynchronously get AMI bill.

        Parameters
        ----------
        electric_number : str
            Electric number.
        client : httpx.AsyncClient, optional
            AsyncClient for requests, by default None

        Returns
        -------
        model.TaipowerAMIBill
            AMI bill.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """

        conn = connection.GetAMIBill(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = await conn.async_get_data(electric_number, client=client)

        if conn_status == "OK":
            return model.TaipowerAMIBill(conn_json["data"])
        else:
            raise RuntimeError(f"An error occurred when retrieving AMI bill: {conn_status}")

    def get_bill_records(self, electric_number : int) -> Dict[str, model.TaipowerBillRecord]:
        """Get bill records.

        Parameters
        ----------
        electric_number : str
            Electric number.

        Returns
        -------
        Dict[str, model.TaipowerBillRecord]
            Bill records.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """
        
        return asyncio.run(self.async_get_bill_records(electric_number))

    async def async_get_bill_records(self, electric_number : int, client : httpx.AsyncClient = None) -> Dict[str, model.TaipowerBillRecord]:
        """Asynchronously get bill records.

        Parameters
        ----------
        electric_number : str
            Electric number.
        client : httpx.AsyncClient, optional
            AsyncClient for requests, by default None

        Returns
        -------
        Dict[str, model.TaipowerBillRecord]
            Bill records.

        Raises
        ------
        RuntimeError
            If an error occurs, RuntimeError will be raised.
        """
        
        conn = connection.GetBillRecords(
            account=self.account,
            password=self.password,
            taipower_tokens=self._taipower_tokens,
            print_response=self.print_response,
        )
        conn_status, conn_json = await conn.async_get_data(electric_number, client=client)

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
        """Refresh status from Taipower API.

        Parameters
        ----------
        electric_number : str, optional
            Electric number. If None is given, all meters will be refreshed, by default None.
        refresh_ami : bool, optional
            Whether or not to refresh AMI, by default True
        refresh_ami_bill : bool, optional
            Whether or not to refresh AMI bill, by default True
        refresh_bill_records : bool, optional
            Whether or not to refresh bill records, by default True

        Raise
        -------
        RuntimeError
            If errors occur, a RuntimeError containing all errors will be raised.
        """

        self._check_before_publish()
        
        async def run(l):
            return await asyncio.gather(*l, return_exceptions=True)

        client = httpx.AsyncClient()
        async_functions = []
        return_storages = []
        errors = []

        for number, meter in self._meters.items():
            if electric_number and number != electric_number:
                continue
            if refresh_ami:
                async_functions.append(self.async_get_ami(number, client=client))
                return_storages.append((meter, "ami"))
            if refresh_ami_bill:
                async_functions.append(self.async_get_ami_bill(number, client=client))
                return_storages.append((meter, "ami_bill"))
            if refresh_bill_records:
                async_functions.append(self.async_get_bill_records(number, client=client))
                return_storages.append((meter, "bill_records"))

        list(
            map(
                lambda x, y: setattr(y[0], y[1], x) if not isinstance(x, Exception) else errors.append(x),
                asyncio.run(run(async_functions)),
                return_storages
            )
        )

        if len(errors) != 0:
            raise RuntimeError(errors)