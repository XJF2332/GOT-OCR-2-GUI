import re
import os
import scripts.HTML2PDF as convertor
from scripts import local, scriptsLogger

##########################

Renderer_logger = scriptsLogger.getChild("Renderer")


##########################


def render(model: object, tokenizer: object, img_path: str, wait: bool, time: int, conv_to_pdf: bool):
    """
    Render images to HTML files, and convert to PDF files (optional)
    渲染图像到HTML文件，并可选择性地转换为PDF文件。

    返回值-含义 / Returns-meaning
    1-成功 / 1-success
    2-未加载模型或未提供图片 / 2-no model or no image
    3-出错 / 3-an error occurred
    4-替换时未找到 utf8_path / 4-utf8_path not found while replacing
    5-替换失败 / 5-replacing failed

    Args:
        model: OCR模型 / Model
        tokenizer: 分词器 / tokenizer
        img_path: 图像文件的路径 / Path of image file
        wait (bool): 是否等待浏览器 / Whether to wait the browser
        time (int): 等待时间（秒） / Wait time (seconds)
        conv_to_pdf (bool): 是否将HTML文件转换为PDF文件 / Whether to convert HTML to PDF

    Returns:
        int: 执行状态 / Render status
    """
    try:
        # 定义输出HTML路径 / Path of output HTML
        img_name = os.path.basename(img_path)
        Renderer_logger.debug(local["Renderer"]["debug"]["img_name"].format(name=img_name))
        img_name_no_ext = os.path.splitext(img_name)[0]
        gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
        utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")
        Renderer_logger.debug(local["Renderer"]["debug"]["output_path"].format(path1=gb2312_path,path2=utf8_path,path3=utf8_local_path))

        # 渲染 / Render
        Renderer_logger.info(local["Renderer"]["info"]["rendering"].format(path=img_path))
        model.chat(tokenizer, img_path, ocr_type='format', render=True, save_render_file=gb2312_path)

        # 转换为UTF-8编码 / Convert to UTF-8
        Renderer_logger.debug(local["Renderer"]["debug"]["conv_enc"].format(path=gb2312_path))
        convertor.conv_html_enc(gb2312_path, utf8_path)

        # 替换 / Replace
        search_string = '(C)'
        replace_string = r'\(C\\)'

        # 读取文件内容 / Read file
        try:
            Renderer_logger.debug(local["Renderer"]["debug"]["reading"].format(path=utf8_path))
            with open(utf8_path, 'r', encoding='utf-8') as file:
                content = file.read()
            content1 = content

            # 使用正则表达式进行替换 / Replace using regex
            content = re.sub(r'\(C\)', r'(C\\\)', content)
            content1.replace(search_string, replace_string)
            Renderer_logger.debug(local["Renderer"]["debug"]["writing"].format(path=utf8_path))
            with open(utf8_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except FileNotFoundError:
            Renderer_logger.error(local["Renderer"]["error"]["file_not_found"].format(path=utf8_path))
            return 4
        except Exception as e:
            Renderer_logger.error(local["Renderer"]["error"]["repl_fail"].format(error=str(e)))
            return 5

        # 转换为PDF / Convert to PDF
        if conv_to_pdf:
            Renderer_logger.info(local["Renderer"]["info"]["conv2pdf"].format(path=utf8_path))
            convertor.replace_content(utf8_path, utf8_local_path)
            pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
            convertor.output_pdf(utf8_local_path, pdf_path, wait=wait, wait_time=time)
        return 1
    except AttributeError:
        Renderer_logger.error(local["Renderer"]["error"]["no_model_or_img"])
        return 2
    except Exception as e:
        Renderer_logger.error(local["Renderer"]["error"]["render_fail"].format(error=str(e)))
        return 3
