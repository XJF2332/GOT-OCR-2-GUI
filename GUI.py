import json
import os

# Load language settings
print("[Info-GUI] Loading language settings")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# Load configuration
print("[Info-GUI] Loading configuration")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# Import libraries
print("[Info-GUI] Importing libraries")
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler
import scripts.PDFMerger as PDFMerger

model = None
tokenizer = None


# Load model function
def load_model():
    print("[Info-GUI] Loading model")
    global model, tokenizer
    model = None
    tokenizer = None
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    print("[Info-GUI] Model loaded")
    return local["info_model_already_loaded"]


# Unload model function
def unload_model():
    global model, tokenizer
    model = None
    tokenizer = None
    return local["info_model_not_loaded"]


# Decide whether to load the model on startup
if config["load_model_on_start"]:
    load_model()
else:
    print("[Info-GUI] Model loading skipped")

# Theme setup
try:
    theme = gr.themes.Ocean(
        primary_hue="indigo",
        secondary_hue="violet",
        radius_size="sm",
    ).set(
        body_background_fill='*neutral_50',
        body_background_fill_dark='*neutral_950',
        body_text_color='*neutral_950',
        body_text_color_dark='*neutral_200',
        background_fill_secondary='*neutral_100',
        button_transform_active='scale(0.98)',
        button_large_radius='*radius_sm',
        button_small_radius='*radius_sm'
    )
except AttributeError:
    print("[Warning-GUI] Ocean theme not available, using default theme")
    theme = gr.themes.Default()



# Update image name
def update_img_name(image_uploaded):
    image_name_with_extension = os.path.basename(image_uploaded)
    return gr.Textbox(label=local["label_img_name"], value=image_name_with_extension)


# Update PDF name
def update_pdf_name(pdf_uploaded):
    pdf_name_with_extension = os.path.basename(pdf_uploaded)
    return gr.Textbox(label=local["label_pdf_file"], value=pdf_name_with_extension)


# Update visibility of PDF conversion checkbox (PDF tab)
def update_pdf_pdf_convert_confirm_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "render":
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=False, value=False)


# Update visibility of PDF merge checkbox (PDF tab)
def update_pdf_pdf_merge_confirm_visibility(pdf_convert_confirm):
    if pdf_convert_confirm:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=False, value=False)


# Update visibility of target DPI input (PDF tab)
def update_pdf_pdf_dpi_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "merge":
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=False)
    else:
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=True)


# Extract prefix
def extract_pdf_pattern(filename):
    """
    Extract the prefix from a filename. If the filename does not match the format <string>_0.pdf,
    raise ValueError.
    :param filename: The filename to process
    :return: The extracted prefix
    """
    # Split the filename at the last underscore
    parts = filename.rsplit('_', 1)

    # Check if the last part is '0.pdf'
    if len(parts) == 2 and parts[1] == '0.pdf':
        return parts[0]
    else:
        raise ValueError("[GUI.extract_pdf_pattern] Input does not match format: <string>_0.pdf")


# Perform OCR
def ocr(image_uploaded, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, pdf_convert_confirm):
    # Build the OCR box
    print("[Info-GUI.ocr] Building bounding box")
    box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"

    # Default value
    res = local["error_ocr_mode_none"]

    # If the result directory does not exist, create it
    if not os.path.exists("result"):
        print("[Debug-GUI.ocr] Result folder does not exist; creating")
        os.makedirs("result")

    try:
        # Perform OCR based on the selected mode
        print("[Info-GUI.ocr] Performing OCR")
        if OCR_type == "ocr":
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr')
        elif OCR_type == "format":
            res = model.chat(tokenizer, image_uploaded, ocr_type='format')
        elif OCR_type == "fine-grained-ocr":
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr', ocr_box=box)
        elif OCR_type == "fine-grained-format":
            res = model.chat(tokenizer, image_uploaded, ocr_type='format', ocr_box=box)
        elif OCR_type == "fine-grained-color-ocr":
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr', ocr_color=fine_grained_color)
        elif OCR_type == "fine-grained-color-format":
            res = model.chat(tokenizer, image_uploaded, ocr_type='format', ocr_color=fine_grained_color)
        elif OCR_type == "multi-crop-ocr":
            res = model.chat_crop(tokenizer, image_uploaded, ocr_type='ocr')
        elif OCR_type == "multi-crop-format":
            res = model.chat_crop(tokenizer, image_uploaded, ocr_type='format')
        elif OCR_type == "render":
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_uploaded,
                                      convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                      time=config["pdf_render_wait_time"])
            image_name_with_extension = os.path.basename(image_uploaded)
            if success:
                res = local["info_render_success"].format(img_file=image_name_with_extension)
            else:
                res = local["error_render_fail"].format(img_file=image_name_with_extension)
        return res
    except Exception as e:
        return str(e)


