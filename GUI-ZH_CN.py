print("正在导入库...")

from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import re
import html2pdf

print("正在加载模型...")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()
print("模型加载成功，正在启动 Webui...")


def convert_html_encoding(input_file_path, output_file_path):
    # 以GB2312编码读取文件
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # 以UTF-8写入内容到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def repalce_html_content(input_file_path, output_file_path):
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)


def func_save_as_pdf(html_utf8_path, html_utf8_local_path, pdf_path):
    repalce_html_content(html_utf8_path, html_utf8_local_path)
    html2pdf.output_pdf(html_utf8_local_path, pdf_path)
    return f"PDF 已保存为{pdf_path}"


def build_name(img_name):
    html_gb2312_path = f"./result/{img_name}-gb2312.html"
    html_utf8_path = f"./result/{img_name}-utf8.html"
    return [html_gb2312_path, html_utf8_path]


def func_submit_name(img_name):
    html_utf8_path = f"./result/{img_name}-utf8.html"
    html_utf8_local_path = f"./result/{img_name}-utf8-local.html"
    pdf_path = f"./result/{img_name}-utf8.pdf"
    return html_utf8_path, html_utf8_local_path, pdf_path


def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, img_name):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    res = "未选择 OCR 模式"

    html_gb2312_path = build_name(img_name)[0]
    html_utf8_path = build_name(img_name)[1]

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
    with gr.Row():
        with gr.Column():
            gr.Markdown("fine-grained-ocr 设置")
            with gr.Row():
                with gr.Column():
                    fine_grained_box_x1 = gr.Number(label="框坐标 x1", value=0)
                    fine_grained_box_y1 = gr.Number(label="框坐标 y1", value=0)
                with gr.Column():
                    fine_grained_box_x2 = gr.Number(label="框坐标 x2", value=0)
                    fine_grained_box_y2 = gr.Number(label="框坐标 y2", value=0)
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="颜色")
        with gr.Column():
            gr.Markdown("渲染模式设置")
            with gr.Row():
                img_name = gr.Textbox(label="图像名称", value="ocr")
                submit_name = gr.Button("Submit Image Name")
            with gr.Row():
                html_utf8_path = gr.Textbox(label="HTML File Path", value="./result/ocr-utf8.html", interactive=False)
                html_utf8_local_path = gr.Textbox(label="HTML Local File Path", value="./result/ocr-utf8-local.html",
                                                  interactive=False)
                pdf_path = gr.Textbox(label="PDF File Path", value="./result/ocr-utf8.pdf", interactive=False)

    gr.Markdown("OCR 设置")

    with gr.Row():
        upload_img = gr.Image(type="filepath", label="上传图像")
        with gr.Column():
            ocr_mode = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR 模式")
            do_ocr = gr.Button("执行 OCR")
            result = gr.Textbox(label="结果")
            with gr.Row():
                save_as_pdf = gr.Button("保存为 PDF")
                save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    gr.Markdown("""
    ## 使用说明
    ### **模式**
    #### `OCR` 模式
    - ocr: 标准OCR
    - format: 带格式化的OCR
    #### `fine-grained` 模式
    - fine-grained-ocr: 在特定框内进行OCR内容识别
    - fine-grained-format: 在特定框内进行OCR内容识别并格式化
    - fine-grained-color-ocr: 在特定颜色的框内进行OCR内容识别（我还没尝试过这个，但看起来你需要先画一个红/绿/蓝色的框，然后在GUI中选择颜色）
    - fine-grained-color-format: 在特定颜色的框内进行OCR内容识别并格式化
    #### `multi-crop` 模式
    - 适用于更复杂的图像
    #### `render` 模式
    - 已存在的文件将被覆盖！！！点击按钮前请检查文件路径！！！
    - 渲染OCR内容并将其保存为HTML文件
    - 将保存为UTF8编码和GB2312编码的文件
    - 你可以将HTML转换为PDF
    ### **如何渲染**
    1. 在文本框中输入图像名称，这将变成输出文件的基本名称
    2. 点击“提交图像名称”按钮以应用名称
    3. 你会发现下面的三个文本框发生了变化，这意味着名称已被应用
    4. 点击“保存为PDF”按钮以将HTML文件保存为PDF文件
    """)

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, img_name],
        outputs=result
    )
    save_as_pdf.click(
        fn=func_save_as_pdf,
        inputs=[html_utf8_path, html_utf8_local_path, pdf_path],
        outputs=save_as_pdf_info
    )
    submit_name.click(
        fn=func_submit_name,
        inputs=[img_name],
        outputs=[html_utf8_path, html_utf8_local_path, pdf_path]
    )

# 启动gradio界面
demo.launch()
