import pdfkit

config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
pdfkit.from_file('ocr_utf8.html', 'ocr_utf8.pdf', configuration=config)
