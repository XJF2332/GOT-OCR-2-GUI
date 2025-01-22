import logging
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import base64
import time
import charset_normalizer
import re
import shutil
from time import sleep
import json

#################################

HTML2PDF_logger = logging.getLogger(__name__)

config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 / Config file not found)")
    print("程序将在3秒后退出 / Exiting in 3 seconds")
    sleep(3)
    exit(1)

try:
    lvl = config['logger_level']
    if lvl.lower() == 'debug':
        HTML2PDF_logger.setLevel(logging.DEBUG)
    elif lvl.lower() == 'info':
        HTML2PDF_logger.setLevel(logging.INFO)
    elif lvl.lower() == 'warning':
        HTML2PDF_logger.setLevel(logging.WARNING)
    elif lvl.lower() == 'error':
        HTML2PDF_logger.setLevel(logging.ERROR)
    elif lvl.lower() == 'critical':
        HTML2PDF_logger.setLevel(logging.CRITICAL)
    else:
        HTML2PDF_logger.warning("无效的日志级别，回滚到 INFO 级别 / Invalid log level, rolling back to INFO level")
        HTML2PDF_logger.warning("请检查配置文件 / Please check the configuration file")
        HTML2PDF_logger.setLevel(logging.INFO)
except KeyError:
    HTML2PDF_logger.warning(
        "配置文件中未找到日志级别，回滚到 INFO 级别 / Log level not found in the config file, rolling back to INFO level")
    HTML2PDF_logger.warning("请检查配置文件 / Please check the configuration file")
    HTML2PDF_logger.setLevel(logging.INFO)


#################################

def convert_html_encoding(html_gb2312_path: str, html_utf8_path: str) -> None:
    """
    将GB2312编码的HTML文件转换为UTF-8编码。
    Args:
        html_gb2312_path: GB2312编码的HTML文件路径。
        html_utf8_path: 转换后的UTF-8编码的HTML文件路径。

    Returns:
        None
    """
    # 检测编码
    try:
        HTML2PDF_logger.info(f"[convert_html_encoding] 正在读取 (Reading)：{html_gb2312_path}")
        with open(html_gb2312_path, 'rb') as b:
            content_byte = b.read()
        encoding = charset_normalizer.detect(content_byte)
        HTML2PDF_logger.debug(f"[convert_html_encoding] 编码检测结果 (Encoding detection result): {encoding}")
    except Exception as e:
        HTML2PDF_logger.error(f"[convert_html_encoding] 编码检测失败 (Encoding detection failed): {e}")
        exit(6)
    try:
        # 编码为utf-8
        if encoding['encoding'] == 'utf-8':
            shutil.copy(html_gb2312_path, html_utf8_path)
            HTML2PDF_logger.info(
                f"[convert_html_encoding] 编码已经是UTF-8编码，无需转换 (The encoding is already UTF-8, no conversion is required)")
            return
        # 转换编码
        else:
            HTML2PDF_logger.info(f"[convert_html_encoding] 正在转换 (Converting)：{html_gb2312_path}")
            with open(html_gb2312_path, 'r', encoding=encoding['encoding']) as f:
                content = f.read()
            with open(html_utf8_path, 'w', encoding='utf-8') as f:
                f.write(content)
            HTML2PDF_logger.info(f"[convert_html_encoding] 转换完成 (Conversion completed)：{html_utf8_path}")
    except Exception as e:
        HTML2PDF_logger.error(f"[convert_html_encoding] {e}")


#################################

def replace_html_content(html_utf8_path: str, html_utf8_local_path: str):
    """
    替换HTML内容
    Args:
        html_utf8_path: UTF-8编码的HTML文件路径。
        html_utf8_local_path: 替换后的HTML文件路径。

    Returns:
        None
    """
    try:
        HTML2PDF_logger.info(f"[replace_html_content] 正在替换 (Replacing)：{html_utf8_path}")

        # 替换内容
        pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
        replacement = 'markdown-it.js'

        HTML2PDF_logger.debug(f"[replace_html_content] 正在读取 (Reading)：{html_utf8_path}")
        with open(html_utf8_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # 替换
        new_html_content = re.sub(pattern, replacement, content)
        HTML2PDF_logger.debug(f"[replace_html_content] 正在写入 (Writing)：{html_utf8_local_path}")
        with open(html_utf8_local_path, 'w', encoding='utf-8') as file:
            file.write(new_html_content)
    except Exception as e:
        # 打印错误信息
        HTML2PDF_logger.error(f"[replace_html_content] {e}")


#################################

def output_pdf(html_path: str, pdf_path: str, waiting_time: int, wait: bool = False):
    """
    将HTML文件转换为PDF文件。
    Args:
        html_path: HTML文件路径。
        pdf_path: PDF文件路径。
        waiting_time: 等待时间。
        wait: 是否等待。

    Returns:
        1: 未找到WebDriver。
        2: 转换成功。
        3: 转换失败。
    """
    try:
        HTML2PDF_logger.info(f"[output_pdf] 正在转换 (Converting)：{html_path}")

        # 设置EdgeDriver的路径
        edge_driver_path = os.path.join("edge_driver", "msedgedriver.exe")
        if not os.path.exists(edge_driver_path):
            HTML2PDF_logger.error(f"[output_pdf] EdgeDriver 不存在 (EdgeDriver does not exist): {edge_driver_path}")
            return 1
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
        HTML2PDF_logger.debug(f"[output_pdf] 正在打开 (Opening)：{html_file_path}")
        driver.get(html_file_path)

        # 确保页面已加载
        if wait:
            time.sleep(waiting_time)

        # 生成PDF文件
        HTML2PDF_logger.info(f"[output_pdf] 正在生成 (Generating)：{pdf_file_path}")
        pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
            'landscape': False,
            'displayHeaderFooter': False
        })['data']

        # 写入PDF文件
        HTML2PDF_logger.debug(f"[output_pdf] 正在写入 (Writing)：{pdf_file_path}")
        with open(pdf_file_path, 'wb') as file:
            file.write(base64.b64decode(pdf_data))

        # 关闭WebDriver
        HTML2PDF_logger.debug(f"[output_pdf] 正在关闭 (Closing)：{html_path}")
        driver.quit()
        return 2
    except Exception as e:
        HTML2PDF_logger.error(f"[output_pdf] {e}")
        return 3


#################################

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
        HTML2PDF_logger.info(f"[all_in_one] 正在转换 (Converting)：{html_gb2312_path}")
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        replace_html_content(html_utf8_path, html_utf8_local_path)
        success = output_pdf(html_utf8_local_path, pdf_path, waiting_time, wait)
        if success == 1:
            HTML2PDF_logger.critical(f"[all_in_one] 未找到WebDriver (WebDriver not found)")
        elif success == 2:
            HTML2PDF_logger.info(f"[all_in_one] 转换成功 (Conversion successful)：{pdf_path}")
        elif success == 3:
            HTML2PDF_logger.critical(f"[all_in_one] 转换失败 (Conversion failed)：{pdf_path}")
    except Exception as e:
        HTML2PDF_logger.error(f"[all_in_one] {e}")
