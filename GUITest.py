import os
from transformers import AutoModel, AutoTokenizer
import gradio as gr

tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()


def ocr(image_file, model, tokenizer, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]
    if OCR_type == "ocr":
        res = model.chat(tokenizer, image_file, ocr_type='ocr')
    elif OCR_type == "format":
        res = model.chat(tokenizer, image_file, ocr_type='format')
    elif OCR_type == "fine-grained-ocr":
        res = model.chat(tokenizer, image_file, ocr_type='ocr', ocr_box=box)
    elif OCR_type == "fine-grained-format":
        res = model.chat(tokenizer, image_file, ocr_type='format', ocr_box=box)
    elif OCR_type == "fine-grained-color-ocr":
        res = model.chat(tokenizer, image_file, ocr_type='ocr', ocr_color=fine_grained_color)
    elif OCR_type == "fine-grained-color-format":
        res = model.chat(tokenizer, image_file, ocr_type='format', ocr_color=fine_grained_color)
    elif OCR_type == "multi-crop-ocr":
        res = model.chat_crop(tokenizer, image_file, ocr_type='ocr')
    elif OCR_type == "multi-crop-format":
        res = model.chat_crop(tokenizer, image_file, ocr_type='format')
    elif OCR_type == "render":
        res = model.chat(tokenizer, image_file, ocr_type='format', render=True, save_render_file=f'./{image_file}.html')
    else:
        res = "Invalid OCR Type"
    return res


# gradio gui
with gr.Blocks() as demo:
    gr.Markdown("fine-grained OCR settings")
    with gr.Row():
        with gr.Column():
            fine_grained_box_x1 = gr.Number(label="fine-grained-box-x1", value=0)
            fine_grained_box_y1 = gr.Number(label="fine-grained-box-y1", value=0)
        with gr.Column():
            fine_grained_box_x2 = gr.Number(label="fine-grained-box-x2", value=0)
            fine_grained_box_y2 = gr.Number(label="fine-grained-box-y2", value=0)
        with gr.Column():
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="fine-grained-color")

    with gr.Row():
        with gr.Column():
            upload_img = gr.Image(label="Upload Image")
            OCR_type = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR Type")
        with gr.Column():
            do_ocr = gr.Button("Do OCR")
            result = gr.Textbox(label="Result")

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, model, tokenizer, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, OCR_type, fine_grained_color],
        outputs=result
    )

# launch gradio gui
demo.launch()
