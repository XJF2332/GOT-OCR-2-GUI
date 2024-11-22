import re
import os
import scripts.HTML2PDF as html2pdf
import logging
import json
from time import sleep

##########################

Renderer_logger = logging.getLogger(__name__)

config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 (The configuration file was not found)")
    print("程序将在3秒后退出")
    sleep(3)
    exit(1)

try:
    lvl = config['logger_level']
    if lvl.lower() == 'debug':
        Renderer_logger.setLevel(logging.DEBUG)
    elif lvl.lower() == 'info':
        Renderer_logger.setLevel(logging.INFO)
    elif lvl.lower() == 'warning':
        Renderer_logger.setLevel(logging.WARNING)
    elif lvl.lower() == 'error':
        Renderer_logger.setLevel(logging.ERROR)
    elif lvl.lower() == 'critical':
        Renderer_logger.setLevel(logging.CRITICAL)
    else:
        Renderer_logger.warning("无效的日志级别，回滚到 INFO 级别 (Invalid log level, rolling back to INFO level)")
        Renderer_logger.warning("请检查配置文件 (Please check the configuration file)")
        Renderer_logger.setLevel(logging.INFO)
except KeyError:
    Renderer_logger.warning("配置文件中未找到日志级别，回滚到 INFO 级别 (The log level was not found in the configuration file, rolling back to INFO level)")
    Renderer_logger.warning("请检查配置文件 (Please check the configuration file)")
    Renderer_logger.setLevel(logging.INFO)


##########################


def render(model: object, tokenizer: object, image_path: str, wait: bool, time: int, convert_to_pdf: bool):
    """
    使用OCR模型渲染图像内容到HTML文件，并可选择性地转换为PDF文件。

    Args:
        model (object): OCR模型。
        tokenizer (object): OCR模型使用的分词器。
        image_path (str): 图像文件的路径。
        wait (bool): 是否等待用户输入。
        time (int): 等待时间（秒）。
        convert_to_pdf (bool): 是否将HTML文件转换为PDF文件。

    Returns:
        int: 渲染成功，则返回 1，未加载模型或无图片返回 2，出错返回 3
    """
    try:
        # 定义输出HTML路径
        img_name = os.path.basename(image_path)
        Renderer_logger.debug(f"获取到图像名称 (Got image name)：{img_name}")
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
        html_utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        html_utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")
        Renderer_logger.debug(f"定义输出HTML路径 (Got output HTML path)：\"{html_gb2312_path}\",\"{html_utf8_path}\",\"{html_utf8_local_path}\"")

        # 渲染OCR结果
        Renderer_logger.info(f"正在渲染OCR结果 (Rendering)")
        model.chat(tokenizer, image_path, ocr_type='format', render=True, save_render_file=html_gb2312_path)

        # 转换为UTF-8编码
        Renderer_logger.info(f"正在转换为 UTF-8 编码 (Switching Encoding to utf-8)：'{html_gb2312_path}'")
        html2pdf.convert_html_encoding(html_gb2312_path, html_utf8_path)

        # 定义要替换的字符串和替换后的字符串
        search_string = '(C)'
        replace_string = r'\(C\\)'

        # 读取文件内容
        try:
            Renderer_logger.info(f"正在读取文件 (Reading file)：'{html_utf8_path}'")
            with open(html_utf8_path, 'r', encoding='utf-8') as file:
                content = file.read()
            content1 = content

            # 使用正则表达式进行替换
            content = re.sub(r'\(C\)', r'(C\\\)', content)
            content1.replace(search_string, replace_string)

            # 将替换后的内容写回文件
            Renderer_logger.info(f"正在将替换后的内容写回文件 (Writing back to file)：'{html_utf8_path}'")
            with open(html_utf8_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except FileNotFoundError:
            Renderer_logger.error(f"文件 '{html_utf8_path}' 不存在。")
        except Exception as e:
            Renderer_logger.error(f"发生错误: {e}")

        # 根据参数决定是否转换为PDF
        if convert_to_pdf:
            Renderer_logger.info(f"正在转换为PDF (Converting to PDF)：'{html_utf8_path}'")
            html2pdf.repalce_html_content(html_utf8_path, html_utf8_local_path)
            pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
            html2pdf.output_pdf(html_utf8_local_path, pdf_path, wait=wait, waiting_time=time)
        return 1
    except AttributeError:
        Renderer_logger.error(f"你看起来没有加载模型或上传图片 (You seem to have not loaded the model or uploaded an image)")
        return 2
    except Exception as e:
        Renderer_logger.error(f"发生错误 (Something went wrong): {e}")
        return 3
