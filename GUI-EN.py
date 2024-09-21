print("Importing packages...")

from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import re
import html2pdf

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

model = model.eval().cuda()
print("Model loaded, launching Webui...")



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
    return f"PDF saved as {pdf_path}"

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

    res = "No OCR Mode Selected"

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
        res = f"render result saved as {html_gb2312_path} and {html_utf8_path}"
    return res


# gradio gui
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown("fine-grained-ocr settings")
            with gr.Row():
                with gr.Column():
                    fine_grained_box_x1 = gr.Number(label="Box x1", value=0)
                    fine_grained_box_y1 = gr.Number(label="Box y1", value=0)
                with gr.Column():
                    fine_grained_box_x2 = gr.Number(label="Box x2", value=0)
                    fine_grained_box_y2 = gr.Number(label="Box y2", value=0)
            fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label="Color")
        with gr.Column():
            gr.Markdown("render mode settings")
            with gr.Row():
                img_name = gr.Textbox(label="Image Name", value="ocr")
                submit_name = gr.Button("Submit Image Name")
            with gr.Row():
                html_utf8_path = gr.Textbox(label="HTML File Path", value="./result/ocr-utf8.html", interactive=False)
                html_utf8_local_path = gr.Textbox(label="HTML Local File Path", value="./result/ocr-utf8-local.html", interactive=False)
                pdf_path = gr.Textbox(label="PDF File Path", value="./result/ocr-utf8.pdf", interactive=False)


    gr.Markdown("OCR Settings")

    with gr.Row():
        upload_img = gr.Image(type="filepath", label="Upload Image")
        with gr.Column():
            ocr_mode = gr.Dropdown(
                choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                         "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                label="OCR Mode")
            do_ocr = gr.Button("DO OCR")
            result = gr.Textbox(label="Result")
            with gr.Row():
                save_as_pdf = gr.Button("Save as PDF")
                save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    gr.Markdown("""
    
    ## Instructions
    ---
    ### Modes
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
    ---
    ### How to render
    1. Input image name in the text box, this will become the base name of the output files
    2. Click the "Submit Image Name" button to apply the name
    3. You will find that three textboxes below changed, which means the name has been applied
    4. Click the "Save as PDF" button to save the HTML file as a PDF file
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
