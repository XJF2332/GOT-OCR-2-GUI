import fitz
import os
import glob
import scripts.Renderer as Renderer
import logging
from datetime import datetime

# 日志记录器 (Logger)
logger = logging.getLogger('PDF2ImagePlusRenderer')
logger.setLevel(logging.DEBUG)

# 时间 (Time)
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# 文件处理器 (File handler)
if not os.path.exists("Logs"):
    os.makedirs("Logs")
log_name = os.path.join("Logs", f"log_PDF2ImagePlusRenderer_{current_time}.log")
file_handler = logging.FileHandler(log_name, encoding='utf-8')

# 格式化器 (Formatter)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 控制台处理器 (Console handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug("日志记录器已初始化 (The logger has been initialized)")

pdf_path_base = ''


def get_base_name(path):
    return os.path.basename(path)


def remove_extension(base_name):
    return os.path.splitext(base_name)[0]


def split_pdf(pdf_path: str, img_path: str, target_dpi: int):
    """
    将PDF文件拆分为单页PDF文件，并保存为PNG图像文件。

    Args:
        pdf_path (str): PDF文件路径
        img_path (str): 保存PNG图像文件的目录路径
        target_dpi (int): 目标DPI
    Returns:
        bool: 操作是否成功
    """
    try:
        if not os.path.exists(img_path):
            os.makedirs(img_path)

        logger.info(f"[split_pdf] 正在打开 (Opening)：{pdf_path}")
        doc = fitz.open(pdf_path)

        pdf_path_base = get_base_name(path=pdf_path)
        logger.debug(f"[split_pdf] PDF 文件名 (Got PDF file name)：{pdf_path_base}")
        pdf_path_base = remove_extension(pdf_path_base)
        logger.debug(f"[split_pdf] PDF 文件名去掉扩展名 (Got PDF file name without extension)：{pdf_path_base}")

        for page_number in range(len(doc)):
            zoom = target_dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            # 将PDF页面转换为图像
            logger.info(f"[split_pdf] 正在转换第 {page_number + 1} 页 (Converting page {page_number + 1})")
            page = doc[page_number]
            pix = page.get_pixmap(matrix=matrix)

            # 保存图像
            logger.info(f"[split_pdf] 正在保存第 {page_number + 1} 页 (Saving page {page_number + 1})")
            output_path = os.path.join(f"{img_path}", f"{pdf_path_base}_{page_number}.png")
            pix.save(output_path)

        logger.info("[split_pdf] 转换完成 (Conversion completed)")
        doc.close()
        return True
    except Exception as e:
        logger.error(f"[split_pdf] 转换失败 (Conversion failed): {e}")
        return False


def get_sorted_png_files(directory: str, prefix: str):
    """
    获取指定目录下，符合前缀和整数后缀的PNG文件列表，并按整数大小排序。

    Args:
        directory (str): 目录路径
        prefix (str): 文件名前缀
    Returns:
        list: 排序后的PNG文件列表
    """
    try:
        # 构建匹配模式
        pattern = os.path.join(directory, f"{prefix}_*.png")
        logger.debug(f"[get_sorted_png_files] 匹配模式 (Pattern)：{pattern}")

        # 获取所有匹配的文件
        files = glob.glob(pattern)
        logger.debug(f"[get_sorted_png_files] 所有匹配的文件 (All matched files)：{files}")

        # 定义一个函数，用于从文件名中提取整数部分
        def extract_integer(filename):
            # 假设文件名格式正确，去掉扩展名 .png 和前缀
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".png", "")
            return int(number_part)

        # 按整数大小排序文件列表
        sorted_files = sorted(files, key=extract_integer)
        logger.debug(f"[get_sorted_png_files] 排序后的文件列表 (Sorted file list)：{sorted_files}")
        return sorted_files
    except Exception as e:
        logger.error(f"[get_sorted_png_files] 获取文件列表失败 (Failed to get file list): {e}")


def pdf_renderer(model: object, tokenizer: object, pdf_path: str, target_dpi: int, pdf_convert: bool, wait: bool,
                 time: int):
    """
    将PDF文件转换为图片，并调用渲染器进行渲染。

    Args:
        model (object): 模型对象
        tokenizer (object): 分词器对象
        pdf_path (str): PDF文件路径
        target_dpi (int): 目标DPI
        pdf_convert (bool): 是否将渲染结果转换为PDF
        wait (bool): 是否等待浏览器渲染
        time (int): 等待时间
    Returns:
        bool: 操作是否成功
    """
    # 创建目录
    if not os.path.exists("pdf"):
        os.makedirs("pdf")
    if not os.path.exists("imgs"):
        os.makedirs("imgs")

    try:
        # 将 pdf 文件转换为图片
        logger.info(f"[pdf_renderer] 正在渲染 (Rendering)：{pdf_path}")
        split_pdf(pdf_path=pdf_path, img_path="imgs", target_dpi=target_dpi)
        # pdf 文件名
        pdf_name = get_base_name(path=pdf_path)
        pdf_name = remove_extension(pdf_name)
        logger.debug(f"[pdf_renderer] PDF 文件名 (Got PDF file name)：{pdf_name}")
        # 获取图片列表
        img_list = get_sorted_png_files(directory="imgs", prefix=pdf_name)
        logger.debug(f"[pdf_renderer] 图片列表 (Got image list)：{img_list}")
        if len(img_list) == 0:
            logger.error("[pdf_renderer] 图片列表为空 (Image list is empty)")
            return False
        # 调用渲染器
        for img in img_list:
            logger.info(f"[pdf_renderer] 正在渲染图片 (Rendering image)：{img}")
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=img, wait=wait, time=time,
                                      convert_to_pdf=pdf_convert)
            if success == 1:
                logger.info("[pdf_renderer] 渲染成功 (Rendering succeeded)")
            elif success == 2:
                logger.error(
                    "[pdf_renderer] 你看起来没有加载模型或上传图片 (You seem to have not loaded the model or uploaded an image)")
            elif success == 3:
                logger.error("[pdf_renderer] 渲染失败 (Rendering failed)")
        return True
    except Exception as e:
        logger.error(f"[pdf_renderer] 渲染失败 (Rendering failed): {e}")
        return False
