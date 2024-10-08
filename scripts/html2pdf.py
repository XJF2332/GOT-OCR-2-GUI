from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os
import base64
import time
import re

def output_pdf(html_path, pdf_path):
    """
    将HTML文件转换为PDF文件
    Args:
        html_path:
        pdf_path:

    Returns:

    """
    # 设置EdgeDriver的路径
    edge_driver_path = os.path.abspath('./edge_driver/msedgedriver.exe')

    # 设置本地HTML文件的路径
    html_file_path = 'file://' + os.path.abspath(html_path)

    # 设置输出的PDF文件路径
    pdf_file_path = pdf_path

    # 设置Edge选项以启用打印
    edge_options = Options()
    edge_options.add_argument("--headless")  # 无头模式
    edge_options.add_argument("--disable-gpu")

    # 初始化Service对象
    service = Service(executable_path=edge_driver_path)

    # 初始化WebDriver
    driver = webdriver.Edge(service=service, options=edge_options)

    # 打开HTML文件
    driver.get(html_file_path)

    # 确保页面已加载
    # time.sleep(2)

    # 生成PDF文件
    pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
        'landscape': False,
        'displayHeaderFooter': False
    })['data']

    # 写入PDF文件
    with open(pdf_file_path, 'wb') as file:
        file.write(base64.b64decode(pdf_data))

    # 关闭WebDriver
    driver.quit()

    # print(f'PDF saved as {pdf_file_path}')


def convert_html_encoding(html_gb2312_path, html_utf8_path):
    """
    转换HTML编码
    Args:
        html_gb2312_path:
        html_utf8_path:

    Returns:

    """
    # gb2312
    with open(html_gb2312_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # utf8
    with open(html_utf8_path, 'w', encoding='utf-8') as file:
        file.write(content)


# 替换HTML内容
def repalce_html_content(html_utf8_path, html_utf8_local_path):
    """
    替换HTML内容
    Args:
        html_utf8_path:
        html_utf8_local_path:

    Returns:

    """
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(html_utf8_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(html_utf8_local_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)


def all_in_one(html_gb2312_path, html_utf8_path, html_utf8_local_path, pdf_path):
    """
    将HTML文件转换为PDF文件
    Args:
        html_gb2312_path:
        html_utf8_path:
        html_utf8_local_path:
        pdf_path:

    Returns:

    """
    convert_html_encoding(html_gb2312_path, html_utf8_path)
    repalce_html_content(html_utf8_path, html_utf8_local_path)
    output_pdf(html_utf8_local_path, pdf_path)