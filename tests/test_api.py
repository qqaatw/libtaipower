import pytest
import time
import json
import httpx

import datetime

from unittest.mock import patch, MagicMock

from Taipower.api import TaipowerAPI, TaipowerElectricMeter
from Taipower.model import TaipowerAMI, TaipowerAMIBill, TaipowerBillRecord
from Taipower.connection import TaipowerTokens

from . import MOCK_ELECTRIC_NUMBER


@pytest.fixture()
def fixture_mock_meter():
    meter = TaipowerElectricMeter(
        json.loads(f"""{{
            "userID": 123456,
            "electricNumber": "{MOCK_ELECTRIC_NUMBER}",
            "electricName": "ABC",
            "idNumber": "",
            "idNumberSha": "",
            "employerId": "",
            "nickname": "a nick name",
            "verifiedType": "",
            "billPrint": "true",
            "engBill": "false",
            "billPrintStatus": "0",
            "applyStatus": "0",
            "applyStatusText": "",
            "applyNo": "",
            "ami": "true",
            "orderEdc": "false",
            "status": "0",
            "outageId": "A",
            "notifyLimit": "",
            "startDatetime": "",
            "updateDatetime": "2022-04-01T05:50:21.810+0000",
            "electricAddr": "Taipei City",
            "electricAddr1": "",
            "electricAddr2": "",
            "electricAddr3": "",
            "electricAddr4": "",
            "createDatetime": "2022-04-05T05:50:55.523+0000",
            "bindDatetime": "2022-04-05T05:50:55.523+0000",
            "billCycle": "01",
            "billDate": "",
            "authorizeCount": "0",
            "empElectric": "false",
            "hasUpdate": "false",
            "verifiedLevel": "0",
            "billPrintStatusText": "123"
        }}""")
    )
    meter.ami = {
        "20220412000000" : TaipowerAMI(
            json.loads("""{
                "startTime": "20220403000000",
                "endTime": "20220404000000",
                "isMssingData": 0,
                "offPeakKwh": 25.2,
                "halfPeakKwh": 0.0,
                "satPeakKwh": 0.0,
                "peakTimeKwh": 0.0,
                "totalKwh": 23.2,
                "mult": 1
            }""")
        )
    }
    meter.ami_bill = TaipowerAMIBill(
        json.loads(
            """{"kwhData": true,
            "status": "zt",
            "totalAmount": 4695,
            "kwh": 1383,
            "comparisonOfLastYear": "+51%",
            "comparisonOfLastMonth": "-22%",
            "outageId": "A",
            "chkCode": "478",
            "payMethod": "",
            "lastKwh": 918,
            "theLast2Kwh": 1776,
            "startDate": "1110121",
            "startDateText": "1110121",
            "endDate": "1110323",
            "endDateText": "111/03/23",
            "payDueDate": "1110426",
            "payDueDateText": "111/04/26",
            "period": "111/01/21 ~ 111/03/23",
            "totalAmountText": "4,695",
            "chargeDate": "1110406",
            "chargeDateText": "11104",
            "lastTotalAmount": 2618,
            "currentAmount": 3765,
            "currentAmountText": "4,695",
            "rtncode": "0",
            "rtnmsg": "",
            "collName": "coll name",
            "collDate": "1100322",
            "collDateText": "110/03/22",
            "chargeInfo": "charge info",
            "recvDate": "",
            "hasPaid": "B"
            }"""
        )
    )
    meter.bill_records = {
        "2020/08" : TaipowerBillRecord(
            json.loads("""{
                "issueYM": "109/08",
                "ctrClassType": "\u8868\u71c8\u975e\u71df\u696d\u7528",
                "billFromAndToDate": "109/05/27~109/07/26",
                "totalKwh": 1374,
                "collDate": "1090825",
                "collName": "\u7e73\u8cbb/\u92b7\u5e33\u65e5\u671f",
                "totalCharge": "4,329",
                "billFormula": "1.63x240(56/61)+2.38x420(56/61)+3.52x340(56/61)+4.80x374(56/61)+1.63x240(5/61)+2.10x420(5/61)+2.89x340(5/61)+3.94x374(5/61)",
                "floatFields": [
                    "\u6d41\u52d5\u96fb\u8cbb:4329.2\u5143",
                    "\u61c9\u7e73\u7e3d\u91d1\u984d:4329\u5143"
                ],
                "outageId": "A",
                "chkCode": "252",
                "payMethod": "免費",
                "hasPaid": "C",
                "curReadMtrDate": "1090727",
                "nextReadMtrDate": "1090924",
                "recvDate": "1090825"
            }""")
        )
    }
    return meter

