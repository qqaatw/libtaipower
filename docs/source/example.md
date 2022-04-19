# Example

## API

1. Import API and define credential informaiton. 

    ```
    from Taipower.api import TaipowerAPI

    # Fill out your Jci Hitachi email address, password, and electric number.
    ACCOUNT = "0987654321"
    PASSWORD = "password"
    ELECTRICNUMBER = "00xxxxxxxx"
    ```

2. Login to API and get info.

    ```
    # Login
    api = TaipowerAPI(ACCOUNT, PASSWORD, ELECTRICNUMBER)
    api.login()

    # Check ami, ami bill, and bill records
    ami = api.meters[ELECTRICNUMBER].ami
    ami_bill = api.meters[ELECTRICNUMBER].ami_bill
    bill_records = api.meters[ELECTRICNUMBER].bill_records
    ```

4. Refresh status.
    
    ```
    # Check the updated device status
    api.refresh_status()
    ```

The python script can be found [here](https://github.com/qqaatw/libtaipower/blob/main/example.py).