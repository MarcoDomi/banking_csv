import pdfplumber

class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.page_count = len(self.pdf.pages)
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[60, 100, 148, 400, 450, 520]}

    def __del__(self):
        self.pdf.close()
        print("goodbye")

    def extract_tables(self):
        '''extracts all tables from a wells fargo banking pdf and returns list of all tables'''
        table_list = []
        with pdfplumber.open(self.PDF_PATH) as pdf:

            page_num = 1 #start at second page
            
            while not self._is_final_page(pdf, page_num + 1):
                print("general")
                self._general_table_extraction(pdf.pages[page_num])

                page_num += 1
                
                
            self._final_table_extraction()
            


    def _general_table_extraction(self, page):
        crop_values = (60, 118, 520, page.height)
        pass

    def _final_table_extraction(self):
        '''extracting final table must be handled differently due to differing varying table size'''

        pass

    def _is_final_page(self,pdf, next_page):
        '''use next page to determine if current page has final table'''
        try:
            pdf.pages[next_page]
            return False
        except IndexError:
            print("outta pages")
            return True