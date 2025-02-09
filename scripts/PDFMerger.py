import os
import fitz
import glob
from scripts import scriptsLogger, local

#################################

PDFMerger_logger = scriptsLogger.getChild("PDFMerger")

#################################

pdf_list = []

#################################

def get_pdf_list(directory: str, prefix: str, except_pattern: str):
    """
    获取指定目录下指定前缀的 PDF 文件列表，并排除文件名有特定字符串的文件
    Get List of PDF files that have certain prefix in a certain folder, and remove files that has certain pattern in its name

    Args:
        directory (str): 目录路径 / Folder path
        prefix (str): 文件前缀 / File prefix
        except_pattern (str): 排除的文件名特征 / Substring in filename that needs to be removed

    Returns:
        list: PDF 文件列表 / PDF file list
    """
    try:
        # 查找文件 / Find files
        PDFMerger_logger.info(local["PDFMerger"]["info"]["looking_dir"].format(path=directory))
        pattern = os.path.join(directory, f"{prefix}_*.pdf")
        PDFMerger_logger.debug(f"[get_pdf_list] 文件名特征 (Got file name pattern)：{pattern}")
        pdf_list = glob.glob(pattern)

        # 排除具有指定特征的文件 / Remove files that has certain substring
        for pdf in pdf_list:
            if except_pattern in pdf:
                pdf_list.remove(pdf)

        # 按数字排序 / Sort
        def extract_integer(filename):
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".pdf", "")
            PDFMerger_logger.debug(
                f"[get_pdf_list] {os.path.basename(filename)}的数字部分 (Number part of {os.path.basename(filename)}): {number_part}")
            return int(number_part)

        pdf_list = sorted(pdf_list, key=extract_integer)
        PDFMerger_logger.debug(f"[get_pdf_list] PDF 文件列表 (Got PDF file list)：{pdf_list}")
        return pdf_list
    except Exception as e:
        PDFMerger_logger.error(f"[get_pdf_list] 获取 PDF 文件列表失败 (Failed to get PDF file list)：{e}")

#################################

def merge_pdfs(prefix: str):
    """
    指定前缀的 PDF 文件

    Args:
        prefix (str): 文件前缀

    Returns:
        bool: 是否成功
    """
    try:
        PDFMerger_logger.info("[merge_pdfs] 合并 PDF 文件 (Merging PDF files)")
        # 创建空文档
        merged = fitz.open()

        # 合并
        pdf_list = get_pdf_list(directory=r"result", prefix=prefix, except_pattern="Merged")
        for pdf in pdf_list:
            with fitz.open(pdf) as pdf_doc:
                for page in pdf_doc:
                    merged.insert_pdf(pdf_doc, from_page=page.number, to_page=page.number)
                    PDFMerger_logger.debug(f"[merge_pdfs] 插入页面 (Inserting page)：{page.number}")

        # 保存合并后的 PDF
        output_file = os.path.join(r"result", f"{prefix}_Merged.pdf")
        merged.save(output_file)
        PDFMerger_logger.info(f"[merge_pdfs] 保存合并后的 PDF (Saved merged PDF)：{output_file}")
        merged.close()
        return True
    except Exception as e:
        PDFMerger_logger.error(f"[merge_pdfs] 合并 PDF 文件失败 (Failed to merge PDF files)：{e}")
        return False

#################################

def t():
    merge_pdfs("t")

#################################

if __name__ == "__main__":
    t()