@pytest.fixture()
def fixture_mock_api(fixture_mock_meter):
    api = TaipowerAPI("", "")
    api._taipower_tokens = TaipowerTokens("", "", time.time() + 3600)
    api._meters = {
        MOCK_ELECTRIC_NUMBER: fixture_mock_meter,
    }
    return api


class TestTaipowerAPI:
    def test_login(self, fixture_mock_api, fixture_mock_meter):
        api = fixture_mock_api
        meter = fixture_mock_meter
        with patch("Taipower.connection.GetMember.async_get_data") as mock_get_data, \
            patch("Taipower.connection.GetMember.login") as mock_login, \
            patch.object(api, "refresh_status") as mock_refresh_status:
            async def mock(client=None):
                assert client is None or isinstance(client, httpx.AsyncClient)
                return_value = {
                    "success": True,
                    "code": 1,
                    "message": "123",
                    "data": {
                        "electricList": [
                            meter._json
                        ]
                    }
                }
                return "OK", return_value

            async def mock_failed(client=None):
                return "Not OK", {}

            mock_login.return_value = ("OK", "")
            mock_get_data.side_effect = mock
            api.login()

            assert isinstance(api.meters, dict)
            assert isinstance(api.meters[MOCK_ELECTRIC_NUMBER], TaipowerElectricMeter)

            mock_get_data.side_effect = mock_failed

            with pytest.raises(RuntimeError, match=f"An error occurred when retrieving electric meters: Not OK"):
                api.login()

    def test_get_ami(self, fixture_mock_api):
        api = fixture_mock_api
        with patch("Taipower.connection.GetAMI.async_get_data") as mock_get_data:

            async def mock(time_period, dt, electric_number, client=None):
                assert time_period == "daily"
                assert dt is None or isinstance(dt, datetime.datetime)
                assert electric_number == MOCK_ELECTRIC_NUMBER
                assert client is None or isinstance(client, httpx.AsyncClient)
                return_value = {
                    "success": True,
                    "code": 1,
                    "message": "123",
                    "data": {
                        "custNo": None,
                        "tags": [
                        1,
                        3,
                        4
                        ],
                        "mult": 1,
                        "totalKwh": None,
                        "data": [{
                            "startTime": "20220403000000",
                            "endTime": "20220404000000",
                            "isMssingData": 0,
                            "offPeakKwh": 25.2,
                            "halfPeakKwh": 0.0,
                            "satPeakKwh": 0.0,
                            "peakTimeKwh": 0.0,
                            "totalKwh": 23.2,
                            "mult": 1
                        }]
                    }
                }

                return "OK", return_value
            
            async def mock_failed(time_period, dt, electric_number, client=None):
                return "Not OK", {}
            
            mock_get_data.side_effect = mock
            ami = api.get_ami(MOCK_ELECTRIC_NUMBER)

            assert isinstance(ami, dict)
            assert isinstance(ami["20220403000000"], TaipowerAMI)

            mock_get_data.side_effect = mock_failed

            with pytest.raises(RuntimeError, match=f"An error occurred when retrieving AMI: Not OK"):
                api.get_ami(MOCK_ELECTRIC_NUMBER)
    
    def test_get_ami_bill(self, fixture_mock_api, fixture_mock_meter):
        api = fixture_mock_api
        meter = fixture_mock_meter
        with patch("Taipower.connection.GetAMIBill.async_get_data") as mock_get_data:
            async def mock(electric_number, client=None):
                assert electric_number == MOCK_ELECTRIC_NUMBER
                assert client is None or isinstance(client, httpx.AsyncClient)
                return_value = {
                    "success": True,
                    "code": 1,
                    "message": "123",
                    "data": [
                        meter.ami_bill._json                        
                    ]
                }

                return "OK", return_value
            
            async def mock_failed(electric_number, client=None):
                return "Not OK", {}
            
            mock_get_data.side_effect = mock
            ami_bill = api.get_ami_bill(MOCK_ELECTRIC_NUMBER)

            assert isinstance(ami_bill, TaipowerAMIBill)

            mock_get_data.side_effect = mock_failed

            with pytest.raises(RuntimeError, match=f"An error occurred when retrieving AMI bill: Not OK"):
                api.get_ami_bill(MOCK_ELECTRIC_NUMBER)
    
    def test_get_bill_records(self, fixture_mock_api, fixture_mock_meter):
        api = fixture_mock_api
        meter = fixture_mock_meter
        with patch("Taipower.connection.GetBillRecords.async_get_data") as mock_get_data:
            async def mock(electric_number, client=None):
                assert electric_number == MOCK_ELECTRIC_NUMBER
                assert client is None or isinstance(client, httpx.AsyncClient)
                return_value = {
                    "success": True,
                    "code": 1,
                    "message": "123",
                    "data": [meter.bill_records["2020/08"]._json],
                }

                return "OK", return_value
            
            async def mock_failed(electric_number, client=None):
                return "Not OK", {}
            
            mock_get_data.side_effect = mock
            bill_records = api.get_bill_records(MOCK_ELECTRIC_NUMBER)

            assert isinstance(bill_records, dict)
            assert isinstance(bill_records["2020/08"], TaipowerBillRecord)

            mock_get_data.side_effect = mock_failed

            with pytest.raises(RuntimeError, match=f"An error occurred when retrieving bill records: Not OK"):
                api.get_bill_records(MOCK_ELECTRIC_NUMBER)

    def test_refresh_status(self, fixture_mock_api):
        api = fixture_mock_api
        with patch.object(api, "async_get_ami") as mock_get_ami, \
             patch.object(api, "async_get_ami_bill") as mock_get_ami_bill, \
             patch.object(api, "async_get_bill_records") as mock_get_bill_records:
            
            async def mock(*args, **kwargs):
                return "Mock Object"
            async def mock_exception(*args, **kwargs):
                raise RuntimeError()
            
            mock_get_ami.side_effect = mock
            mock_get_ami_bill.side_effect = mock
            mock_get_bill_records.side_effect = mock

            api.refresh_status()

            assert api.meters[MOCK_ELECTRIC_NUMBER].ami == "Mock Object"
            assert api.meters[MOCK_ELECTRIC_NUMBER].ami_bill == "Mock Object"
            assert api.meters[MOCK_ELECTRIC_NUMBER].bill_records == "Mock Object"

            mock_get_ami.side_effect = mock_exception
            mock_get_ami_bill.side_effect = mock_exception
            mock_get_bill_records.side_effect = mock_exception

            with pytest.raises(RuntimeError, match=f"[RuntimeError(), RuntimeError(), RuntimeError()]"):
                api.refresh_status()


class TestTaipowerElectricMeter:
    def test_repr(self, fixture_mock_meter):
        meter = fixture_mock_meter
        assert meter.__repr__() == f"""name: ABC
number: {MOCK_ELECTRIC_NUMBER}
main_addr: Taipei City
nickname: a nick name"""
    
    def test_attrs(self, fixture_mock_meter):
        meter = fixture_mock_meter
        attrs = [
            ("ami", dict),
            ("ami_bill", TaipowerAMIBill),
            ("bill_records", dict),
            ("user_id", str),
            ("name", str),
            ("nickname", str),
            ("number", str),
            ("type", str),
            ("main_addr", str),
        ]

        for attr_name, attr_type in attrs:
            assert type(getattr(meter, attr_name)) == attr_type, attr_name

    def test_from_electric_meter_list(self, fixture_mock_meter):
        # without specifying electric numbers
        meter = fixture_mock_meter
        
        meters = TaipowerElectricMeter.from_electric_meter_list(
            {"data": {"electricList": [meter._json]}}
        )

        assert meters[MOCK_ELECTRIC_NUMBER]._json == meter._json
