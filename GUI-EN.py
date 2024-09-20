from transformers import AutoModel, AutoTokenizer
import gradio as gr
import pdfkit
import os
from bs4 import BeautifulSoup
import re

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()
print("Model loaded, launching Webui...")

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
        return f"Succeeded, PDF file saved as：{output_pdf_path}"
    except Exception as e:
        return f"Failed: {e}"


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

    res = "No OCR Mode Selected"

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
        res = f"render result saved as {html_gb2312_path} and {html_utf8_path}"
    return res


# gradio gui
with gr.Blocks() as demo:
    gr.Markdown("fine-grained-ocr Settings")
    with gr.Row():
        with gr.Column():
            fine_grained_box_x1 = gr.Number(label="框x1", value=0)
            fine_grained_box_y1 = gr.Number(label="框y1", value=0)
        with gr.Column():
            fine_grained_box_x2 = gr.Number(label="框x2", value=0)
            fine_grained_box_y2 = gr.Number(label="框y2", value=0)
        with gr.Column():
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="颜色")

    gr.Markdown("OCR Settings")

    with gr.Row():
        with gr.Column():
            OCR_type = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR Mode")
            upload_img = gr.Image(type="filepath", label="Upload Image")
        with gr.Column():
            do_ocr = gr.Button("DO OCR")
            result = gr.Textbox(label="Result")
            with gr.Row():
                html_path = gr.Textbox(label="HTML File Path", value="./result/ocr_utf8.html")
                pdf_path = gr.Textbox(label="PDF File Path", value="./result/ocr_utf8.pdf")
            with gr.Row():
                save_as_pdf = gr.Button("Save as PDF")
                save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    gr.Markdown("""
    ### Instructions
    #### OCR Modes
    - ocr: Standard OCR
    - format: OCR with formatting
    #### Fine-Grained Modes
    - fine-grained-ocr: OCR content within a specific box
    - fine-grained-format: OCR and format content within a specific box
    - fine-grained-color-ocr: OCR content within a box of a specific color (I haven't tried this, but it seems like you would need to draw a red/green/blue box first and then select the color in the GUI)
    - fine-grained-color-format: OCR and format content within a box of a specific color
    #### Multi-Crop Modes
    - Suitable for more complex images
    #### Render Modes
    - Exist files will be overwritten!!!Check the file path before clicking the button!!!
    - Render OCR content and save it as an HTML file
    - Will be saved as UTF8 encoding and GB2312 encoding files
    - You can convert HTML to PDF
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
