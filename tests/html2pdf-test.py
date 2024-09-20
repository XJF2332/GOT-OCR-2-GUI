import pdfkit

config = pdfkit.configuration(wkhtmltopdf='./wkhtmltopdf/bin/wkhtmltopdf.exe')

options = {
    'javascript-delay': 10000,  # 延迟时间，确保JavaScript有足够的时间执行
    'quiet': ''
}

pdfkit.from_file('ocr_utf8.html', 'out.pdf', options=options, configuration=config)
