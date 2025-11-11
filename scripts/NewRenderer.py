import subprocess
import os
from scripts import ErrorCode, local, scriptsLogger
from scripts import TeXComplete
import send2trash

available_outputs = ["pdf", "markdown", "docx", "tex"]
NewRendererLogger = scriptsLogger.getChild("NewRenderer")

def render(raw_tex: str, output_format: str, output_name: str = "output") -> tuple[str, int]:
    """
    把tex文本转换成其他格式，保存到result文件夹

    :param raw_tex: 原始的tex文本
    :param output_format: 输出格式，支持"tex"、"pdf"、"markdown"、"docx"，只能选择一种
    :param output_name: 输出文件名
    :return: 一个元组，第一个元素是转换结果，第二个元素是错误码
    """
    temp_files = []
    NewRendererLogger.info("[render] Rendering started")
    # 无效的输出格式
    if output_format not in available_outputs:
        NewRendererLogger.error(f"[render] Invalid output format: {output_format}")
        return "Invalid output format", ErrorCode.INVALID_OUTPUT_FORMAT.value

    # 补全tex格式并保存
    NewRendererLogger.debug("[render] Completing TeX using TeXComplete.py")
    completed_tex = TeXComplete.complete_tex(raw_tex)
    out_tex_path_abs = os.path.abspath(os.path.join("result", f"{output_name}.tex"))
    with open(out_tex_path_abs, "w", encoding="utf-8") as f:
        f.write(completed_tex)

    # 转换
    # PDF
    NewRendererLogger.debug("[render] Converting")
    if output_format == "pdf":
        try:
            NewRendererLogger.debug("[render] Target: PDF")
            pdf_args = ["pdflatex", out_tex_path_abs, f"-output-directory={os.path.abspath('result')}"]
            NewRendererLogger.debug(f"[render] Subprocess args: {pdf_args}")
            subprocess.run(args=pdf_args, check=True, stderr=subprocess.PIPE)
            
            # 清理临时文件
            temp_files.append(out_tex_path_abs)
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.aux")))
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.log")))
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.out")))
            NewRendererLogger.debug(f"[render] Temp file list: {temp_files}")
            for file in temp_files:
                send2trash.send2trash(file)
                NewRendererLogger.debug(f"[render] Deleted: {file}")

            NewRendererLogger.info("[render] Converted to PDF")
            return "Converted to PDF", ErrorCode.SUCCESS.value
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = f"[render] PDFLaTeX error: {error_msg}"
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PDFLATEX_ERROR.value
    # Markdown
    elif output_format == "markdown":
        try:
            NewRendererLogger.debug("[render] Target: markdown")
            md_args = ["pandoc", out_tex_path_abs, "-o", os.path.abspath(os.path.join("result", f"{output_name}.md"))]
            NewRendererLogger.debug(f"[render] Subprocess args: {md_args}")
            subprocess.run(args=md_args, check=True, stderr=subprocess.PIPE)

            temp_files.append(out_tex_path_abs)
            NewRendererLogger.debug(f"[render] Temp file list: {temp_files}")
            for file in temp_files:
                send2trash.send2trash(file)
                NewRendererLogger.debug(f"[render] Deleted: {file}")

            NewRendererLogger.info("[render] Converted to markdown")
            return "Converted to markdown", ErrorCode.SUCCESS.value
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = f"[render] Pandoc error: {error_msg}"
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PANDOC_ERROR.value
    # Docx (Word)
    elif output_format == "docx":
        try:
            NewRendererLogger.debug("[render] Target: docx(Word)")
            docx_args = ["pandoc", out_tex_path_abs, "-o", os.path.abspath(os.path.join("result", f"{output_name}.docx"))]
            NewRendererLogger.debug(f"[render] Docx args: {docx_args}")
            subprocess.run(args=docx_args, check=True, stderr=subprocess.PIPE)
            # 删除临时文件
            temp_files.append(out_tex_path_abs)
            NewRendererLogger.debug(f"[render] Temp file list: {temp_files}")
            for file in temp_files:
                send2trash.send2trash(file)
                NewRendererLogger.debug(f"[render] Deleted: {file}")

            NewRendererLogger.info("[render] Converted to docx")
            return "Converted to docx", ErrorCode.SUCCESS.value
        # 报错处理
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = f"[render] Pandoc error: {error_msg}"
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PANDOC_ERROR.value
    # tex不需要做什么
    else:
        NewRendererLogger.info(f"[render] No need to convert")
        return "No conversion made", ErrorCode.SUCCESS.value