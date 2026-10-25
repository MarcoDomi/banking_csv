# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
import pdfplumber
from pathlib import Path
import sys
import wf_extractor

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



#####
def visual_table_debug(page):
    table_setting = {"vertical_strategy":"text", "horizontal_strategy":"lines", "min_words_vertical":7}
    im = page.to_image(resolution=200)
    im.debug_tablefinder(table_setting)
    im.show()


def read_table(tables):
    for table in tables:
        for row in table:
            print(row)
    exit()
#####


def create_csv(pdf_path:str):
    '''create a csv for for a banking transaction pdf'''
    
    table_list = wf_extractor.wells_fargo_extractor()
    
    

        

def get_csv_dict() -> dict:
    '''create dictionary using year/month for each pdf path'''
    csv_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        pdf = pypdf.PdfReader(pdf_path)
        month, year = get_dateYear(pdf)
        pdf.close()

        print(pdf_path.name)
        create_csv(pdf_path) #NOTE i should pass the pdf path instead
        #create_csv("/home/marcodom/repos/banking_csv/banking_pdfs/March_2024.pdf") #NOTE delete later

        if year not in csv_dict:
            csv_dict[year] = {}
        csv_dict[year][month] = pdf_path #there should only be one pdf per month in a given year

    return csv_dict


def merge_pdf(): 
    '''merge all pdfs in banking_pdfs into a single pdf'''
    second_page = 1 #start at second page

    pdf_dict = get_csv_dict()
    
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
