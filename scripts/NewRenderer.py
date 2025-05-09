import subprocess
import os
from scripts import ErrorCode,local,scriptsLogger
from scripts import TeXComplete
import send2trash

temp_files = []
available_outputs = ["pdf", "markdown", "docx", "tex"]
NewRendererLogger = scriptsLogger.getChild("NewRenderer")

def render(raw_tex: str, output_format: str) -> tuple:
    global temp_files
    temp_files = []
    # 无效的输出格式
    if output_format not in available_outputs:
        NewRendererLogger.error(local["NewRenderer"]["error"]["invalid_out_format"].format(format=output_format))
        return local["NewRenderer"]["error"]["invalid_out_format"], ErrorCode.INVALID_OUTPUT_FORMAT.value

    # 补全tex格式并保存
    completed_tex = TeXComplete.complete_tex(raw_tex)
    out_tex_path_abs = os.path.abspath(os.path.join("result", "output.tex"))
    with open(os.path.join("result", "output.tex"), "w", encoding="utf-8") as f:
        f.write(completed_tex)

    # 转换
    if output_format == "pdf": # PDF
        try:
            subprocess.run(["pdflatex", out_tex_path_abs, f"-output-directory={os.path.abspath('result')}"], check=True)

            temp_files.append(out_tex_path_abs)
            temp_files.append(os.path.abspath(os.path.join("result", "output.aux")))
            temp_files.append(os.path.abspath(os.path.join("result", "output.log")))
            temp_files.append(os.path.abspath(os.path.join("result", "output.out")))
            NewRendererLogger.info(local["NewRenderer"]["info"]["pdf_converted"])

            for file in temp_files:
                send2trash.send2trash(file)

            return local["NewRenderer"]["info"]["pdf_converted"], 0
        except subprocess.CalledProcessError:
            NewRendererLogger.error(local["NewRenderer"]["error"]["pdflatex_error"])
            return local["NewRenderer"]["error"]["pdflatex_error"], ErrorCode.PDFLATEX_ERROR.value
    elif output_format == "markdown": # MD
        try:
            subprocess.run(["pandoc", out_tex_path_abs, "-o",
                            os.path.abspath(os.path.join("result", "output.md"))],check=True)

            temp_files.append(out_tex_path_abs)
            NewRendererLogger.info(local["NewRenderer"]["info"]["markdown_converted"])

            for file in temp_files:
                send2trash.send2trash(file)

            return local["NewRenderer"]["info"]["markdown_converted"], 0
        except  subprocess.CalledProcessError:
            NewRendererLogger.error(local["NewRenderer"]["error"]["pandoc_error"])
            return local["NewRenderer"]["error"]["pandoc_error"], ErrorCode.PANDOC_ERROR.value
    elif output_format == "docx": # DOCX
        try:
            subprocess.run(["pandoc", out_tex_path_abs, "-o",
                            os.path.abspath(os.path.join("result", "output.docx"))],check=True)

            temp_files.append(out_tex_path_abs)
            NewRendererLogger.info(local["NewRenderer"]["info"]["docx_converted"])

            for file in temp_files:
                send2trash.send2trash(file)

            return local["NewRenderer"]["info"]["docx_converted"], 0
        except  subprocess.CalledProcessError:
            NewRendererLogger.error(local["NewRenderer"]["error"]["pandoc_error"])
            return local["NewRenderer"]["error"]["pandoc_error"], ErrorCode.PANDOC_ERROR.value
    else: # TEX不用动
        NewRendererLogger.info(local["NewRenderer"]["info"]["tex_converted"])
        return local["NewRenderer"]["info"]["tex_converted"], 0