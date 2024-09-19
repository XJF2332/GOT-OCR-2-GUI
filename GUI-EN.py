from transformers import AutoModel, AutoTokenizer
import gradio as gr


tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()


def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color):
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    res = "No OCR mode selected"

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
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=f'tests/ocr.html')
        res = f"rendered as ./ocr.html"
    return res


# gradio gui
with gr.Blocks() as demo:
    gr.Markdown("fine-grained-ocr settings")
    with gr.Row():
        with gr.Column():
            fine_grained_box_x1 = gr.Number(label="Box x1", value=0)
            fine_grained_box_y1 = gr.Number(label="Box y1", value=0)
        with gr.Column():
            fine_grained_box_x2 = gr.Number(label="Box x2", value=0)
            fine_grained_box_y2 = gr.Number(label="Box y2", value=0)
        with gr.Column():
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="color")

    gr.Markdown("OCR settings")

    with gr.Row():
        with gr.Column():
            OCR_type = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR Mode")
            upload_img = gr.Image(type="filepath", label="Upload Image")
        with gr.Column():
            do_ocr = gr.Button("DO OCR")
            result = gr.Textbox(label="result")

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
    """)

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, OCR_type, fine_grained_color],
        outputs=result
    )

# 启动gradio界面
demo.launch()
