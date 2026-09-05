# edit banking information in google sheets
import gspread
import csv
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


def fix_description(data:list[dict], index:int, curr_row:dict):
    '''fix transaction description by concatenating descriptions parts found on separate rows'''
    blank_row_count = 0 #skip of rows with blank DATES

    try:
        description_list = [curr_row["DESCRIPTION"]]
        next_row = data[index]
        while next_row["DATE"] == '': #if a row has no DATE then there must be a DESCRIPTION 
            description_list.append(str(next_row["DESCRIPTION"])) #some description fragments may be ints so convert to str
            index += 1
            blank_row_count += 1
            next_row = data[index]

        curr_row["DESCRIPTION"] = " ".join(description_list) #joins the DESCRIPTION fragments

        
    except IndexError:
        pass #if index goes out of bound -- do nothing

    return blank_row_count 
    


def modify_columns(row:dict):
    '''add and remove columns from row'''
    
    row["STATUS"] = "Posted"
    del row["Additions"]


def format_data(sheet:gspread.Worksheet) -> list[dict]:
    '''format data so it is inline with wells fargo csv download'''
    data = sheet.get_all_records()
    formatted_data = [] #append each row from data once it has been formatted

    i = 0
    row_count = len(data)
    while i < row_count:
        row = data[i]
       
        if row["DATE"] != "":
            row["DATE"] += "/2024"

            skip_rows = fix_description(data, i+1, row) #add one to i to indicate next row
            format_AMOUNT(row) 
            modify_columns(row)

            formatted_data.append(row)
            i += skip_rows

        i+=1
        
    return formatted_data


def create_csv(data_rows):
    '''create new csv file from rows of old csv'''
    fields = data_rows[0].keys() #get fields for csv

    with open("output.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data_rows)

def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    SHEET_ID = "1dsdO5bnxLvUWTrplAWhyn3J_bfheBb-slVSUNFjXmbA"  # google sheet ID
    sheet = client.open_by_key(SHEET_ID).sheet1

    formatted_data = format_data(sheet)
    create_csv(formatted_data)


if __name__ == "__main__":
    main()
