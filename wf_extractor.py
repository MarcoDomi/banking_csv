import pdfplumber

class wells_fargo_extractor:
    '''performs table extraction on Wells Fargo bank transaction PDF files'''
    def __init__(self, pdf_path:str):
        self.pdf = pdfplumber.open(pdf_path)
        self.page_count = len(self.pdf.pages)
        self.table_settings = {"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[60, 100, 148, 400, 450, 520]} #vertical lines are hardcoded. can cause issues if pdf layout is changed


    def __del__(self):
        print("closing pdfplumber object...")
        self.pdf.close()
        

    def extract_tables(self):
        '''extracts all tables from a wells fargo banking pdf and returns list of all tables'''
        table_list = []
        
        page_index = 1 #start at second page to skip title page
        
        while not self._is_final_page(page_index):
            print("general")
            table_list.append(self._general_table_extraction(page_index))
            page_index += 1

        print("final")
        table_list.append(self._final_table_extraction(page_index))

        return table_list
            

    def _general_table_extraction(self, page_index):
        '''extracts and returns the table from page '''
        page = self.pdf.pages[page_index]
        cropped_page = page.crop((60, 118, 520, page.height))
        table = cropped_page.find_table(self.table_settings)

        return table


    def _final_table_extraction(self, page_index):
        '''extracting final table must be handled differently due to differing varying table size'''
        page = self.pdf.pages[page_index]
        bottom = self._get_crop_bottom(page)

        cropped_page = page.crop((60,118,520,bottom))
        table = cropped_page.find_table(self.table_settings)

        return table
        

    def _get_crop_bottom(self, page):
        '''finds and returns bottom value for cropping the final page'''
        line_list = page.lines
        
        prev_line = line_list[1] #start at second line on page
        for index in range(2,len(line_list)):
            if line_list[index]['linewidth'] > prev_line["linewidth"]:
                return prev_line['bottom']
                
            prev_line = line_list[index]


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


    def _table_debug(self, page):
        im = page.to_image(resolution=200)
        im.debug_tablefinder(self.table_settings)
        im.show()