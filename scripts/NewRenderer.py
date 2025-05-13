import subprocess
import os
from scripts import ErrorCode, local, scriptsLogger
from scripts import TeXComplete
import send2trash

available_outputs = ["pdf", "markdown", "docx", "tex"]
NewRendererLogger = scriptsLogger.getChild("NewRenderer")

def render(raw_tex: str, output_format: str, output_name: str = "output") -> tuple:
    """
    把tex文本转换成其他格式，保存到result文件夹

    :param raw_tex: 原始的tex文本
    :param output_format: 输出格式，支持"tex"、"pdf"、"markdown"、"docx"，只能选择一种
    :param output_name: 输出文件名
    :return: 运行状态，成功则返回0
    """
    temp_files = []
    # 无效的输出格式
    if output_format not in available_outputs:
        NewRendererLogger.error(
            local["NewRenderer"]["error"]["invalid_out_format"].format(format=output_format))
        return (local["NewRenderer"]["error"]["invalid_out_format"],
                ErrorCode.INVALID_OUTPUT_FORMAT.value)

    # 补全tex格式并保存
    completed_tex = TeXComplete.complete_tex(raw_tex)
    out_tex_path_abs = os.path.abspath(os.path.join("result", f"{output_name}.tex"))
    with open(out_tex_path_abs, "w", encoding="utf-8") as f:
        f.write(completed_tex)

    # 转换
    # PDF
    if output_format == "pdf":
        try:
            subprocess.run(["pdflatex", out_tex_path_abs,
                            f"-output-directory={os.path.abspath('result')}"],
                            check=True, stderr=subprocess.PIPE)
            
            # 清理临时文件
            temp_files.append(out_tex_path_abs)
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.aux")))
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.log")))
            temp_files.append(os.path.abspath(os.path.join("result", f"{output_name}.out")))
            for file in temp_files:
                send2trash.send2trash(file)

            NewRendererLogger.info(local["NewRenderer"]["info"]["pdf_converted"])
            return local["NewRenderer"]["info"]["pdf_converted"], 0
        # 报错
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = local["NewRenderer"]["error"]["pdflatex_error"].format(error=error_msg)
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PDFLATEX_ERROR.value
    # Markdown
    elif output_format == "markdown":
        try:
            subprocess.run(["pandoc", out_tex_path_abs, "-o",
                            os.path.abspath(os.path.join("result", f"{output_name}.md"))],
                            check=True, stderr=subprocess.PIPE)

            temp_files.append(out_tex_path_abs)
            for file in temp_files:
                send2trash.send2trash(file)
            # 虽然我知道这里要干什么但空着一行不加点注释总觉得不好看
            NewRendererLogger.info(local["NewRenderer"]["info"]["markdown_converted"])
            return local["NewRenderer"]["info"]["markdown_converted"], 0
        # 报错
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = local["NewRenderer"]["error"]["pandoc_error"].format(error=error_msg)
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PANDOC_ERROR.value
    # Docx (Word)
    elif output_format == "docx":
        try:
            subprocess.run(["pandoc", out_tex_path_abs, "-o",
                            os.path.abspath(os.path.join("result", f"{output_name}.docx"))],
                            check=True, stderr=subprocess.PIPE)
            # 删除临时文件
            temp_files.append(out_tex_path_abs)
            for file in temp_files:
                send2trash.send2trash(file)

            NewRendererLogger.info(local["NewRenderer"]["info"]["docx_converted"])
            return local["NewRenderer"]["info"]["docx_converted"], 0
        # 报错处理
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8").strip() if e.stderr else "Unknown error"
            full_error = local["NewRenderer"]["error"]["pandoc_error"].format(error=error_msg)
            NewRendererLogger.error(full_error)
            return full_error, ErrorCode.PANDOC_ERROR.value
    # tex不需要做什么
    else:
        NewRendererLogger.info(local["NewRenderer"]["info"]["tex_converted"])
        return local["NewRenderer"]["info"]["tex_converted"], 0