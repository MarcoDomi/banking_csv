# edit banking information in google sheets
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "intense-acumen-505422-k6-16d08f1e3b27.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def update_AMOUNT(row):
    '''change the value under AMOUNT column to match banking csv format'''
    if row["Additions"] != '':
        row["AMOUNT"] = row["Additions"]
    else:
        row["AMOUNT"] *= -1

    


def format_data(sheet):
    '''format data so it is inline with banking csv sheet'''
    data = sheet.get_all_records()

    for row in data:
        if row["DATE"] != "":
            row["DATE"] += "/2024"
            update_AMOUNT(row)
            
        else:
            pass
            # move description to previous row
        

def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    SHEET_ID = "1QbJitEyPlr8LuJauisFQEwhNJHd8DGcSknpH_QT5Kds"
    sheet = client.open_by_key(SHEET_ID).sheet1

    format_data(sheet)


if __name__ == "__main__":
    main()
