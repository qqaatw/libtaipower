import uuid
import json
import logging
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime

import httpx
from . import utility

ENDPOINT = "mapp-2019.taipower.com.tw"
BASIC_AUTH = "dHBlYy13U1pvLTVDNjZTZG84ZzM6X1UyVlpZd05kWi1hTW9ILV9fZlctZ3ROR0lwVmgydy4="
APP_VERSION = "3.0.6"

_LOGGER = logging.getLogger(__name__)


@dataclass
class TaipowerTokens:
    access_token: str
    refresh_token: str
    expiration: float


class TaipowerConnection:
    """Connecting to Taipower API.

    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    taipower_tokens : TaipowerTokens, optional
        If taipower_tokens is given, it is used by request;
        otherwise, a login procedure is performed to obtain new taipower_tokens,
        by default None.
    proxy : str, optional
        Proxy setting. Format:"IP:port", by default None. 
    print_response : bool, optional
        If set, all responses of httpx will be printed, by default False.
    """

    def __init__(self, account, password, taipower_tokens=None, proxy=None, print_response=False):
        self._login_response = None
        self._account = account
        self._password = password
        self._print_response = print_response
        self._proxies = {'http': proxy, 'https': proxy} if proxy else None

        if taipower_tokens:
            self._taipower_tokens = taipower_tokens
        else:
            conn_status, self._taipower_tokens = self.login()
            if conn_status != "OK":
                raise RuntimeError(f"An error occurred when signing into Taipower API: {conn_status}")

    def _generate_headers(self, token_type="bearer"):
        auth = f"Bearer {self._taipower_tokens.access_token}" if token_type == "bearer" else f"Basic {BASIC_AUTH}"
        headers = {
            "Accept": "*",
            "Authorization": auth,
            "User-Agent": "Mozilla/5.0 ( compatible )"
        }
        return headers
    
    def _handle_response(self, response):
        response_json = response.json()
        
        if response.status_code == httpx.codes.ok:
            if "success" in response_json and "message" in response_json:
                if response_json["success"] == True:
                    return "OK", response_json
                else:
                    return response_json["message"], response_json
            else:
                return "OK", response_json
        elif "error" in response_json:
            if "error_description" in response_json:
                return f"{response_json['error_description']}", response_json
            else:
                return f"{response_json['error']}", response_json
        else:
            return "Unknown error", response_json
    
    def _send(self, api_name, **kwargs):
        with httpx.Client(proxies=self._proxies) as c:
            headers = kwargs.pop("headers") if "headers" in kwargs else self._generate_headers()
            req = c.post(
                f"https://{ENDPOINT}/{api_name}",
                headers=headers,
                **kwargs,
            )
        if self._print_response:
            self.print_response(req)

        message, response_json = self._handle_response(req)

        return message, response_json

    async def _async_send(self, api_name, client=None, **kwargs):
        c = httpx.AsyncClient(proxies=self._proxies) if client is None else client
        headers = kwargs.pop("headers") if "headers" in kwargs else self._generate_headers()
        req = await c.post(
            f"https://{ENDPOINT}/{api_name}",
            headers=headers,
            **kwargs,
        )
        if client is None:
            await c.aclose()
        
        if self._print_response:
            self.print_response(req)

        message, response_json = self._handle_response(req)

        return message, response_json

    def login(self, use_refresh_token=False):
        """Login API.

        Parameters
        ----------
        use_refresh_token : bool, optional
            Whether or not to use TaipowerTokens.refresh_token to login. 
            If TaipowerTokens is not provided, fallback to email and password, by default False

        Returns
        -------
        (str, TaipowerTokens)
            (status, Taipower tokens).
        """

        if use_refresh_token and self._taipower_tokens != None:
            login_json_data = {
                "refresh_token": self._taipower_tokens.refresh_token,
                "grant_type": "refresh_token",
            }
        else:
            login_json_data = {
                "username": self._account,
                "password": utility.des_encrypt(self._password),
                "grant_type": "password",
                "scope": "tpec",
                "device_id": str(uuid.uuid4()),
                "appVersion": APP_VERSION,
            }
        
        login_headers = self._generate_headers(token_type="basic")

        status, response = asyncio.run(self._async_send("oauth/token", data=login_json_data, headers=login_headers))

        taipower_tokens = None
        if status == "OK" and response["token_type"] == "bearer":
            taipower_tokens = TaipowerTokens(
                access_token = response['access_token'],
                refresh_token = self._taipower_tokens.refresh_token if use_refresh_token else response['refresh_token'],
                expiration = time.time() + response['expires_in'],
            )
        return status, taipower_tokens
    
    def get_data(self, *args, **kwargs):
        return self._send(self.api_name, json=self.setup_payload(*args, **kwargs))
    
    async def async_get_data(self, *args, client=None, **kwargs):
        return await self._async_send(self.api_name, json=self.setup_payload(*args, **kwargs), client=client)

    def setup_payload(self):
        return None

    def print_response(self, response):
        print('===================================================')
        print(self.__class__.__name__, 'Response:')
        print('headers:', response.headers)
        print('status_code:', response.status_code)
        print('text:', json.dumps(response.json(), indent=True))
        print('===================================================')


