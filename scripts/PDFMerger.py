import os
import fitz
import glob

pdf_list = []


def get_pdf_list(directory:str, prefix:str, except_pattern:str):
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
        pattern = os.path.join(directory, f"{prefix}_*.pdf")
        print(f"[Info-PDFMerger.get_pdf_list] 正在查找 PDF 文件")
        pdf_list = glob.glob(pattern)

        # 排除具有指定后缀的文件
        print(f"[Info-PDFMerger.get_pdf_list] 正在排除 {except_pattern} 文件")
        for pdf in pdf_list:
            if except_pattern in pdf:
                pdf_list.remove(pdf)

        # 排序文件列表
        print(f"[Info-PDFMerger.get_pdf_list] 正在排序 PDF 文件")

        def extract_integer(filename):
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".pdf", "")
            return int(number_part)

        pdf_list = sorted(pdf_list, key=extract_integer)
        print(f"[Info-PDFMerger.get_pdf_list] PDF 文件列表：{pdf_list}")
        return pdf_list
    except Exception as e:
        print(f"[Error-PDFMerger.get_pdf_list] 获取 PDF 列表失败：{e}")


def merge_pdfs(prefix):
    """
    指定前缀的 PDF 文件

    输入:
    prefix: 文件前缀

    输出:
    True: 合并成功
    False: 合并失败
    """
    try:
        # 创建空文档
        merged = fitz.open()

        # 合并
        pdf_list = get_pdf_list(directory=r"result", prefix=prefix, except_pattern="Merged")
        for pdf in pdf_list:
            print(f"[Info-PDFMerger.merge_pdfs] 正在合并 PDF 文件：{pdf}")
            with fitz.open(pdf) as pdf_doc:
                for page in pdf_doc:
                    merged.insert_pdf(pdf_doc, from_page=page.number, to_page=page.number)

        # 保存合并后的 PDF
        output_file = os.path.join(r"result", f"{prefix}_Merged.pdf")
        print(f"[Info-PDFMerger.merge_pdfs] 正在保存合并后的 PDF 文件：{output_file}")
        merged.save(output_file)
        merged.close()
        return True
    except Exception as e:
        print(f"[Error-PDFMerger.merge_pdfs] 合并 PDF 文件失败：{e}")
        return False


def t():
    merge_pdfs("t")


if __name__ == "__main__":
    t()
