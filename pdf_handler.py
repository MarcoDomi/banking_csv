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


def get_dateYear(pdf:pypdf.PdfReader) -> str:
    '''retrieve the date and year from pdf text'''
   
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

   
def get_csv_dict() -> dict:
    '''create dictionary using year/month for each pdf path'''
    csv_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        pdf = pypdf.PdfReader(pdf_path)
        month, year = get_dateYear(pdf)
        pdf.close()

        print(pdf_path.name)
        table = get_table(pdf_path) 
        
        if year not in csv_dict:
            csv_dict[year] = {}
        csv_dict[year][month] = table #there should only be one pdf per month in a given year

    return csv_dict


def merge_pdf(): 
    '''merge all pdfs in banking_pdfs into a single pdf'''

    csv_dict = get_csv_dict()

    print(csv_dict["2024"].keys())
    
    pdf_years = list(csv_dict.keys())
    pdf_years.sort()

   
    months = list(calendar.month_name)[1:] #slicing removes empty element 
    for year in pdf_years:
        for month in months:
            try:
                pass
            except KeyError:
                next

    


if __name__ == "__main__":
    merge_pdf()