class CheckToken(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    api_name = "oauth/check_token"

    def __init__(self, account, password, **kwargs):
        super().__init__(account, password, **kwargs)

    def setup_payload(self, access_token : str):
        json_data = {
            "token": access_token,
        }
        return json_data
    
    def get_data(self, access_token: str):
        headers = self._generate_headers("basic")
        return self._send(self.api_name, data=self.setup_payload(access_token), headers=headers)

    async def async_get_data(self, access_token: str, client: httpx.AsyncClient = None):
        headers = self._generate_headers("basic")
        return await self._async_send(self.api_name, json=self.setup_payload(access_token), headers=headers, client=client)


class GetMember(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    api_name = "member/getData"

    def __init__(self, account, password, **kwargs):
        super().__init__(account, password, **kwargs)

class GetAMIBill(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    api_name = "api/home/bills"
    
    def setup_payload(self, electric_number):
        json_data = {
            "phoneNo": self._account,
            "deviceId": "",
            "customNo": electric_number,
        }
        return json_data
    
    def get_data(self, electric_number: str):
        return super().get_data(electric_number)

    async def async_get_data(self, electric_number: str, client: httpx.AsyncClient = None):
        return await super().async_get_data(electric_number, client=client)


class GetAMIPowerRate(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    api_name = "api/trial/power-rate"

    def __init__(self, account, password, **kwargs):
        super().__init__(account, password, **kwargs)


class GetAMI(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    def __init__(self, account, password, **kwargs):
        super().__init__(account, password, **kwargs)
    
    def setup_payload(self, time_period: str, datetime: datetime, electric_number: str):
        if time_period == "hour":
            time_text = "date"
            time_rep = datetime.strftime("%Y%m%d") # YYYYMMDD
        elif time_period == "daily":
            time_text = "yearMonth"
            time_rep = datetime.strftime("%Y%m") # YYYYMM
        elif time_period == "monthly":
            time_text = "year"
            time_rep = datetime.strftime("%Y") # YYYY
        elif time_period == "quater":
            time_text = "date"
            time_rep = datetime.strftime("%Y%m%d") # YYYYMMDD
        else:
            raise ValueError("time_period accepts either `hour`, `daily`, `monthly`, or `quater`.")

        json_data = {
            "custNo": electric_number,
            time_text: time_rep
        }
        return json_data
    
    def get_data(self, time_period: str, datetime: datetime, electric_number: str):
        return self._send(f"api/ami/{time_period}", json=self.setup_payload(time_period, datetime, electric_number))
    
    async def async_get_data(self, time_period: str, datetime: datetime, electric_number: str, client : httpx.AsyncClient = None):
        return await self._async_send(f"api/ami/{time_period}", json=self.setup_payload(time_period, datetime, electric_number), client=client)

class GetBillRecords(TaipowerConnection):
    """API internal endpoint.
    
    Parameters
    ----------
    account : str
        User phone number.
    password : str
        User password.
    """

    api_name = "api/mybill/records"

    def __init__(self, account, password, **kwargs):
        super().__init__(account, password, **kwargs)
    
    def setup_payload(self, electric_number : str):
        json_data = {
            "customNo": electric_number,
        }
        return json_data
    
    def get_data(self, electric_number: str):
        return super().get_data(electric_number)

    async def async_get_data(self, electric_number: str, client: httpx.AsyncClient = None):
        return await super().async_get_data(electric_number, client=client)