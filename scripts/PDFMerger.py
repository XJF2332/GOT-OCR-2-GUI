import os
import fitz
import glob
import logging
from datetime import datetime

# 日志记录器 (Logger)
logger = logging.getLogger('PDFMerger')
logger.setLevel(logging.DEBUG)

# 时间 (Time)
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# 文件处理器 (File handler)
if not os.path.exists("Logs"):
    os.makedirs("Logs")
log_name = os.path.join("Logs", f"log_PDFMerger_{current_time}.log")
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

pdf_list = []


def get_pdf_list(directory: str, prefix: str, except_pattern: str):
    """
    获取指定目录下指定前缀的 PDF 文件列表

    Args:
        directory (str): 目录路径
        prefix (str): 文件前缀
        except_pattern (str): 排除的文件后缀

    Returns:
        list: PDF 文件列表
    """
    try:
        # 查找文件
        logger.info(f"[get_pdf_list] 查找目录 (Looking for files in directory)：{directory}")
        pattern = os.path.join(directory, f"{prefix}_*.pdf")
        logger.debug(f"[get_pdf_list] 文件名特征 (Got file name pattern)：{pattern}")
        pdf_list = glob.glob(pattern)

        # 排除具有指定后缀的文件
        for pdf in pdf_list:
            if except_pattern in pdf:
                pdf_list.remove(pdf)

        # 按数字排序
        def extract_integer(filename):
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".pdf", "")
            logger.debug(
                f"[get_pdf_list] {os.path.basename(filename)}的数字部分 (Number part of {os.path.basename(filename)}): {number_part}")
            return int(number_part)

        pdf_list = sorted(pdf_list, key=extract_integer)
        logger.debug(f"[get_pdf_list] PDF 文件列表 (Got PDF file list)：{pdf_list}")
        return pdf_list
    except Exception as e:
        logger.error(f"[get_pdf_list] 获取 PDF 文件列表失败 (Failed to get PDF file list)：{e}")


def merge_pdfs(prefix: str):
    """
    指定前缀的 PDF 文件

    Args:
        prefix (str): 文件前缀

    Returns:
        bool: 是否成功
    """
    try:
        logger.info("[merge_pdfs] 合并 PDF 文件 (Merging PDF files)")
        # 创建空文档
        merged = fitz.open()

        # 合并
        pdf_list = get_pdf_list(directory=r"result", prefix=prefix, except_pattern="Merged")
        for pdf in pdf_list:
            with fitz.open(pdf) as pdf_doc:
                for page in pdf_doc:
                    merged.insert_pdf(pdf_doc, from_page=page.number, to_page=page.number)
                    logger.debug(f"[merge_pdfs] 插入页面 (Inserting page)：{page.number}")

        # 保存合并后的 PDF
        output_file = os.path.join(r"result", f"{prefix}_Merged.pdf")
        merged.save(output_file)
        logger.info(f"[merge_pdfs] 保存合并后的 PDF (Saved merged PDF)：{output_file}")
        merged.close()
        return True
    except Exception as e:
        logger.error(f"[merge_pdfs] 合并 PDF 文件失败 (Failed to merge PDF files)：{e}")
        return False


def t():
    merge_pdfs("t")


if __name__ == "__main__":
    t()
