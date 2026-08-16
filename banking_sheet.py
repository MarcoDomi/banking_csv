# edit banking information in google sheets
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "intense-acumen-505422-k6-16d08f1e3b27.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def format_sheet(sheet):
    
    
    for data in sheet.get_all_records():
       if data['DATE'] != '':
           print(data['DATE'])


def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    SHEET_ID = "1QbJitEyPlr8LuJauisFQEwhNJHd8DGcSknpH_QT5Kds"
    sheet = client.open_by_key(SHEET_ID).sheet1

    row_count = len(sheet.get_all_records())
    col_count = len(sheet.get_all_records()[0])

    #format_sheet(sheet)
    print(len(sheet.get_all_records()[1]))
    

if __name__ == "__main__":
    main()
