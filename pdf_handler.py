# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
from pathlib import Path
import sys

if len(sys.argv) < 2:
    print("ERROR: provide a absolute path directory containing banking PDFs\nUsage: python3 pdf_handler.py <absolute path>")
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


def get_last_page(pdf:pypdf.PdfReader):
    '''returns the last page in pdf that has bank transaction table'''
    pass


def get_pdf_dict():
    '''get dictionary that using year/month for each pdf path'''
    pdf_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        pdf = pypdf.PdfReader(pdf_path)
        
        month, year = get_dateYear(pdf_path)
        #TODO get last page that has table
        if year not in pdf_dict:
            pdf_dict[year] = {}

        pdf_dict[year][month] = pdf_path #there should only be one pdf per month in a given year

    return pdf_dict


def merge_pdf(): 
    '''merge all pdfs in banking_pdfs into a single pdf'''
    second_page = 1 #start at second page
    last_pages = 2 #remove last 2 pages

    pdf_dict = get_pdf_dict()
    
    pdf_years = list(pdf_dict.keys())
    pdf_years.sort()

    merger = pypdf.PdfWriter()
    for year in pdf_years:
        months = list(calendar.month_name)[1:] #slicing removes empty element 
        for month in months:
            try:
                pdf_path = pdf_dict[year][month]
                reader = pypdf.PdfReader(pdf_path)

                page_count = len(reader.pages)
                merger.append(reader, pages=(second_page, page_count - last_pages))
            except KeyError:
                next

    merger.write("merged.pdf")


if __name__ == "__main__":
    merge_pdf()