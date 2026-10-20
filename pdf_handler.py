# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
import pdfplumber
from pathlib import Path
import sys

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


def get_last_page(pdf:pypdf.PdfReader) -> int:
    '''returns the index to the last page in pdf with a bank transaction table'''
    page_count = len(pdf.pages)
    for i in range(page_count-1, -1, -1):
        page = pdf.pages[i]
        if "Transaction history" in page.extract_text():
            return i 


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


def page_tester(page:pdfplumber.page):
    '''test out page methods. will delete later'''

    line_list = page.lines[1:] #cut off the first line of page
    top_boundary = line_list[0]
    im = page.to_image(resolution=200)

    prev_linewidth = top_boundary["linewidth"]
    for index in range(len(line_list)):
        if line_list[index]["linewidth"] > prev_linewidth:
            print(index - 1)
            im.draw_line(line_list[index-1], stroke_width=3)
            im.show()
            break
        prev_linewidth = line_list[index]["linewidth"]

    #TODO crop the page 
    exit()
#####


def create_csv(pdf_path:str, last_page:int):
    '''create a csv for for a banking transaction pdf'''
    table_setting = {"vertical_strategy":"text", "horizontal_strategy":"lines", "min_words_vertical":7} #NOTE i dont understand table settings

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[1]
        #TODO create for loop to go thru each page before last page and store each table in table_list. 
        table_list = page.extract_tables(table_setting)

        f_page = pdf.pages[last_page]
        page_tester(f_page)
        #visual_table_debug(f_page)
        #table_list2 = final_page.extract_tables(table_setting)


def get_pdf_dict() -> dict:
    '''get dictionary using year/month for each pdf path'''
    pdf_dict = {}
    for pdf_path in PDF_DIR.iterdir():
        pdf = pypdf.PdfReader(pdf_path)
        month, year = get_dateYear(pdf)
        final_page = get_last_page(pdf)
        pdf.close()

        #create_csv(pdf_path, final_page) #NOTE i should pass the pdf path instead
        create_csv("/home/marcodom/repos/banking_csv/banking_pdfs/March_2024.pdf", final_page) #NOTE delete later

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
