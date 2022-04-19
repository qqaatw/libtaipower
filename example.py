from Taipower.api import TaipowerAPI

# Fill out your Jci Hitachi email address, password, and electric number.
ACCOUNT = "0987654321"
PASSWORD = "password"
ELECTRICNUMBER = "00xxxxxxxx"

def main():
    # Login
    api = TaipowerAPI(ACCOUNT, PASSWORD, ELECTRICNUMBER)
    api.login()

    # Check ami, ami bill, and bill records
    ami = api.meters[ELECTRICNUMBER].ami
    ami_bill = api.meters[ELECTRICNUMBER].ami_bill
    bill_records = api.meters[ELECTRICNUMBER].bill_records

    # Refresh status
    api.refresh_status()

if __name__ == "__main__":
    main()