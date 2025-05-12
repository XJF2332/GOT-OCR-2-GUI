import re
import os
# import scripts.HTML2PDF as convertor
from scripts import local, scriptsLogger, ErrorCode
import charset_normalizer

##########################

Renderer_logger = scriptsLogger.getChild("Renderer")


##########################


def render(model: object, tokenizer: object, img_path: str, wait: bool = False,
           time: int = 0, conv_to_pdf: bool = False) -> int:
    """
    渲染图像到HTML文件
    Render images to HTML files

    :param model: OCR模型 / Model
    :param tokenizer: 分词器 / tokenizer
    :param img_path: 图像文件的路径 / Path of image file
    :param wait (bool): [DEPR] 是否等待浏览器 / Whether to wait the browser
    :param time (int): [DEPR] 等待时间（秒） / Wait time (seconds)
    :param conv_to_pdf (bool): [DEPR] 是否将HTML文件转换为PDF文件 / Whether to convert HTML to PDF

    Returns:
        int: 执行状态 / Render status
    """
    try:
        # 定义输出HTML路径 / Path of output HTML
        img_name = os.path.basename(img_path)
        Renderer_logger.debug(local["Renderer"]["debug"]["img_name"].format(name=img_name))
        img_name_no_ext = os.path.splitext(img_name)[0]
        pdf_path = os.path.join("result", f"{img_name_no_ext}.html")
        # utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        # utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")
        # Renderer_logger.debug(local["Renderer"]["debug"]["output_path"].format(path1=gb2312_path,path2=utf8_path,path3=utf8_local_path))

        # 渲染 / Render
        Renderer_logger.info(local["Renderer"]["info"]["rendering"].format(path=img_path))
        model.chat(tokenizer, img_path, ocr_type='format', render=True, save_render_file=pdf_path)

        # 转换为 UTF-8 编码 / Convert to UTF-8
        # Renderer_logger.debug(local["Renderer"]["debug"]["conv_enc"].format(path=gb2312_path))
        # conv_res = convertor.conv_html_enc(gb2312_path, utf8_path)
        # if conv_res != 0:
        #     return conv_res

        # 替换 / Replace
        search_string = '(C)'
        replace_string = r'\(C\\)'

        # 读取文件内容 / Read file
        try:
            Renderer_logger.debug(local["Renderer"]["debug"]["reading"].format(path=pdf_path))
            with open(pdf_path, 'rb') as content_bytes:
                cbytes = content_bytes.read()
                encoding = charset_normalizer.detect(cbytes)
            with open(pdf_path, "r", encoding=encoding["encoding"]) as f:
                content = f.read()

            # 使用正则表达式进行替换 / Replace using regex
            content1 = content
            content = re.sub(r'\(C\)', r'(C\\\)', content)
            content1.replace(search_string, replace_string)
            Renderer_logger.debug(local["Renderer"]["debug"]["writing"].format(path=pdf_path))
            with open(pdf_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except FileNotFoundError:
            Renderer_logger.error(local["Renderer"]["error"]["file_not_found"].format(path=pdf_path))
            return ErrorCode.FILE_NOT_FOUND.value
        except Exception as e:
            Renderer_logger.error(local["Renderer"]["error"]["repl_fail"].format(error=str(e)))
            return ErrorCode.REPLACEMENT_FAIL.value

        # 转换为PDF / Convert to PDF
        # if conv_to_pdf:
        #     Renderer_logger.info(local["Renderer"]["info"]["conv2pdf"].format(path=utf8_path))
        #     repl_res = convertor.replace_content(utf8_path, utf8_local_path)
        #     if repl_res != 0:
        #         return repl_res
        #     pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
        #     output_res = convertor.output_pdf(utf8_local_path, pdf_path, wait=wait, wait_time=time)
        #     if output_res != 0:
        #         return output_res
        return 0
    except AttributeError:
        Renderer_logger.error(local["Renderer"]["error"]["no_model_or_img"])
        return ErrorCode.NO_MODEL_IMG.value
    except Exception as e:
        Renderer_logger.error(local["Renderer"]["error"]["render_fail"].format(error=str(e)))
        return ErrorCode.UNKNOWN.value
