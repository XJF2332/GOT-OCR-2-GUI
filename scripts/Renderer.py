import re
import os
import scripts.HTML2PDF as html2pdf


def render(model: object, tokenizer: object, image_path: str, wait: bool, time: int, convert_to_pdf: bool):
    """
    使用OCR模型渲染图像内容到HTML文件，并可选择性地转换为PDF文件。

    Args:
        model (Model): OCR模型。
        tokenizer (Tokenizer): OCR模型使用的分词器。
        image_path (str): 图像文件的路径。
        wait (bool): 是否等待用户输入。
        time (int): 等待时间（秒）。
        convert_to_pdf (bool): 是否将HTML文件转换为PDF文件。

    Returns:
        bool: 如果成功渲染并转换为PDF文件，则返回True；否则返回False。
    """
    try:
        # 定义输出HTML路径
        img_name = os.path.basename(image_path)
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
        html_utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        html_utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")

        # 渲染OCR结果
        model.chat(tokenizer, image_path, ocr_type='format', render=True, save_render_file=html_gb2312_path)

        # 转换为UTF-8编码
        print(f"[Info-Renderer.render] 正在将文件 '{html_gb2312_path}' 从 GB2312 编码转换为 UTF-8 编码。")
        html2pdf.convert_html_encoding(html_gb2312_path, html_utf8_path)

        # 定义文件路径
        file_path = html_utf8_path

        # 定义要替换的字符串和替换后的字符串
        search_string = '(C)'
        replace_string = r'\(C\\)'

        # 读取文件内容
        try:
            print(f"[Info-Renderer.render] 正在读取文件 '{file_path}'。")
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            content1 = content
            # 使用正则表达式进行替换
            content = re.sub(r'\(C\)', r'(C\\\)', content)

            content1.replace(search_string, replace_string)

            # 将替换后的内容写回文件
            print(f"[Info-Renderer.render] 正在将替换后的内容写回文件 '{file_path}'。")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            print(f"[Info-Renderer.render] 字符串 '{search_string}' 已被替换为 '{replace_string}'。")

        except FileNotFoundError:
            print(f"[Info-Renderer.render] 文件 '{file_path}' 未找到。")
        except Exception as e:
            print(f"[Error-Renderer.render] 发生错误: {e}")

        # 根据参数决定是否转换为PDF
        if convert_to_pdf:
            print(f"[Info-Renderer.render] 正在将文件 '{html_utf8_path}' 转换为 PDF 文件。")
            html2pdf.repalce_html_content(html_utf8_path, html_utf8_local_path)
            pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
            html2pdf.output_pdf(html_utf8_local_path, pdf_path, wait=wait, waiting_time=time)
        return True
    except Exception as e:
        print(f"[Error-Renderer.render] 发生错误: {e}")
        return False
