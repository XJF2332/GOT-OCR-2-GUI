import os
import fitz
import glob
from scripts import scriptsLogger, local

#################################

PDFMerger_logger = scriptsLogger.getChild("PDFMerger")
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
        PDFMerger_logger.debug(local["PDFMerger"]["debug"]["filename_pattern"].format(pattern=pattern))
        pdf_list = glob.glob(pattern)

        # 排除具有指定特征的文件 / Remove files that has certain substring
        for pdf in pdf_list:
            if except_pattern in pdf:
                pdf_list.remove(pdf)

        # 按数字排序 / Sort
        def extract_integer(filename):
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".pdf", "")
            PDFMerger_logger.debug(
                local["PDFMerger"]["debug"]["num_part"].format(file=os.path.basename(filename), num=number_part))
            return int(number_part)

        pdf_list = sorted(pdf_list, key=extract_integer)
        PDFMerger_logger.info(local["PDFMerger"]["info"]["pdf_list"].format(lst=pdf_list))
        return pdf_list
    except Exception as e:
        PDFMerger_logger.error(local["PDFMerger"]["info"]["pdf_list_fail"].format(error=str(e)))


#################################

def merge_pdfs(prefix: str):
    """
    Merge PDF files that have given prefix
    合并指定前缀的 PDF 文件

    Args:
        prefix (str): 文件前缀 / Prefix of PDF files to merged

    Returns:
        bool: 是否成功 / Succeeded or not
    """
    try:
        PDFMerger_logger.info(local["PDFMerger"]["info"]["merging"])
        # 创建空文档 / Create an empty doc
        merged = fitz.open()

        # 合并 / Merge
        pdf_list = get_pdf_list(directory=r"result", prefix=prefix, except_pattern="Merged")
        for pdf in pdf_list:
            with fitz.open(pdf) as pdf_doc:
                for page in pdf_doc:
                    merged.insert_pdf(pdf_doc, from_page=page.number, to_page=page.number)
                    PDFMerger_logger.debug(local["PDFMerger"]["debug"]["insert_page"].format(page=page.number))

        # 保存 / Save
        output_file = os.path.join(r"result", f"{prefix}_Merged.pdf")
        merged.save(output_file)
        PDFMerger_logger.info(local["PDFMerger"]["info"]["save_merged"].format(path=output_file))
        merged.close()
        return True
    except Exception as e:
        PDFMerger_logger.error(local["PDFMerger"]["error"]["merge_fail"].format(error=str(e)))
        return False


#################################

if __name__ == "__main__":
    pass
