import pdfkit
from bs4 import BeautifulSoup

config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

def extract_const_text_content(html_content):
    """
    从HTML内容中提取<script>标签中的const text内容。

    参数:
    html_content -- HTML内容字符串

    返回:
    提取出的const text内容字符串
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    script_content = soup.find('script').string if soup.find('script') else ''
    const_text_pattern = r'const\s+text\s*=\s*"(.*?)"'
    match = re.search(const_text_pattern, script_content)
    const_text = match.group(1) if match else ''
    return const_text

def const_text_to_pdf(input_html_path, output_pdf_path):
    """
    从HTML文件中提取const text内容，并将其保存为PDF文件。

    参数:
    input_html_path -- 输入HTML文件的路径
    output_pdf_path -- 输出PDF文件的路径
    """
    try:
        # 读取HTML文件
        with open(input_html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 提取const text内容
        const_text = extract_const_text_content(html_content)

        # 将const text内容转换为PDF
        pdfkit.from_string(const_text, output_pdf_path, configuration=config)
        print(f"转换完成，PDF文件已保存为：{output_pdf_path}")
    except Exception as e:
        print(f"转换失败：{e}")

# 导入re模块用于正则表达式匹配
import re

# 用户可以直接调用这个函数并提供文件路径
if __name__ == "__main__":
    # 用户需要提供输入HTML文件的路径和输出PDF文件的路径
    input_html_path = input("请输入HTML文件的路径: ")
    output_pdf_path = input("请输入PDF文件的输出路径: ")

    # 调用函数进行转换
    const_text_to_pdf(input_html_path, output_pdf_path)
