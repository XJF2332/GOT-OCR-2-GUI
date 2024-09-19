from transformers import AutoModel, AutoTokenizer
import gradio as gr

tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()


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
        convert_html_encoding("./ocr.html", "./ocr_utf8.html")
        res = f"渲染结果已保存为 ./ocr.html 和 ./ocr_utf8.html"
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
                save_as_pdf = gr.Button("保存为PDF")
                save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    gr.Markdown("""
    ### 使用教程
    #### ocr模式
    - ocr：普通的ocr
    - format：ocr并格式化
    #### fine-grained模式
    - fine-grained-ocr：ocr特定的框中的内容
    - fine-grained-format：ocr并格式化特定的框中的内容
    - fine-grained-color-ocr：ocr特定颜色的框中的内容（我还没用过，大概是要先用红/绿/蓝色画框再在GUI里选择颜色）
    - fine-grained-color-format：ocr并格式化特定颜色的框中的内容
    #### multi-crop模式
    - 适用于更复杂的图片
    """)

    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, OCR_type, fine_grained_color],
        outputs=result
    )

# 启动gradio界面
demo.launch()
