from transformers import AutoModel, AutoTokenizer
import gradio as gr
import pdfkit
import os
from bs4 import BeautifulSoup
import re

print("正在加载模型......")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()

print("加载完成，正在启动Webui......")

config = pdfkit.configuration(wkhtmltopdf='wkhtmltopdf\\bin\wkhtmltopdf.exe')


def extract_style_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    style_tag = soup.find('style')
    return style_tag.string if style_tag else ''


def extract_const_text_from_script(script_content):
    # 使用正则表达式来匹配所有被双引号包围的字符串，并保留换行符
    string_pattern = r'(?<!\\)"(.*?)(?<!\\)"'
    matches = re.findall(string_pattern, script_content, re.DOTALL)
    # 将所有匹配的字符串连接起来，并替换掉转义引号
    const_text = ''.join(matches).replace('\\"', '"')
    # 替换JavaScript的换行符为HTML的换行符
    const_text = const_text.replace('\\n', '<br>')
    return const_text


def const_text_to_pdf(input_html_path, output_pdf_path):
    try:
        with open(input_html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 提取<style>标签内容
        style_content = extract_style_from_html(html_content)

        # 提取<script>标签内容
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script')
        script_content = script_tag.string if script_tag else ''

        # 提取const text内容
        const_text = extract_const_text_from_script(script_content)

        # 构建完整的HTML文档，包含提取的<style>标签和const text内容
        styled_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {style_content}
            </style>
        </head>
        <body>
            <pre>{const_text}</pre>
        </body>
        </html>
        """

        if not os.path.exists("./result"):
            os.makedirs("./result")

        # 将const text内容转换为PDF
        pdfkit.from_string(styled_text, output_pdf_path, configuration=config)
        return f"转换完成，PDF文件已保存为：{output_pdf_path}"
    except Exception as e:
        return f"转换失败：{e}"


def convert_html_encoding(input_file_path, output_file_path):
    # 以GB2312编码读取文件
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # 以UTF-8编码写入内容到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    res = "未选择OCR模式"

    html_gb2312_path = "./result/ocr_gb2312.html"
    html_utf8_path = "./result/ocr_utf8.html"

    if not os.path.exists("./result"):
        os.makedirs("./result")

    if OCR_type == "ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr')
    elif OCR_type == "format":
        res = model.chat(tokenizer, image, ocr_type='format')
    elif OCR_type == "fine-grained-ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
    elif OCR_type == "fine-grained-format":
        res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
    elif OCR_type == "fine-grained-color-ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=fine_grained_color)
    elif OCR_type == "fine-grained-color-format":
        res = model.chat(tokenizer, image, ocr_type='format', ocr_color=fine_grained_color)
    elif OCR_type == "multi-crop-ocr":
        res = model.chat_crop(tokenizer, image, ocr_type='ocr')
    elif OCR_type == "multi-crop-format":
        res = model.chat_crop(tokenizer, image, ocr_type='format')
    elif OCR_type == "render":
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        res = f"渲染结果已保存为 {html_gb2312_path} 和 {html_utf8_path}"
    return res


# gradio gui
with gr.Blocks() as demo:
    gr.Markdown("fine-grained-ocr设置")
    with gr.Row():
        with gr.Column():
            fine_grained_box_x1 = gr.Number(label="框x1", value=0)
            fine_grained_box_y1 = gr.Number(label="框y1", value=0)
        with gr.Column():
            fine_grained_box_x2 = gr.Number(label="框x2", value=0)
            fine_grained_box_y2 = gr.Number(label="框y2", value=0)
        with gr.Column():
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="颜色")

    gr.Markdown("OCR设置")

    with gr.Row():
        with gr.Column():
            OCR_type = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR类型")
            upload_img = gr.Image(type="filepath", label="上传图片")
        with gr.Column():
            do_ocr = gr.Button("执行OCR")
            result = gr.Textbox(label="结果")
            with gr.Row():
                html_path = gr.Textbox(label="HTML文件路径", value="./result/ocr_utf8.html")
                pdf_path = gr.Textbox(label="PDF文件路径", value="./result/ocr_utf8.pdf")
            with gr.Row():
                save_as_pdf = gr.Button("保存为PDF")
                save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    gr.Markdown("""
    ## 使用教程
    ### **模式选择**
    #### `ocr`模式
    - ocr：普通的 ocr
    - format：ocr 并格式化
    #### `fine-grained`模式
    - fine-grained-ocr：ocr 特定的框中的内容
    - fine-grained-format：ocr 并格式化特定的框中的内容
    - fine-grained-color-ocr：ocr 特定颜色的框中的内容（我还没用过，大概是要先用红/绿/蓝色画框再在 GUI 里选择颜色）
    - fine-grained-color-format：ocr 并格式化特定颜色的框中的内容
    #### `multi-crop`模式
    - 适用于更复杂的图片
    #### `render`模式
    - 已经存在的文件会被覆盖！！！渲染前查看是否有以及存在的文件！！！
    - 渲染图片中的文字，并保存为 html 文件
    - 同时具有 GB2312 和 UTF8 编码
    - 可以转换 html 为 pdf ， pdf 为 UTF8 编码
    ### **使用`render`模式**
    """)

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, OCR_type, fine_grained_color],
        outputs=result
    )
    save_as_pdf.click(
        fn=const_text_to_pdf,
        inputs=[html_path, pdf_path],
        outputs=save_as_pdf_info
    )

# 启动gradio界面
demo.launch()
