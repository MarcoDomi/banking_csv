# edit banking information in google sheets
import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "intense-acumen-505422-k6-16d08f1e3b27.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def check_amt(amt):
    amt_list = amt.split('.')
    if len(amt_list) == 1:
        print(amt)
    elif len(amt_list[1]) < 2:
        print(amt)


def append_decimal(amount:str) -> str:
    'appends decimal and zeroes to amount if needed'

    amount_list = amount.split('.')
    if len(amount_list) == 1: #there is no decimal
        amount_list.append("00")
    elif len(amount_list[1]) == 1: #there is a decimal but only 1 digit after decimal
        amount_list[1] += '0'

    return ".".join(amount_list)


def format_AMOUNT(row:dict):
    '''change the value under AMOUNT column to match banking csv format'''

    if row["Additions"] != '':
        row["AMOUNT"] = row["Additions"] #if value present under Additions copy to a cell under AMOUNT
    else:
        row["AMOUNT"] *= -1
    
    row["AMOUNT"] = append_decimal(str(row["AMOUNT"]))
    check_amt(row["AMOUNT"])


def format_data(sheet) -> list[dict]:
    '''format data so it is inline with banking csv sheet'''
    data = sheet.get_all_records()

    for i in range(len(data)):
        row = data[i]

        if row["DATE"] != "":
            row["DATE"] += "/2024"
            format_AMOUNT(row)

            desc1 = row["DESCRIPTION"]
            desc2 = data[i+1]["DESCRIPTION"]
            row["DESCRIPTION"] = " ".join([desc1, desc2])

            row["STATUS"] = "Posted"
            row["CHECK #"] = ""
            del row["Additions"]


    return data


def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    SHEET_ID = "1QbJitEyPlr8LuJauisFQEwhNJHd8DGcSknpH_QT5Kds"
    sheet = client.open_by_key(SHEET_ID).sheet1

    formatted_data = format_data(sheet)
    print(formatted_data)


if __name__ == "__main__":
    main()
