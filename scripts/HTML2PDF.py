import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import base64
import time
import charset_normalizer
import re
import shutil
from scripts import local
from scripts import scriptsLogger

#################################

HTML2PDF_logger = scriptsLogger.getChild("HTML2PDF")

#################################

def conv_html_enc(original_path: str, utf8_path: str) -> None:
    """
    将HTML文件转换为UTF-8编码
    Convert encoding of HTML files to UTF-8

    Args:
        original_path: 输入 HTML 文件路径 / Input HTML file path
        utf8_path: 转换后的 HTML 文件路径 / Converted HTML file path

    Returns:
        None
    """
    # 检测编码 / Detect encoding
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["reading_ori"].format(file=original_path))
        with open(original_path, 'rb') as b:
            content_byte = b.read()
        encoding = charset_normalizer.detect(content_byte)
        HTML2PDF_logger.debug(local["HTML2PDF"]["debug"]["enc_detect"].format(encoding=encoding))
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["enc_detect_fail"].format(e=e))
        exit(6)
    try:
        # 编码为 utf-8 / Encoding is utf-8
        if encoding['encoding'] == 'utf-8':
            shutil.copy(original_path, utf8_path)
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["no_cnv_required"])
            return
        # 转换编码 / Convert encoding
        else:
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["converting"].format(file=original_path))
            with open(original_path, 'r', encoding=encoding['encoding']) as f:
                content = f.read()
            with open(utf8_path, 'w', encoding='utf-8') as f:
                f.write(content)
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["cnv_completed"].format(file=utf8_path))
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error"].format(e=e))


#################################

def replace_content(utf8_path: str, utf8_local_path: str):
    """
    替换 HTML 中的在线脚本为本地文件
    Replace online script in HTML files into local file

    Args:
        utf8_path: UTF-8编码的HTML文件路径 / Input HTML path (UTF-8)
        utf8_local_path: 替换后的HTML文件路径 / Replaced HTML path

    Returns:
        None
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["replacing"].format(file=utf8_path))

        # 替换内容
        pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
        replacement = 'markdown-it.js'

        HTML2PDF_logger.debug(local["HTML2PDF"]["info"]["reading"].format(file=utf8_path))
        with open(utf8_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # 替换
        new_html_content = re.sub(pattern, replacement, content)
        HTML2PDF_logger.debug(local["HTML2PDF"]["info"]["writing"].format(file=utf8_local_path))
        with open(utf8_local_path, 'w', encoding='utf-8') as file:
            file.write(new_html_content)
    except Exception as e:
        # 打印错误信息
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error_rep"].format(e=e))


#################################

def output_pdf(html_path: str, pdf_path: str, wait_time: int, wait: bool = False):
    """
    将 HTML 文件转换为 PDF 文件
    Convert HTML to PDF

    Args:
        html_path: HTML文件路径 / Input HTML path
        pdf_path: PDF文件路径 / Output PDF path
        wait_time: 等待时间 / Wait time
        wait: 是否等待 / Whether to wait the browser

    Returns:
        1: 未找到 WebDriver / WebDriver not found
        2: 转换成功 / Succeeded
        3: 转换失败 / Failed
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["conv2pdf"].format(file=html_path))

        # 设置EdgeDriver的路径 / EdgeDriver path
        edge_driver_path = os.path.join("edge_driver", "msedgedriver.exe")
        if not os.path.exists(edge_driver_path):
            HTML2PDF_logger.error(local["HTML2PDF"]["error"]["no_driver"].format(path=edge_driver_path))
            return 1
        # 设置本地HTML文件的路径 / Local HTML file path
        html_file_path = 'file://' + os.path.abspath(html_path)
        # 设置输出的PDF文件路径 / Output PDF file path
        pdf_file_path = pdf_path

        # 设置Edge选项以启用打印 / Enable printing
        edge_options = Options()
        edge_options.add_argument("--headless")  # 无头模式 / Headless mode
        edge_options.add_argument("--disable-gpu")

        # 初始化 Service 对象 / Init service
        service = Service(executable_path=edge_driver_path)

        # 初始化 WebDriver / Init webdriver
        driver = webdriver.Edge(service=service, options=edge_options)

        # 打开 HTML 文件 / Open HTML file
        HTML2PDF_logger.debug(local["HTML2PDF"]["info"]["opening"].format(file=html_path))
        driver.get(html_file_path)

        # 确保页面已加载 / Ensure that page has been loaded
        if wait:
            time.sleep(wait_time)

        # 生成 PDF 文件 / Generate PDF file
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["generating"].format(file=pdf_file_path))
        pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
            'landscape': False,
            'displayHeaderFooter': False
        })['data']

        # 写入 PDF 文件 / Write PDF file
        HTML2PDF_logger.debug(local["HTML2PDF"]["debug"]["writing"].format(file=pdf_file_path))
        with open(pdf_file_path, 'wb') as file:
            file.write(base64.b64decode(pdf_data))

        # 关闭 WebDriver / Close WebDriver
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["closing"])
        driver.quit()
        return 2
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error_pdf"].format(e=e))
        return 3


#################################

def aio(ori_html_path: str, html_utf8_path: str, html_utf8_local_path: str, pdf_path: str, wait: bool, wait_time: int):
    """
    上面的函数三合一
    All-In-One

    Args:
        ori_html_path: 输入 HTML 文件路径 / Input HTML file path
        html_utf8_path: UTF-8 编码的 HTML 文件路径 / HTML(UTF-8) path
        html_utf8_local_path: 替换后的 HTML 文件路径 / Replaced HTML path
        pdf_path: PDF 文件路径 / PDF file path
        wait: 是否等待 / Whether to wait the browser to load
        wait_time: 等待时间 / Waiting time

    Returns:
        None
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["aio_conv"].format(file=ori_html_path))
        conv_html_enc(ori_html_path, html_utf8_path)
        replace_content(html_utf8_path, html_utf8_local_path)
        success = output_pdf(html_utf8_local_path, pdf_path, wait_time, wait)
        if success == 1:
            HTML2PDF_logger.error(local["HTML2PDF"]["error"]["aio_no_driver"])
        elif success == 2:
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["aio_success"].format(file=pdf_path))
        elif success == 3:
            HTML2PDF_logger.error(local["HTML2PDF"]["info"]["aio_fail"].format(file=ori_html_path))
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["info"]["unexpected_error_aio"].format(e=e))
