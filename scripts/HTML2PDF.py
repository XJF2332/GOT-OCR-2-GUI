import os
import shutil

import send2trash
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import charset_normalizer
from scripts import local
from scripts import scriptsLogger
from scripts import ErrorCode

#################################

HTML2PDF_logger = scriptsLogger.getChild("HTML2PDF")

CONFIG = {
    "DRIVER_PATH": os.path.join("edge_driver", "msedgedriver.exe"),
    "MATHJAX_URL": r"https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js",
    "LOCAL_MATHJAX": "markdown-it.js"
}

#################################

def conv_html_enc(original_path: str, utf8_path: str) -> int:
    """
    将HTML文件转换为UTF-8编码
    Convert encoding of HTML files to UTF-8
    如果输入已经是UTF-8了，则会复制一份
    If input is already UTF-8, it will create a copy

    Args:
        original_path: 输入 HTML 文件路径 / Input HTML file path
        utf8_path: 转换后的 HTML 文件路径 / Converted HTML file path

    Returns:
        错误码 / Error codes
    """
    if not os.path.exists(original_path):
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["file_not_found"].format(file=original_path))
        return ErrorCode.FILE_NOT_FOUND.value

    # 检测编码 / Detect encoding
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["reading_ori"].format(file=original_path))
        with open(original_path, 'rb') as b:
            content_byte = b.read()
        encoding = charset_normalizer.detect(content_byte)
        HTML2PDF_logger.debug(local["HTML2PDF"]["debug"]["enc_detect"].format(encoding=encoding))
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["enc_detect_fail"].format(e=e))
        return 11
    try:
        # 编码为 utf-8 / Encoding is utf-8
        if encoding['encoding'] == 'utf-8':
            shutil.copy(original_path, utf8_path)
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["no_cnv_required"])
            return 0
        # 编码不是 utf-8 / Encoding is not utf-8
        else:
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["converting"].format(file=original_path))
            with open(original_path, 'r', encoding=encoding['encoding']) as f:
                content = f.read()
            with open(utf8_path, 'w', encoding='utf-8') as f:
                f.write(content)
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["cnv_completed"].format(file=utf8_path))
            return 0
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error"].format(e=e))
        return 12


#################################

def replace_content(utf8_path: str, utf8_local_path: str) -> int:
    """
    替换 HTML 中的在线脚本为本地文件
    Replace online script in HTML files into local file

    Args:
        utf8_path: UTF-8编码的HTML文件路径 / Input HTML path (UTF-8)
        utf8_local_path: 替换后的HTML文件路径 / Replaced HTML path

    Returns:
        错误码 / Error code
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["replacing"].format(file=utf8_path))

        HTML2PDF_logger.debug(local["HTML2PDF"]["info"]["reading"].format(file=utf8_path))
        with open(utf8_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # 替换
        new_html_content = content.replace(CONFIG["MATHJAX_URL"], CONFIG["LOCAL_MATHJAX"])
        HTML2PDF_logger.debug(local["HTML2PDF"]["info"]["writing"].format(file=utf8_local_path))
        with open(utf8_local_path, 'w', encoding='utf-8') as file:
            file.write(new_html_content)
        return 0
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error_rep"].format(e=e))
        return 13


#################################

def output_pdf(html_path: str, pdf_path: str, wait_time: int, wait: bool = False) -> int:
    """
    将 HTML 文件转换为 PDF 文件
    Convert HTML to PDF

    Args:
        html_path: HTML文件路径 / Input HTML path
        pdf_path: PDF文件路径 / Output PDF path
        wait_time: 等待时间 / Wait time
        wait: 是否等待 / Whether to wait the browser

    Returns:
        运行状态 / Status
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["conv2pdf"].format(file=html_path))

        # 设置EdgeDriver的路径 / EdgeDriver path
        edge_driver_path = os.path.join("edge_driver", "msedgedriver.exe")
        if not os.path.exists(edge_driver_path):
            HTML2PDF_logger.error(local["HTML2PDF"]["error"]["no_driver"].format(path=edge_driver_path))
            return 14
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
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

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
        return 0
    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["error"]["unexpected_error_pdf"].format(e=e))
        return 15


#################################

def aio(ori_html_path: str,
        html_utf8_path: str,
        html_utf8_local_path: str,
        pdf_path: str,
        wait: bool,
        wait_time: int) -> int | None:
    """
    转换编码 + 替换内容 + 输出 PDF
    Convert encoding + replace content + output PDF

    Args:
        ori_html_path: 输入 HTML 文件路径 / Input HTML file path
        html_utf8_path: UTF-8 编码的 HTML 文件路径 / HTML(UTF-8) path
        html_utf8_local_path: 替换后的 HTML 文件路径 / Replaced HTML path
        pdf_path: PDF 文件路径 / PDF file path
        wait: 是否等待 / Whether to wait the browser to load
        wait_time: 等待时间 / Waiting time

    Returns:
        错误码 / Error codes
    """
    try:
        HTML2PDF_logger.info(local["HTML2PDF"]["info"]["aio_conv"].format(file=ori_html_path))
        def cleanup_temp_files():
            for path in [html_utf8_path, html_utf8_local_path]:
                if os.path.exists(path):
                    send2trash.send2trash(path)
                    HTML2PDF_logger.debug(local["HTML2PDF"]["debug"]["temp_file_deleted"].format(file=path))

        conv_flag = conv_html_enc(ori_html_path, html_utf8_path)
        if conv_flag != ErrorCode.SUCCESS.value:
            cleanup_temp_files()
            return conv_flag

        repl_flag = replace_content(html_utf8_path, html_utf8_local_path)
        if repl_flag != ErrorCode.SUCCESS.value:
            cleanup_temp_files()
            return repl_flag

        output_flag = output_pdf(html_utf8_local_path, pdf_path, wait_time, wait)
        if output_flag != ErrorCode.SUCCESS.value:
            cleanup_temp_files()
            return output_flag
        else:
            cleanup_temp_files()
            HTML2PDF_logger.info(local["HTML2PDF"]["info"]["aio_success"].format(file=pdf_path))
            return ErrorCode.SUCCESS.value

    except Exception as e:
        HTML2PDF_logger.error(local["HTML2PDF"]["info"]["unexpected_error_aio"].format(e=e))
        return ErrorCode.UNEXPECTED_AIO.value
