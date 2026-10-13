# removes pages and merges pdfs in a certain order that contain wells fargo banking transactions
import pypdf
import calendar
from pathlib import Path


pdf_dir = Path("banking_pdfs").resolve()
print(pdf_dir)

def get_dateYear(pdf_path:Path):
    '''retrieve the date and year from pdf text'''
    pdf = pypdf.PdfReader(pdf_path)
    page = pdf.pages[0]
    
    text_list = page.extract_text().splitlines()
    dateline = text_list[1]
    date = dateline.split(' ')

    month = date[0]
    year = date[2]

    return month, year


def monthly_rename_pdf(): #dont think this function is needed anymore but i will keep it anyway
    '''rename a wells fargo pdf to its month'''
    for pdf in pdf_dir.iterdir():
        month, year = get_dateYear(pdf)
        new_path = pdf_dir / f"{month}_{year}.pdf"

        if new_path.exists():
            print("ERROR: Path already exists. aborting operation")

        pdf.replace(new_path)


def get_pdf_dict():
    '''get dictionary that contains years and months and for each pdf path'''
    pdf_dict = {}
    for pdf in pdf_dir.iterdir():
        month, year = get_dateYear(pdf)
        if year not in pdf_dict:
            pdf_dict[year] = {}

        pdf_dict[year][month] = pdf #there should only be one pdf per month in a given year

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