import json
import os

# 从config.json文件中加载配置
print("Loading config...")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

# 从对应语言的json文件中加载本地化字符串
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# 导入库
print(local["import_libs"])
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import re
import scripts.html2pdf as html2pdf

# 加载模型
print(local["load_model"])
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print(local["model_loaded"])


# 将文件以GB2312编码读取，并以UTF-8编码写入新文件
def convert_html_encoding(input_file_path, output_file_path):
    # 以GB2312编码读取文件
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # 以UTF-8写入内容到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# 替换html文件中的内容
def replace_html_content(input_file_path, output_file_path):
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)


# 将html文件转换为pdf文件
def func_save_as_pdf(html_utf8_path, html_utf8_local_path, pdf_path):
    # 替换html文件中的内容
    replace_html_content(html_utf8_path, html_utf8_local_path)
    # 将html文件转换为pdf文件
    html2pdf.output_pdf(html_utf8_local_path, pdf_path)
    # 打印pdf保存成功
    success = local["pdf_save_success"].format(pdf_path=pdf_path)
    return success


# 构建文件名
def build_name(img_name):
    # 构建html文件名
    html_gb2312_path = os.path.join("result", f"{img_name}-gb2312.html")
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    return [html_gb2312_path, html_utf8_path]


# 提交文件名
def func_submit_name(img_name):
    # 构建html文件名
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    html_utf8_local_path = os.path.join("result", f"{img_name}-utf8-local.html")
    pdf_path = os.path.join("result", f"{img_name}-utf8.pdf")
    return html_utf8_path, html_utf8_local_path, pdf_path


# 进行OCR识别
def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, img_name):
    # 构建OCR框
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    # 未选择模式
    res = local["ocr_mode_none"]

    # 构建html文件名
    html_gb2312_path = build_name(img_name)[0]
    html_utf8_path = build_name(img_name)[1]

    # 如果result文件夹不存在，则创建
    if not os.path.exists("result"):
        os.makedirs("result")

    # 根据OCR类型进行OCR识别
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
        # 进行渲染
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        # 将文件以GB2312编码读取，并以UTF-8编码写入新文件
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        # 打印渲染保存成功
        res = local["render_save_success"].format(html_utf8_path=html_utf8_path, html_gb2312_path=html_gb2312_path)
    return res


# gradio gui
with gr.Blocks() as demo:
    # OCR选项卡
    with gr.Tab(local["tab_ocr"]):
        with gr.Row():
            with gr.Column():
                # Fine-grained 设置
                gr.Markdown(local["fine_grained_settings"])
                with gr.Row():
                    with gr.Column():
                        fine_grained_box_x1 = gr.Number(label=local["fine_grained_box_x1"], value=0)
                        fine_grained_box_y1 = gr.Number(label=local["fine_grained_box_y1"], value=0)
                    with gr.Column():
                        fine_grained_box_x2 = gr.Number(label=local["fine_grained_box_x2"], value=0)
                        fine_grained_box_y2 = gr.Number(label=local["fine_grained_box_y2"], value=0)
                fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label=local["fine_grained_color"])
            with gr.Column():
                # 渲染设置
                gr.Markdown(local["render_settings"])
                with gr.Row():
                    img_name = gr.Textbox(label=local["img_name"], value="ocr")
                    submit_name = gr.Button(local["submit_img_name"])
                with gr.Row():
                    html_utf8_path = gr.Textbox(label=local["html_file_path"],
                                                value=os.path.join("result", "ocr-utf8.html"), interactive=False)
                    html_utf8_local_path = gr.Textbox(label=local["html_local_file_path"],
                                                      value=os.path.join("result", "ocr-utf8-local.html"),
                                                      interactive=False)
                    pdf_path = gr.Textbox(label=local["pdf_file_path"], value=os.path.join("result", "ocr-utf8.pdf"),
                                          interactive=False)
        # OCR设置
        gr.Markdown(local["ocr_settings"])

        with gr.Row():
            upload_img = gr.Image(type="filepath", label=local["upload_img"])
            with gr.Column():
                ocr_mode = gr.Dropdown(
                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                             "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                    label=local["ocr_mode"])
                do_ocr = gr.Button(local["do_ocr_btn"])
                result = gr.Textbox(label=local["result"])
                with gr.Row():
                    save_as_pdf = gr.Button(local["save_as_pdf"])
                    save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)
    # 指南选项卡
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()
        # 显示指南
        gr.Markdown(instructions)

    # 点击进行OCR识别
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, img_name],
        outputs=result
    )
    # 点击保存为pdf
    save_as_pdf.click(
        fn=func_save_as_pdf,
        inputs=[html_utf8_path, html_utf8_local_path, pdf_path],
        outputs=save_as_pdf_info
    )
    # 点击提交图片名
    submit_name.click(
        fn=func_submit_name,
        inputs=[img_name],
        outputs=[html_utf8_path, html_utf8_local_path, pdf_path]
    )

# 启动gradio界面
demo.launch()
