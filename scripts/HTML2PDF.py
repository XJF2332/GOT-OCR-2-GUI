from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os
import base64
import time
import re


def convert_html_encoding(html_gb2312_path, html_utf8_path):
    """
    将GB2312编码的HTML文件转换为UTF-8编码的HTML文件。

    参数:
    - html_gb2312_path: str
        GB2312编码的HTML文件的路径。
    - html_utf8_path: str
        转换为UTF-8编码后HTML文件的保存路径。

    功能:
    - 读取指定路径的GB2312编码的HTML文件。
    - 将读取的内容转换为UTF-8编码。
    - 将转换后的内容写入到新的HTML文件中。

    注意:
    - 确保输入文件确实使用GB2312编码，否则转换可能会失败。
    - 输出文件将使用UTF-8编码，这是现代Web标准推荐使用的编码。
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


def repalce_html_content(html_utf8_path, html_utf8_local_path):
    """
    替换HTML文件中的内容。

    参数:
    - html_utf8_path: str
        输入的UTF-8编码的HTML文件路径。
    - html_utf8_local_path: str
        替换内容后的HTML文件保存路径。

    功能:
    - 读取UTF-8编码的HTML文件内容。
    - 替换HTML文件中的特定内容。
    - 将替换后的内容写入新的HTML文件。
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


def output_pdf(html_path, pdf_path, waiting_time, wait=False):
    """
    将HTML文件转换为PDF文件。

    参数:
    - html_path: str
        要转换的HTML文件的路径。
    - pdf_path: str
        输出PDF文件的保存路径。
    - waiting_time: int
        等待时间（秒）。
    - wait: bool
        是否等待页面加载完成。默认为False

    功能:
    - 使用Edge浏览器在无头模式下打开HTML文件。
    - 等待页面加载完成。
    - 执行打印命令，将页面内容转换为PDF格式。
    - 将生成的PDF数据保存到指定的文件路径。

    注意:
    - 需要事先在本地安装EdgeDriver，并设置正确的路径。
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


def all_in_one(html_gb2312_path, html_utf8_path, html_utf8_local_path, pdf_path, wait, waiting_time):
    """
    将GB2312编码的HTML文件转换为UTF-8编码，替换内容，并最终输出为PDF文件。

    参数:
    - html_gb2312_path: str
        GB2312编码的原始HTML文件的路径。
    - html_utf8_path: str
        转换为UTF-8编码后的HTML文件的临时保存路径。
    - html_utf8_local_path: str
        替换内容后的UTF-8编码HTML文件的本地保存路径。
    - pdf_path: str
        最终生成的PDF文件的保存路径。
    - wait: bool
        是否等待页面加载完成。
    - time: int
        等待时间（秒）。

    功能:
    - 使用`convert_html_encoding`函数将GB2312编码的HTML文件转换为UTF-8编码。
    - 使用`replace_html_content`函数替换UTF-8编码HTML文件中的特定内容。
    - 使用`output_pdf`函数将替换内容后的HTML文件输出为PDF文件。
    """
    try:
        print(f"[Info-HTML2PDF.all_in_one] 正在转换：{html_gb2312_path}")
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        repalce_html_content(html_utf8_path, html_utf8_local_path)
        output_pdf(html_utf8_local_path, pdf_path, waiting_time, wait)
    except Exception as e:
        print(f"[Error-HTML2PDF.all_in_one] {e}")
