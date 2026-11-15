# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
import re
import sys
import wf_extractor
import csv
from pathlib import Path

options = ["--alt_output", "-alt"]
usage = f"\nUsage: python3 pdf_handler.py [OPTION] <DIR absolute path>"

if len(sys.argv) == 2:
    if not Path(sys.argv[1]).exists():
        raise Exception(f"Error: provide a valid absolute path to directory containing banking PDFs{usage}")
    path_index = 1
    option_bool = False

elif len(sys.argv) == 3:
    if not sys.argv[1] in options:
        raise Exception(f"Error: invalid option{usage}")
    if not Path(sys.argv[2]).exists():
        raise Exception(f"Error: provide a valid absolute path to directory containing banking PDFs{usage}")
    path_index = 2
    option_bool = True
else:
    raise Exception(f"ERROR: invalid number of arguments{usage}")


PDF_DIR = Path(sys.argv[path_index]) #NOTE: should i add a check to see if dir exists?
ALT_OUTPUT = option_bool


def get_monthYear(pdf_path:Path) -> str:
    '''retrieve the month and year from pdf text'''

    with pypdf.PdfReader(pdf_path) as pdf:
        page = pdf.pages[0]

        page_text = page.extract_text()
        date_re = re.compile(r"[A-Z][a-z]{2,} \d{1,2}, \d{4}")
        date = date_re.search(page_text).group()
        date_split = date.split()

        month = date_split[0]
        year = date_split[2]
        
    return month, year


def get_table(pdf_path:str):
    '''create a csv for for a banking transaction pdf'''

    wf1 = wf_extractor.wells_fargo_extractor(pdf_path)
    table = wf1.extract_tables()

    return table


def get_table_dict() -> dict:
    '''create dictionary using year/month for each pdf path'''
    table_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        if pdf_path.suffix != ".pdf":
            continue
        
        month, year = get_monthYear(pdf_path)
        
        print(pdf_path.name)
        table = get_table(pdf_path) 
        
        if year not in table_dict:
            table_dict[year] = {}
        table_dict[year][month] = table #there should only be one pdf per month in a given year

    return table_dict


def csv_writer1(csvfile, table_years:list, table_dict:dict):
    '''option 1 for creating the banking transaction csv file'''
    months = list(calendar.month_name)[1:] #slicing removes empty element

    bankwriter = csv.writer(csvfile)
    bankwriter.writerow(["Date", "Check Number", "Description", "Deposit/Credits", "Withdrawals/Debits"])
    for year in table_years:
        tables_in_year = table_dict[year]
        for month in months:
            try:
                for row in tables_in_year[month]:
                    row[0] += f"/{year}"
                    bankwriter.writerow(row)
            except KeyError:
                next


def process_row(row:list, year:int) -> dict:
    """convert row to dictionary and edit row values"""

    headers = ["DATE", "CHECK #", "DESCRIPTION", "AMOUNT", "WITHDRAW"]
    row_dict = dict(zip(headers, row))

    row_dict["DATE"] += "/" + year
    if row_dict["AMOUNT"] == '':
        row_dict["AMOUNT"] = '-' + row_dict["WITHDRAW"]
    del row_dict["WITHDRAW"]

    return row_dict


def alt_csv_writer(csvfile, table_years:list[str], table_dict:dict):
    months = list(calendar.month_name)[1:]

    ordered_fields = ["DATE", "DESCRIPTION", "AMOUNT", "CHECK #"]
    bankwriter = csv.DictWriter(csvfile, fieldnames=ordered_fields)
    bankwriter.writeheader()

    for year in table_years:
        tables_in_year = table_dict[year]
        for month in months:
            try: 
                for row in tables_in_year[month]:
                    row_dict = process_row(row, year)
                    bankwriter.writerow(row_dict)
            except KeyError:
                next


def csv_conversion(): 
    '''converts all banking pdfs into a single csv file'''
    table_dict = get_table_dict()

    table_years = list(table_dict.keys())
    table_years.sort()

    with open(PDF_DIR / "banking_transaction.csv",'w',newline='') as csvfile:
        if not ALT_OUTPUT:
            csv_writer1(csvfile, table_years, table_dict)
        else:
            alt_csv_writer(csvfile, table_years, table_dict)


if __name__ == "__main__":
    csv_conversion()
