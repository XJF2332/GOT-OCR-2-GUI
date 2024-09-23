from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os
import base64
import time

def output_pdf(html_path, pdf_path):
    # 设置EdgeDriver的路径
    edge_driver_path = os.path.abspath('../edge_driver/msedgedriver.exe')

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
    time.sleep(2)

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