# PDF OCR
def pdf_ocr(mode, pdf_file, target_dpi, pdf_convert, pdf_merge):
    pdf_name = os.path.basename(pdf_file)
    if mode == "split-to-image":
        print("[Info-GUI] Splitting PDF file")
        success = PDFHandler.split_pdf(pdf_path=pdf_file, img_path="imgs", target_dpi=target_dpi)
        if success:
            print("[Info-GUI] PDF split successful")
            gr.Info(message=local["info_pdf_split_success"].format(pdf_file=pdf_name))
        else:
            print("[Error-GUI] PDF split failed")
            raise gr.Error(duration=0, message=local["error_pdf_split_fail"].format(pdf_file=pdf_name))
    elif mode == "render":
        print(f"[Info-GUI] Starting to render PDF file: {pdf_name}")
        gr.Info(message=local["info_pdf_render_start"].format(pdf_file=pdf_name))
        success = PDFHandler.pdf_renderer(model=model, tokenizer=tokenizer, pdf_path=pdf_file, target_dpi=target_dpi,
                                          pdf_convert=pdf_convert, wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        if success:
            print(f"[Info-GUI] PDF render successful: {pdf_name}")
            gr.Info(message=local["info_pdf_render_success"].format(pdf_file=pdf_name))
        else:
            print(f"[Error-GUI] PDF render failed: {pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_render_fail"].format(pdf_file=pdf_name))
        if pdf_merge:
            print(f"[Info-GUI] Starting to merge PDF files: {pdf_name}")
            gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
            success = PDFMerger.merge_pdfs(prefix=pdf_name)
            if success:
                print(f"[Info-GUI] PDF merge successful: {pdf_name}")
                gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
            else:
                print(f"[Error-GUI] PDF merge failed: {pdf_name}")
                raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))
        else:
            gr.Warning(message=local["info_pdf_merge_skip"].format(pdf_file=pdf_name))
            print(f"[Info-GUI] Skipping PDF merge: {pdf_name}")
    elif mode == "merge":
        print(f"[Info-GUI] Starting to merge PDF files: {pdf_name}")
        gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
        prefix = extract_pdf_pattern(pdf_name)
        success = PDFMerger.merge_pdfs(prefix=prefix)
        if success:
            print(f"[Info-GUI] PDF merge successful: {pdf_name}")
            gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
        else:
            print(f"[Error-GUI] PDF merge failed: {pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))


# Renderer
def renderer(imgs_path, pdf_convert_confirm):
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

    # Send each image to the renderer's render function
    for image_path in image_files:
        print(f"[Info-GUI] Starting rendering: {image_path}")
        success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                  convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                  time=config["pdf_render_wait_time"])
        if success:
            print(f"[Info-GUI] Render successful: {image_path}")
        else:
            raise gr.Error(duration=0, message=local["error_render_fail"].format(img_file=image_path))


