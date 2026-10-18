# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
import pdfplumber
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


def get_last_page(pdf:pypdf.PdfReader) -> int:
    '''returns the last page in pdf that has bank transaction table'''
    page_count = len(pdf.pages)
    for i in range(page_count-1, -1, -1):
        page = pdf.pages[i]
        if "Transaction history (continued)" in page.extract_text():
            return i + 1 #convert from index to page number


def read_tables(tables):
    for table in tables:
        for row in table:
            print(row)
    exit()


# NOTE i am trying to see if i can pull tables from a PdfReader object
def create_csv(pdf_path:str, last_table:int):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[1]
        table_list = page.extract_tables({"vertical_strategy":"text", "horizontal_strategy":"lines", "min_words_vertical":7}) #NOTE i dont understand table settings
        
        


def get_pdf_dict() -> dict:
    '''get dictionary using year/month for each pdf path'''
    pdf_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        pdf = pypdf.PdfReader(pdf_path)
        month, year = get_dateYear(pdf)
        final_page = get_last_page(pdf)
        pdf.close()

        create_csv(pdf_path, final_page) #NOTE i should pass the pdf path instead


        if year not in pdf_dict:
            pdf_dict[year] = {}
        pdf_dict[year][month] = (pdf_path, final_page) #there should only be one pdf per month in a given year

    return pdf_dict


def merge_pdf(): 
    '''merge all pdfs in banking_pdfs into a single pdf'''
    second_page = 1 #start at second page

    pdf_dict = get_pdf_dict()
    
    # pdf_years = list(pdf_dict.keys())
    # pdf_years.sort()

    # merger = pypdf.PdfWriter()
    # months = list(calendar.month_name)[1:] #slicing removes empty element 
    # for year in pdf_years:
    #     for month in months:
    #         try:
    #             pdf_path = pdf_dict[year][month][0]
    #             last_page = pdf_dict[year][month][1]
    #             reader = pypdf.PdfReader(pdf_path)

    #             merger.append(reader, pages=(second_page, last_page))
    #             reader.close()
    #         except KeyError:
    #             next

    # merger.write("merged.pdf")


if __name__ == "__main__":
    merge_pdf()
