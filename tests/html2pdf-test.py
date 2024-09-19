import pdfkit
import re
from bs4 import BeautifulSoup

config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')

def extract_style_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    style_tag = soup.find('style')
    return style_tag.string if style_tag else ''

def extract_const_text_from_script(script_content):
    # 使用正则表达式来匹配所有被双引号包围的字符串，并保留换行符
    string_pattern = r'(?<!\\)"(.*?)(?<!\\)"'
    matches = re.findall(string_pattern, script_content, re.DOTALL)
    # 将所有匹配的字符串连接起来，并替换掉转义引号
    const_text = ''.join(matches).replace('\\"', '"')
    # 替换JavaScript的换行符为HTML的换行符
    const_text = const_text.replace('\\n', '<br>')
    return const_text

def const_text_to_pdf(input_html_path, output_pdf_path):
    try:
        with open(input_html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 提取<style>标签内容
        style_content = extract_style_from_html(html_content)

        # 提取<script>标签内容
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script')
        script_content = script_tag.string if script_tag else ''

        # 提取const text内容
        const_text = extract_const_text_from_script(script_content)

        # 构建完整的HTML文档，包含提取的<style>标签和const text内容
        styled_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {style_content}
            </style>
        </head>
        <body>
            <pre>{const_text}</pre>
        </body>
        </html>
        """

        # 将const text内容转换为PDF
        pdfkit.from_string(styled_text, output_pdf_path, configuration=config)
        print(f"转换完成，PDF文件已保存为：{output_pdf_path}")
    except Exception as e:
        print(f"转换失败：{e}")

if __name__ == "__main__":
    input_html_path = input("请输入HTML文件的路径: ")
    output_pdf_path = input("请输入PDF文件的输出路径: ")
    const_text_to_pdf(input_html_path, output_pdf_path)