# Gradio GUI
with gr.Blocks(theme=theme) as demo:
    # Model panel
    with gr.Row(variant="panel", equal_height=True):
        if config["load_model_on_start"]:
            model_status = gr.Textbox(local["info_model_already_loaded"], show_label=False)
        else:
            model_status = gr.Textbox(local["info_model_not_loaded"], show_label=False)
        unload_model_btn = gr.Button(local["btn_unload_model"], variant="secondary")
        load_model_btn = gr.Button(local["btn_load_model"], variant="primary")

    # OCR tab
    with gr.Tab(local["tab_ocr"]):
        with gr.Row():
            with gr.Column():
                # Fine-grained settings
                gr.Markdown(local["label_fine_grained_settings"])
                with gr.Row():
                    fine_grained_box_x1 = gr.Number(label=local["label_fine_grained_box_x1"], value=0)
                    fine_grained_box_y1 = gr.Number(label=local["label_fine_grained_box_y1"], value=0)
                    fine_grained_box_x2 = gr.Number(label=local["label_fine_grained_box_x2"], value=0)
                    fine_grained_box_y2 = gr.Number(label=local["label_fine_grained_box_y2"], value=0)
                fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"],
                                                 label=local["label_fine_grained_color"], value="red")

            with gr.Column():
                # Render settings
                gr.Markdown(local["label_render_settings"])
                img_name = gr.Textbox(label=local["label_img_name"], value="ocr")
                pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"])

        # OCR
        gr.Markdown(local["label_ocr_settings"])
        with gr.Row():
            upload_img = gr.Image(type="filepath", label=local["label_upload_img"])
            with gr.Column():
                ocr_mode = gr.Dropdown(
                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr", "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                    label=local["label_ocr_mode"], value="format")

                do_ocr = gr.Button(local["btn_do_ocr"], variant="primary")
                result = gr.Textbox(label=local["label_result"])

    # Renderer tab
    with gr.Tab(local["tab_renderer"]):
        with gr.Row():
            input_folder_path = gr.Textbox(label=local["label_input_folder_path"], value="imgs", interactive=True)
        with gr.Row():
            batch_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], value=True, interactive=True)
            batch_render_btn = gr.Button(local["btn_render"], variant="primary")

    # PDF tab
    with gr.Tab("PDF"):
        gr.Markdown(local["info_developing"])
        with gr.Row():
            with gr.Column():
                pdf_file_name = gr.Textbox(value="input.pdf", interactive=False, label=local["label_pdf_file_name"])
                pdf_file = gr.File(label=local["label_pdf_file"], file_count="single", file_types=[".pdf"])
            with gr.Column():
                with gr.Group():
                    pdf_ocr_mode = gr.Dropdown(
                        choices=["split-to-image", "render", "merge"],
                        label=local["label_ocr_mode"], value="split-to-image", interactive=True)
                    dpi = gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150)
                    with gr.Row():
                        pdf_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], interactive=True,
                                                              visible=False)
                        pdf_pdf_merge_confirm = gr.Checkbox(label=local["label_merge_pdf"], interactive=True,
                                                            visible=False)
                pdf_ocr_btn = gr.Button(local["btn_pdf_ocr"], variant="primary")

    # Instructions tab
    with gr.Tab(local["tab_instructions"]):
        # Load instructions from the corresponding language's md file
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()

        gr.Markdown(instructions)

    # Click to perform OCR
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm],
        outputs=result
    )

    # Click to render
    batch_render_btn.click(
        fn=renderer,
        inputs=[input_folder_path, batch_pdf_convert_confirm],
        outputs=None
    )

    # Update image name
    upload_img.change(
        fn=update_img_name,
        inputs=upload_img,
        outputs=img_name
    )

    # Update PDF OCR save as PDF option visibility
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_convert_confirm_visibility,
        inputs=pdf_ocr_mode,
        outputs=pdf_pdf_convert_confirm
    )

    # Update PDF DPI input visibility
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_dpi_visibility,
        inputs=pdf_ocr_mode,
        outputs=dpi
    )

    # Update PDF merge option visibility
    pdf_pdf_convert_confirm.change(
        fn=update_pdf_pdf_merge_confirm_visibility,
        inputs=pdf_pdf_convert_confirm,
        outputs=pdf_pdf_merge_confirm
    )

    # Perform PDF OCR
    pdf_ocr_btn.click(
        fn=pdf_ocr,
        inputs=[pdf_ocr_mode, pdf_file, dpi, pdf_pdf_convert_confirm, pdf_pdf_merge_confirm],
        outputs=None
    )

    # Update PDF name
    pdf_file.change(
        fn=update_pdf_name,
        inputs=pdf_file,
        outputs=pdf_file_name
    )

    # Load model
    load_model_btn.click(
        fn=load_model,
        inputs=None,
        outputs=model_status
    )

    # Unload model
    unload_model_btn.click(
        fn=unload_model,
        inputs=None,
        outputs=model_status
    )

# Launch Gradio interface
demo.launch()
