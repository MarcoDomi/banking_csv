import pdfplumber

class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.page_count = len(self.pdf.pages)
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[60, 100, 148, 400, 450, 520]}


    def __del__(self):
        self.pdf.close()
        

    def extract_tables(self):
        '''extracts all tables from a wells fargo banking pdf and returns list of all tables'''
        table_list = []
        
        page_index = 1 #start at second page
        
        while not self._is_final_page(page_index):
            print("general")
            self._general_table_extraction(page_index)
            page_index += 1
        print("final")
        self._final_table_extraction()

        return table_list
            

    def _general_table_extraction(self, page_index):
        '''extracts and returns the table from page '''
        page = self.pdf.pages[page_index]
        crop_values = (60, 118, 520, page.height)
        cropped_page = page.crop(crop_values)
        self._table_image_debug(cropped_page)


    def _final_table_extraction(self):
        '''extracting final table must be handled differently due to differing varying table size'''

        pass


    def _is_final_page(self, curr_page_index):
        '''use next page to determine if current page has final table'''
        try:
            next_page = self.pdf.pages[curr_page_index + 1]
            
            if "Transaction history( continued)" in next_page.extract_text(): #could fail if wells fargo makes changes to the text
                return False

            return True
        except IndexError:
            print("outta pages")
            return True


    def _table_image_debug(self, page):
        im = page.to_image(resolution=200)
        im.debug_tablefinder(self.table_settings)
        im.show()