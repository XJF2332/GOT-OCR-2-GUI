import json
import os

print("Loading config...")

with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

print(local["import_libs"])

from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import re
import scripts.html2pdf as html2pdf

print(local["load_model"])
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()
print(local["model_loaded"])


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
    success = local["pdf_save_success"].format(pdf_path=pdf_path)
    return success


def build_name(img_name):
    html_gb2312_path = os.path.join("result", f"{img_name}-gb2312.html")
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    return [html_gb2312_path, html_utf8_path]


def func_submit_name(img_name):
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    html_utf8_local_path = os.path.join("result", f"{img_name}-utf8-local.html")
    pdf_path = os.path.join("result", f"{img_name}-utf8.pdf")
    return html_utf8_path, html_utf8_local_path, pdf_path


def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, img_name):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    res = local["ocr_mode_none"]

    html_gb2312_path = build_name(img_name)[0]
    html_utf8_path = build_name(img_name)[1]

    if not os.path.exists("result"):
        os.makedirs("result")

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
        res = local["render_save_success"].format(html_utf8_path=html_utf8_path, html_gb2312_path=html_gb2312_path)
    return res


# gradio gui
with gr.Blocks() as demo:
    with gr.Tab(local["tab_ocr"]):
        with gr.Row():
            with gr.Column():
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
                gr.Markdown(local["render_settings"])
                with gr.Row():
                    img_name = gr.Textbox(label=local["img_name"], value="ocr")
                    submit_name = gr.Button(local["submit_img_name"])
                with gr.Row():
                    html_utf8_path = gr.Textbox(label=local["html_file_path"], value=os.path.join("result", "ocr-utf8.html"), interactive=False)
                    html_utf8_local_path = gr.Textbox(label=local["html_local_file_path"], value=os.path.join("result", "ocr-utf8-local.html"),
                                                      interactive=False)
                    pdf_path = gr.Textbox(label=local["pdf_file_path"], value=os.path.join("result", "ocr-utf8.pdf"), interactive=False)

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

    with gr.Tab(local["tab_instructions"]):
        with open(os.path.join('Locales','gui','instructions',f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()

        gr.Markdown(instructions)

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
