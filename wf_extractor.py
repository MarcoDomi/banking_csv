import pdfplumber
import re

#NOTE there is no check for pdfs that have zero transactions b/c im not sure what an empty table would look like
class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.pages = self.pdf.pages[1:] #remove title page
        self.page_count = len(self.pdf.pages)

        header_obj = self._get_header_obj(self.pages[0])
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[header_obj["x0"], 100,148,400,450,520]} #vertical lines are hardcoded. can cause issues if pdf layout is changed
        
        
    def __del__(self):
        self.pdf.close()
        print("closing pdfplumber object...")
        

    def extract_tables(self) -> list:
        '''extracts and merges all tables from the wells fargo banking pdf'''
        table_list = []
        
        page_index = 0 
        
        while not self._is_final_page(page_index):
            table_list.extend(self._general_table_extraction(page_index))
            page_index += 1

        table_list.extend(self._final_table_extraction(page_index))

        return table_list
            

    def _general_table_extraction(self, page_index:int) -> list[list[str]]:
        '''extracts and returns the table from page '''
        page = self.pages[page_index]
  
        header_obj = self._get_header_obj(page)
        top_bound = header_obj["bottom"]
        left_bound = self.table_settings["explicit_vertical_lines"][0]

        cropped_page = page.crop((left_bound, top_bound, 520, page.height))
        table = cropped_page.extract_table(self.table_settings)
       
        return table


    def _final_table_extraction(self, page_index:int) -> list[list[str]]:
        '''extracting final table must be handled differently due to differing varying table size'''
        page = self.pages[page_index]

        header_obj = self._get_header_obj(page)
        top_bound = header_obj["bottom"]
        left_bound = self.table_settings["explicit_vertical_lines"][0]

        bottom = self._get_crop_bottom(page)

        cropped_page = page.crop((left_bound,top_bound,520,bottom))
        table = cropped_page.extract_table(self.table_settings)

        return table
        

    def _get_crop_bottom(self, page):
        '''finds and returns 'bottom' value for cropping the final page'''
        line_list = page.lines
        
        prev_line = line_list[1] #start at second line on page
        for index in range(2,len(line_list)):
            if line_list[index]['linewidth'] > prev_line["linewidth"]: #stop iterating thru page lines when we arrive at a line that is thicker
                return prev_line['bottom']
                
            prev_line = line_list[index]


    def _is_final_page(self, curr_page_index): #NOTE  i should check for the presence of a table header instead. some pdfs have "transaction history( continued)" but no actual table
        try:
            next_page = self.pages[curr_page_index + 1]
            
            if "Transaction history( continued)" in next_page.extract_text(): #could fail if wells fargo makes changes to the text
                return False

            return True
        except IndexError:
            print("outta pages")
            return True


    def _get_header_obj(self, page) -> dict:
        '''returns dictionary for the table header'''
        header_patterns = [
            r"Date Number Description Additions Subtractions balance",
            r"Date Number Description Credits Debits balance"
        ]

        header_obj = page.search(header_patterns[0])
        if len(header_obj) == 0:
            header_obj = page.search(header_patterns[1])

        return header_obj[0]
    

def _table_debug(wf, page_num):
    '''pass PDF object and its table settings'''

    page = wf.pdf.pages[page_num]

    # top = page.lines[1]["bottom"] #NOTE some pages have 2 bold lines before the table. for some reason the second line gets ignored and using index 1 gets the 3rd line on page which is the line under the table headers
    # left = page.lines[1]["x0"]
    # cutoff = page.search(r"Ending balance on \d/\d{1,2}\s+\d+(,\d{3})*\.\d{2}") #NOTE pdfs from 2026 DO NOT have this 
    # bottom = cutoff[0]["top"]
    #crop_page = page.crop((left, top, 520, bottom)) #right side of table is going to be hardcoded. i dont want entire table. has same value as the last explicit vertical line

    # im_crop = crop_page.to_image(resolution=200)
    # im_crop.debug_tablefinder({"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[left, 100, 148, 400, 450, 520]})
    # im_crop.show()


def table_detect(page, table_settings):
    im = page.to_image(resolution=200)
    im.debug_tablefinder(table_settings)
    im.show()

def get_bottom_cutoff(page):
    cutoff = page.search(r"Ending bal\s*ance on \d{1,2}/\d{1,2}\s+-?\d+(,\d{3})*\.\d{2}")
    if len(cutoff) == 0:
        cutoff = page.search(r"Totals\s+(\$\d{1,3}(,\d{3})*.?\d{2}(\s+)?){2}") #NOTE replace (\s+)? with \s*

    return cutoff[0]


def tables_debug(path, end_page):
    wf = wells_fargo_extractor(path)

    start_page = 0
    end_page -= 2
    for i in range(start_page, end_page):
        page = wf.pages[i]
        header = wf._get_header_obj(page)
        left = header["x0"]
        top = header["bottom"]
        bottom = page.height
        crop_page = page.crop((left, top, 520, bottom))
        table_detect(crop_page, wf.table_settings)
        print("OK")



    page = wf.pages[end_page]
    header = wf._get_header_obj(page)
    left = header["x0"]
    top = header["bottom"]
    bottom = get_bottom_cutoff(page)["top"]
    crop_page = page.crop((left, top, 520, bottom))
    table_detect(crop_page, wf.table_settings)



if __name__ == "__main__":
    from pathlib import Path

    file_path = Path("/mnt/c/Users/MarcoDominguez/Desktop/bb/")
    tables_debug("banking_pdfs/May_2024.pdf", 5)    


    # with pdfplumber.open(file_path / "Statement 10_18_22 (33K, PDF).pdf") as pdf:
    #     page = pdf.pages[2]
    #     print(page.extract_text())