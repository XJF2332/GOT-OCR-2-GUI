import os
from transformers import AutoModel, AutoTokenizer
import gradio as gr
from PIL import Image
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()


def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    res = "未选择OCR模式"

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
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=f'./ocr.html')
        res = f"rendered as ./ocr.html"
    return res


# gradio gui
with gr.Blocks() as demo:
    gr.Markdown("细粒度OCR设置")
    with gr.Row():
        with gr.Column():
            fine_grained_box_x1 = gr.Number(label="细粒度框x1", value=0)
            fine_grained_box_y1 = gr.Number(label="细粒度框y1", value=0)
        with gr.Column():
            fine_grained_box_x2 = gr.Number(label="细粒度框x2", value=0)
            fine_grained_box_y2 = gr.Number(label="细粒度框y2", value=0)
        with gr.Column():
            fine_grained_color = gr.Dropdown(choices=["红色", "绿色", "蓝色"], label="细粒度颜色")

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

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, OCR_type, fine_grained_color],
        outputs=result
    )

# 启动gradio界面
demo.launch()
