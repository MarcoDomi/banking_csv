# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
from pathlib import Path
import sys
import wf_extractor
import csv

if len(sys.argv) < 2:
    print("ERROR: provide a absolute path to the directory containing the banking PDFs\nUsage: python3 pdf_handler.py <absolute path>")
    exit()

PDF_DIR = Path(sys.argv[1]) #NOTE: should i add a check to see if dir exists?


def get_dateYear(pdf_path:Path) -> str:
    '''retrieve the date and year from pdf text'''
    with pypdf.PdfReader(pdf_path) as pdf:
        page = pdf.pages[0]
        
        text_list = page.extract_text().splitlines()
        dateline = text_list[1]
        date = dateline.split(' ')

        month = date[0]
        year = date[2]

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
        
        month, year = get_dateYear(pdf_path)
        
        print(pdf_path.name)
        table = get_table(pdf_path) 
        
        if year not in table_dict:
            table_dict[year] = {}
        table_dict[year][month] = table #there should only be one pdf per month in a given year

    return table_dict


def create_csv(): 
    '''merge all pdfs in banking_pdfs into a single pdf'''
    table_dict = get_table_dict()

    pdf_years = list(table_dict.keys())
    pdf_years.sort()

    months = list(calendar.month_name)[1:] #slicing removes empty element 
    with open("test.csv",'w',newline='') as csvfile:
        bankwriter = csv.writer(csvfile)
        bankwriter.writerow(["Date", "Check Number", "Description", "Deposit/Credits", "Withdrawals/Debits"])
        for year in pdf_years:
            tables_in_year = table_dict[year]
            for month in months:
                try:
                    for row in tables_in_year[month]:
                        bankwriter.writerow(row)
                except KeyError:
                    next


if __name__ == "__main__":
    create_csv()
