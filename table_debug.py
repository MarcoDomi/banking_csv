import pdfplumber
from pathlib import Path

pdf_path = Path("banking_pdfs/May_2024.pdf")


# with pdfplumber.open(pdf_path, pages=[2,3,4]) as pdf:
#     words = pdf.pages[0].extract_words(extra_attrs=["fontname", "size", "doctop"])
#     headers = [header for header in words if header["doctop"] > 107 and header["doctop"] < 160]

# print(words[0].keys())

# for header in headers:
#     print(header["text"], header["doctop"], header["x0"], header["x1"])


# with pdfplumber.open(pdf_path, pages=[2,3,4]) as pdf:
#     for page in pdf.pages:
#         table = page.crop((60, 118, 520, page.height))
#         im = table.to_image(resolution=200)
#         im.debug_tablefinder({"horizontal_strategy":"lines_strict", "vertical_strategy":"explicit", "explicit_vertical_lines":[60, 100, 148, 400, 450, 520]})
#         im.show()
import wf_extractor

wf1 = wf_extractor.wells_fargo_extractor(pdf_path)
wf1.extract_tables()
#print(wf1._is_final_page(4))