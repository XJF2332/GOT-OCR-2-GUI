def convert_html_encoding(input_file_path, output_file_path):
    # 以GB2312编码读取文件
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # 以UTF-8编码写入内容到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

input_file_path = 'ocr.html'
output_file_path = 'ocr_utf8.html'
result = convert_html_encoding(input_file_path, output_file_path)