import pdfkit

config = pdfkit.configuration(wkhtmltopdf='./wkhtmltopdf/bin/wkhtmltopdf.exe')

options = {
    'page-size': 'A4',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm',
    'enable-javascript': '',
    'javascript-delay': 5000,  # 延迟 10 秒，确保 JavaScript 有足够的时间执行
    'no-stop-slow-scripts': '',  # 不停止慢脚本
}

pdfkit.from_file('ocr_utf8.html', 'out.pdf', options=options, configuration=config)
