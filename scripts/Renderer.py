import re
import os
import scripts.HTML2PDF as html2pdf
# from IPython.display import clear_output
# from IPython.display import display
# from IPython.display import Latex


def render(model, tokenizer, image_path, wait, time, convert_to_pdf):
    """
    使用OCR模型渲染图像内容到HTML文件，并可选择性地转换为PDF文件。

    参数:
    - model: object
        用于执行OCR的模型实例。
    - tokenizer: object
        用于处理文本的tokenizer实例。
    - image_path: str
        待处理图像的文件路径。
    - wait: bool
        是否等待页面加载完成。默认为False
    - time: int
        等待页面加载的时间（秒）。默认为10
    - convert_to_pdf: bool
        是否将生成的HTML文件转换为PDF文件。

    功能:
    - 使用OCR模型对图像进行识别，并将识别结果渲染到HTML文件中。
    - 将渲染的HTML文件从GB2312编码转换为UTF-8编码。
    - 可选地将HTML文件中的特定字符串进行替换。
    - 如果`convert_to_pdf`为True，则将HTML文件转换为PDF文件。

    返回:
    - bool
        如果整个过程成功完成，返回True；如果过程中发生任何错误，返回False。

    注意:
    - `image_path`必须指向一个有效的图像文件。
    - 生成的HTML和PDF文件将保存在`result`目录下，该目录必须存在且可写。
    - 如果`convert_to_pdf`为True，则函数将尝试生成PDF文件，这要求系统中已安装相应的浏览器驱动。
    """
    try:
        # 定义输出HTML路径
        img_name = os.path.basename(image_path)
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
        html_utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        html_utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")

        # 生成Latex格式的结果
        # res = model.chat_crop(tokenizer, image_path, ocr_type='format')
        # display(Latex(res))

        # 渲染OCR结果
        model.chat(tokenizer, image_path, ocr_type='format', render=True, save_render_file=html_gb2312_path)

        # 转换为UTF-8编码
        html2pdf.convert_html_encoding(html_gb2312_path, html_utf8_path)

        # 定义文件路径
        file_path = html_utf8_path

        # 定义要替换的字符串和替换后的字符串
        search_string = '(C)'
        replace_string = r'\(C\\)'

        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            content1 = content
            # 使用正则表达式进行替换
            content = re.sub(r'\(C\)', r'(C\\\)', content)

            content1.replace(search_string, replace_string)

            # 将替换后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            print(f"[debug] 字符串 '{search_string}' 已被替换为 '{replace_string}'。")

        except FileNotFoundError:
            print(f"[debug] 文件 '{file_path}' 未找到。")
        except Exception as e:
            print(f"[debug] 发生错误: {e}")

        # 根据参数决定是否转换为PDF
        if convert_to_pdf:
            html2pdf.repalce_html_content(html_utf8_path, html_utf8_local_path)
            pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
            html2pdf.output_pdf(html_utf8_local_path, pdf_path, wait=wait, waiting_time=time)
        return True
    except:
        return False
