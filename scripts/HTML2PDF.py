from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os
import base64
import time
import re


def convert_html_encoding(html_gb2312_path: str, html_utf8_path: str):
    """
    将GB2312编码的HTML文件转换为UTF-8编码。
    Args:
        html_gb2312_path: GB2312编码的HTML文件路径。
        html_utf8_path: 转换后的UTF-8编码的HTML文件路径。

    Returns:
        None
    """
    try:
        # gb2312
        print(f"[Info-HTML2PDF.convert_html_encoding] 正在打开：{html_gb2312_path}")
        with open(html_gb2312_path, 'r', encoding='gb2312') as file:
            content = file.read()
        # utf8
        print(f"[Info-HTML2PDF.convert_html_encoding] 正在转码：{html_utf8_path}")
        with open(html_utf8_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"[Error-HTML2PDF.convert_html_encoding] {e}")


def repalce_html_content(html_utf8_path: str, html_utf8_local_path: str):
    """
    替换HTML内容
    Args:
        html_utf8_path: UTF-8编码的HTML文件路径。
        html_utf8_local_path: 替换后的HTML文件路径。

    Returns:
        None
    """
    try:
        print(f"[Info-HTML2PDF.repalce_html_content] 正在准备替换：{html_utf8_path}")
        # 替换内容
        pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
        replacement = 'markdown-it.js'

        # 打开文件并读取内容
        print(f"[Info-HTML2PDF.repalce_html_content] 正在打开：{html_utf8_path}")
        with open(html_utf8_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # 替换
        new_html_content = re.sub(pattern, replacement, content)
        # 将替换后的内容写入新文件
        print(f"[Info-HTML2PDF.repalce_html_content] 正在写入：{html_utf8_local_path}")
        with open(html_utf8_local_path, 'w', encoding='utf-8') as file:
            file.write(new_html_content)
    except Exception as e:
        # 打印错误信息
        print(f"[Error-HTML2PDF.repalce_html_content] {e}")


def output_pdf(html_path: str, pdf_path: str, waiting_time: int, wait: bool = False):
    """
    将HTML文件转换为PDF文件。
    Args:
        html_path: HTML文件路径。
        pdf_path: PDF文件路径。
        waiting_time: 等待时间。
        wait: 是否等待。

    Returns:
        None
    """
    try:
        print(f"[Info-HTML2PDF.output_pdf] 正在转换 PDF ：{html_path}")
        print(f"[Info-HTML2PDF.output_pdf] 正在初始化 WebDriver")

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
        print(f"[Info-HTML2PDF.output_pdf] 正在打开：{html_file_path}")
        driver.get(html_file_path)

        # 确保页面已加载
        if wait:
            time.sleep(waiting_time)

        # 生成PDF文件
        print(f"[Info-HTML2PDF.output_pdf] 正在生成 PDF：{pdf_file_path}")
        pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
            'landscape': False,
            'displayHeaderFooter': False
        })['data']

        # 写入PDF文件
        print(f"[Info-HTML2PDF.output_pdf] 正在写入：{pdf_file_path}")
        with open(pdf_file_path, 'wb') as file:
            file.write(base64.b64decode(pdf_data))

        # 关闭WebDriver
        print(f"[Info-HTML2PDF.output_pdf] 正在关闭 WebDriver")
        driver.quit()
    except Exception as e:
        print(f"[Error-HTML2PDF.output_pdf] {e}")


def all_in_one(html_gb2312_path: str, html_utf8_path: str, html_utf8_local_path: str, pdf_path: str, wait: bool,
               waiting_time: int):
    """
    将GB2312编码的HTML文件转换为UTF-8编码，并替换内容，最后转换为PDF文件。
    Args:
        html_gb2312_path: GB2312编码的HTML文件路径。
        html_utf8_path: UTF-8编码的HTML文件路径。
        html_utf8_local_path: 替换后的HTML文件路径。
        pdf_path: PDF文件路径。
        wait: 是否等待。
        waiting_time: 等待时间。

    Returns:
        None
    """
    try:
        print(f"[Info-HTML2PDF.all_in_one] 正在转换：{html_gb2312_path}")
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        repalce_html_content(html_utf8_path, html_utf8_local_path)
        output_pdf(html_utf8_local_path, pdf_path, waiting_time, wait)
    except Exception as e:
        print(f"[Error-HTML2PDF.all_in_one] {e}")
