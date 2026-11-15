import pdfplumber

#NOTE there is no check for pdfs that have zero transactions b/c im not sure what an empty table would look like
class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.pages = self.pdf.pages[1:] #remove title page
        self.page_count = len(self.pdf.pages)

        header_obj = self._get_header_obj(self.pages[0])
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[header_obj["x0"], 100,148,400,450,520], "snap_y_tolerance":4} #vertical lines are hardcoded. can cause issues if pdf layout is changed
        
        
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

        bottom_bound = self._get_crop_bottom(page)

        cropped_page = page.crop((left_bound,top_bound,520,bottom_bound))
        table = cropped_page.extract_table(self.table_settings)

        return table
        

    def _get_crop_bottom(self, page):
        '''finds and returns 'bottom' value for cropping the final page'''
        cutoff = page.search(r"Ending bal\s*ance on \d{1,2}/\d{1,2}\s+-?\d+(,\d{3})*\.\d{2}")
        if len(cutoff) == 0:
            cutoff = page.search(r"Totals\s+(\$\d{1,3}(,\d{3})*.?\d{2}(\s+)?){2}") #NOTE replace (\s+)? with \s*
        
        return cutoff[0]["top"] #NOTE should add error handler here


    def _is_final_page(self, curr_page_index): 
        try:
            next_page = self.pages[curr_page_index + 1]
            header_check = self._get_header_obj(next_page) #NOTE should try to return this header obj so i can use its data for next iteration
            if header_check == None:
                return True

            return False
        except IndexError:
            print("No more pages")
            return True


    def _get_header_obj(self, page) -> dict:
        '''returns dictionary for the table header'''

        header_patterns = [
            r"Date Number Description Additions Subtractions balance",
            r"Date Number Description Credits Debits balance"
        ]

        for pattern in header_patterns:
            header_list = page.search(pattern)
            if len(header_list) != 0:
                return header_list[0]

        return None #no matching headers were found
    

def table_detect(page, table_settings):
    im = page.to_image(resolution=200)
    im.debug_tablefinder(table_settings)
    im.show()


def test__get_bottom_cutoff(page):
    cutoff = page.search(r"Ending bal\s*ance on \d{1,2}/\d{1,2}\s+-?\d+(,\d{3})*\.\d{2}")
    if len(cutoff) == 0:
        cutoff = page.search(r"Totals\s+(\$\d{1,3}(,\d{3})*.?\d{2}(\s+)?){2}") 

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
    bottom = test__get_bottom_cutoff(page)["top"]
    crop_page = page.crop((left, top, 520, bottom))
    table_detect(crop_page, wf.table_settings)


def test__get_header_obj(file_path):
    for dir in file_path.iterdir():
        wf = wells_fargo_extractor(dir)
        print(dir.name)
        print(wf._get_header_obj(wf.pages[0])["text"])


def test__is_final_page(file_path):
    for pdf in file_path.iterdir():
        wf = wells_fargo_extractor(pdf)
        for i in range(wf.page_count):
            is_final = wf._is_final_page(i)
            if is_final:
                print(pdf.name, i+2) #add 2 to convert index to page number and account for removed title page
                break

def test__crop_bottom(file_path):
    for pdf in file_path.iterdir():
        wf = wells_fargo_extractor(pdf)
        for i in range(wf.page_count):
            if wf._is_final_page(i):
                try:
                    wf._get_crop_bottom(wf.pages[i])
                except:
                    print("ERROR: ", pdf.name)
                break


if __name__ == "__main__":
    from pathlib import Path

    file_path1 = Path("/mnt/c/Users/MarcoDominguez/Desktop/bb/")
    file_path2 = Path("banking_pdfs") 
    tables_debug(file_path1 / "Statement 03_16_26 (180K, PDF).pdf", 3) 