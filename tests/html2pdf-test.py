import matplotlib.pyplot as plt
import matplotlib
import os
import re
from bs4 import BeautifulSoup
import pdfkit

config = pdfkit.configuration(wkhtmltopdf=r'./wkhtmltopdf/bin/wkhtmltopdf.exe')


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


input_html_path = 'ocr_utf8.html'

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

# 确保matplotlib使用LaTeX渲染
matplotlib.rcParams['text.usetex'] = True

# 如果需要更详细的LaTeX设置，可以使用以下代码
# matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# 创建一个图形和一个子图
fig, ax = plt.subplots()

# 添加LaTeX文本
ax.text(0.5, 0.5, styled_text,
        fontsize=15, ha='center', va='center')

# 设置子图的边界
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# 移除坐标轴
ax.axis('off')

# 保存为PDF文件
plt.savefig('latex_matplotlib.pdf')
