import fitz
import os
import glob
import scripts.Renderer as Renderer
from scripts import scriptsLogger, local

#################################

PDFHandler_logger = scriptsLogger.getChild("PDFHandler")

#################################

def get_base_name(path):
    return os.path.basename(path)


def remove_extension(base_name):
    return os.path.splitext(base_name)[0]

#################################

def split_pdf(pdf_path: str, img_path: str, target_dpi: int) -> bool:
    """
    将 PDF 文件的每一页都拆成独立的图片文件
    Split every page in the input PDF file into images

    Args:
        pdf_path (str): PDF 文件路径 / PDF to be split
        img_path (str): 保存 PNG 图像文件的目录路径 / Path to save images
        target_dpi (int): 分割 PDF 时使用的 DPI / DPI used while splitting PDFs
    Returns:
        bool: 操作是否成功 / Succeeded or not
    """
    try:
        if not os.path.exists(img_path):
            os.makedirs(img_path)

        PDFHandler_logger.info(local["PDFHandler"]["info"]["opening"].format(file=pdf_path))
        doc = fitz.open(pdf_path)

        pdf_path_base = remove_extension(get_base_name(pdf_path))
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["got_pdf_name"])

        for page_number in range(len(doc)):
            zoom = target_dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            # 将PDF页面转换为图像
            PDFHandler_logger.debug(local["PDFHandler"]["debug"]["converting_page"].format(page=page_number + 1))
            page = doc[page_number]
            pix = page.get_pixmap(matrix=matrix)

            # 保存图像
            PDFHandler_logger.debug(local["PDFHandler"]["debug"]["saving_page"].format(page=page_number + 1))
            output_path = os.path.join(f"{img_path}", f"{pdf_path_base}_{page_number}.png")
            pix.save(output_path)

        PDFHandler_logger.info(local["PDFHandler"]["info"]["conv_complete"])
        doc.close()
        return True
    except Exception as e:
        PDFHandler_logger.error(local["PDFHandler"]["info"]["conv_fail"].format(error=str(e)))
        return False

#################################

def get_png_seq(directory: str, prefix: str):
    """
    获取指定目录下，符合前缀和整数后缀的 PNG 文件列表，并按整数大小排序
    Get png file sequence that has given prefix in the given directory, and sort them by number

    Args:
        directory (str): 目录路径 / Directory you want to scan
        prefix (str): 文件名前缀 / Prefix of your image sequence
    Returns:
        list: 排序后的 PNG 文件列表 / Sorted png list
    """
    try:
        # 构建匹配模式 / Build pattern
        pattern = os.path.join(directory, f"{prefix}_*.png")
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["build_pattern"].format(pattern=pattern))

        # 获取所有匹配的文件 / Get all matched files
        files = glob.glob(pattern)
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["matched_files"].format(files=files))

        # 从文件名中提取整数部分 / Extract int from filename
        def extract_int(filename):
            # 去掉扩展名 .png 和前缀 / Remove .png and the prefix
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".png", "")
            PDFHandler_logger.debug(local["PDFHandler"]["debug"]["number"].forma(num=number_part))
            return int(number_part)

        # 按整数大小排序文件列表
        sorted_files = sorted(files, key=extract_int)
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["sorted_list"].format(list=sorted_files))
        return sorted_files
    except Exception as e:
        PDFHandler_logger.error(local["PDFHandler"]["error"]["seq_get_fail"].format(error=str(e)))

#################################

def pdf_renderer(model: object, tokenizer: object, pdf_path: str, dpi: int, pdf_conv: bool, wait: bool,
                 time: int):
    """
    将 PDF 文件转换为图片，并调用渲染器进行渲染
    wait 这个参数说是等待浏览器渲染，但我测试没有发现浏览器没有渲染就被转 PDF 的现象，所以不等大概率也是没问题的
    Split PDF into images and render them using the renderer
    the param "wait" was said to wait your browser to fully render the HTML, but I did not find not-rendered PDF, so it's possibly safe not to wait

    Args:
        model (object): 模型对象 / Your loaded model
        tokenizer (object): 分词器对象 / Your loaded tokenizer
        pdf_path (str): PDF 文件路径 / PDF file path
        dpi (int): 分割 PDF 时使用的 DPI / DPI used when splitting PDF
        pdf_conv (bool): 是否将渲染结果转换为 PDF / Whether to convert render results into PDF
        wait (bool): 是否等待浏览器渲染 / Whether to wait the browser to render
        time (int): 等待时间
    Returns:
        执行状态 / Status
    """
    # 创建目录 / Create folder
    if not os.path.exists("pdf"):
        os.makedirs("pdf")
    if not os.path.exists("imgs"):
        os.makedirs("imgs")

    try:
        re=False
        PDFHandler_logger.info(local["PDFHandler"]["info"]["rendering"].format(file=pdf_path))
        # 将 PDF 文件转换为图片 / Split PDFs into images
        split_pdf(pdf_path=pdf_path, img_path="imgs", target_dpi=dpi)
        # PDF 文件名 / PDF file name
        pdf_name = remove_extension(get_base_name(pdf_path))
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["pdf_name"].format(file=pdf_name))
        # 获取图片序列 / Get image sequence
        img_list = get_png_seq(directory="imgs", prefix=pdf_name)
        PDFHandler_logger.debug(local["PDFHandler"]["debug"]["image_seq"].format(seq=img_list))
        if len(img_list) == 0:
            PDFHandler_logger.error(local["PDFHandler"]["error"]["empty_seq"])
            return False
        # 调用渲染器 / Use renderer
        for img in img_list:
            PDFHandler_logger.info(local["PDFHandler"]["info"]["rendering_img"].format(img=img))
            success = Renderer.render(model=model, tokenizer=tokenizer, img_path=img, wait=wait, time=time, conv_to_pdf=pdf_conv)
            if success == 1:
                PDFHandler_logger.info(local["PDFHandler"]["info"]["render_success"])
                re = True
            elif success == 2:
                PDFHandler_logger.error(local["PDFHandler"]["error"]["no_model_or_pdf"])
                re = False
            elif success == 3:
                PDFHandler_logger.error(local["PDFHandler"]["error"]["render_fail"])
                re = False
        return re
    except Exception as e:
        PDFHandler_logger.error(local["PDFHandler"]["error"]["render_fail_unexp"].format(error=str(e)))
        return False
