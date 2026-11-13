import pdfplumber
import re

#NOTE there is no check for pdfs that have zero transactions b/c im not sure what an empty table would look like
class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.pages = self.pdf.pages[1:] #remove title page
        self.page_count = len(self.pdf.pages)

        header_obj = self._get_header_obj()
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[header_obj["x0"], 100,148,400,450,520]} #vertical lines are hardcoded. can cause issues if pdf layout is changed
        
        
    def __del__(self):
        self.pdf.close()
        print("closing pdfplumber object...")
        

    def extract_tables(self) -> list:
        '''extracts and merges all tables from the wells fargo banking pdf'''
        table_list = []
        
        page_index = 1 #start at second page to skip title page
        
        while not self._is_final_page(page_index):
            table_list.extend(self._general_table_extraction(page_index))
            page_index += 1

        table_list.extend(self._final_table_extraction(page_index))

        return table_list
            

    def _general_table_extraction(self, page_index:int) -> list[list[str]]:
        '''extracts and returns the table from page '''
        page = self.pages[page_index]
  
        #NOTE check position for start line on each page.
        left, top = 0 #placeholder values. will change later
        cropped_page = page.crop((left, top, 520, page.height))
        table = cropped_page.extract_table(self.table_settings)

        return table


    def _final_table_extraction(self, page_index:int) -> list[list[str]]:
        '''extracting final table must be handled differently due to differing varying table size'''
        page = self.pages[page_index]
        bottom = self._get_crop_bottom(page)

        cropped_page = page.crop((60,118,520,bottom))
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


    def _get_header_obj(self) -> dict:
        '''returns dictionary for the table header'''
        header_patterns = [
            r"Date Number Description Additions Subtractions balance",
            r"Date Number Description Credits Debits balance"
        ]

        header_obj = self.pages[0].search(header_patterns[0])
        if len(header_obj) == 0:
            header_obj = self.pages[0].search(header_patterns[1])

        return header_obj[0]


def _line_debug(pdf, page_num):
    page = pdf.pages[page_num]
    start_line = page.lines[1]
    end_line = page.lines[19] #hardcode to specify the line i want

    im = page.to_image(resolution=200)
    im.draw_line(start_line, stroke_width=3)

    im.show()

    print(start_line["linewidth"])
    print(end_line["linewidth"])
    

def _table_debug(wf, page_num):
    '''pass PDF object and its table settings'''

    page = wf.pdf.pages[page_num]

    top = page.lines[1]["bottom"] #NOTE some pages have 2 bold lines before the table. for some reason the second line gets ignored and using index 1 gets the 3rd line on page which is the line under the table headers
    left = page.lines[1]["x0"]
    cutoff = page.search(r"Ending balance on \d/\d{1,2}\s+\d+(,\d{3})*\.\d{2}") #NOTE pdfs from 2026 DO NOT have this 
    bottom = cutoff[0]["top"]
    
    
    crop_page = page.crop((left, top, 520, bottom)) #right side of table is going to be hardcoded. i dont want entire table. has same value as the last explicit vertical line
    im_crop = crop_page.to_image(resolution=200)
    im_crop.debug_tablefinder({"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[left, 100, 148, 400, 450, 520]})
    im_crop.show()

def get_table_header(wf):
    page = wf.pdf.pages[1]
    wf._set_vertical_lines(page)



def debug(path, page_num):
    wf = wells_fargo_extractor(path)
    # get_table_header(wf)
    # print(wf.table_settings)
    # _table_debug(wf, page_num)
    #_line_debug(wf.pdf, page_num)

   


if __name__ == "__main__":
    debug("/mnt/c/Users/MarcoDominguez/Desktop/bb/Statement 03_15_22 (27K, PDF).pdf", 1)
    debug("banking_pdfs/February_2024.pdf", 4)
    
   
