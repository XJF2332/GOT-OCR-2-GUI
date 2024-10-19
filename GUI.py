import json
import os

# 加载语言设置
print("[Info-GUI] 正在加载语言设置")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# 加载配置文件
print("[Info-GUI] 正在加载配置文件")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 导入库
print("[Info-GUI] " + local["info_import_libs"])
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler

model = None
tokenizer = None


# 加载模型函数
def load_model():
    print("[Info-GUI] " + local["info_load_model"])
    global model, tokenizer
    model = None
    tokenizer = None
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    print("[Info-GUI] " + local["info_model_loaded"])
    return local["info_model_already_loaded"]


# 卸载模型函数
def unload_model():
    global model, tokenizer
    model = None
    tokenizer = None
    return local["info_model_not_loaded"]


# 决定是否加载模型
if config["load_model_on_start"]:
    model, tokenizer = load_model()
else:
    print("[Info-GUI] " + local["info_model_load_skipped"])

# 主题
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


# 更新图片名称
def update_img_name(image_uploaded):
    image_name_with_extension = os.path.basename(image_uploaded)
    return gr.Textbox(label=local["label_img_name"], value=image_name_with_extension)


# 更新 PDF 名称
def update_pdf_name(pdf_uploaded):
    pdf_name_with_extension = os.path.basename(pdf_uploaded)
    return gr.Textbox(label=local["label_pdf_file"], value=pdf_name_with_extension)


# 显示保存 PDF 勾选框（ PDF 标签页）
def show_pdf_pdf_convert_confirm(pdf_ocr_mode):
    if pdf_ocr_mode == "render":
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=False)


# 显示合并 PDF 勾选框（ PDF 标签页）
def show_pdf_pdf_merge_confirm(pdf_convert_confirm):
    if pdf_convert_confirm:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=False)


# 进行 OCR 识别
def ocr(image_uploaded, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, pdf_convert_confirm):
    # 构建 OCR 框
    print("[Info-GUI.ocr] 正在构建框")
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    # 默认值
    res = local["error_ocr_mode_none"]

    # 如果 result 文件夹不存在，则创建
    if not os.path.exists("result"):
        print("[Debug-GUI.ocr] 检测到 result 文件夹不存在，正在创建 result 文件夹")
        os.makedirs("result")

    try:
        # 根据 OCR 类型进行 OCR 识别
        print("[Info-GUI.ocr] 正在执行 OCR")
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
def pdf_ocr(mode, pdf_file, target_dpi, pdf_convert):
    pdf_name = os.path.basename(pdf_file)
    if mode == "split-to-image":
        print("[Info-GUI] 正在分割 PDF 文件")
        success = PDFHandler.split_pdf(pdf_path=pdf_file, img_path="imgs", target_dpi=target_dpi)
        if success:
            print("[Info-GUI] PDF 文件分割成功")
            gr.Info(message=local["info_pdf_split_success"].format(pdf_file=pdf_name))
        else:
            print("[Error-GUI] PDF 文件分割失败")
            raise gr.Error(duration=0, message=local["error_pdf_split_fail"].format(pdf_file=pdf_name))
    elif mode == "render":
        print(f"[Info-GUI] 开始渲染PDF文件：{pdf_name}")
        gr.Info(message=local["info_pdf_render_start"].format(pdf_file=pdf_name))
        success = PDFHandler.pdf_renderer(model=model, tokenizer=tokenizer, pdf_path=pdf_file, target_dpi=target_dpi,
                                          pdf_convert=pdf_convert, wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        if success:
            print(f"[Info-GUI] PDF 文件渲染成功：{pdf_name}")
            gr.Info(message=local["info_pdf_render_success"].format(pdf_file=pdf_name))
        else:
            print(f"[Error-GUI] PDF 文件渲染失败：{pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_render_fail"].format(pdf_file=pdf_name))


# 渲染器
def renderer(imgs_path, pdf_convert_confirm):
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

    # 逐个发送图片给 renderer 的 render 函数
    for image_path in image_files:
        print(f"[Info-GUI] 开始渲染：{image_path}")
        success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                  convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                  time=config["pdf_render_wait_time"])
        if success:
            print(f"[Info-GUI] 成功渲染：{image_path}")
        else:
            raise gr.Error(duration=0, message=local["error_render_fail"].format(img_file=image_path))


# gradio gui
with gr.Blocks(theme=theme) as demo:
    # 模型面板
    with gr.Column(variant="panel"):
        if config["load_model_on_start"]:
            model_status = gr.Markdown(local["info_model_already_loaded"])
        else:
            model_status = gr.Markdown(local["info_model_not_loaded"])
        with gr.Row():
            unload_model_btn = gr.Button(local["btn_unload_model"], variant="secondary")
            load_model_btn = gr.Button(local["btn_load_model"], variant="primary")

    # OCR 选项卡
    with gr.Tab(local["tab_ocr"]):
        with gr.Row():
            with gr.Column():
                # Fine-grained 设置
                gr.Markdown(local["label_fine_grained_settings"])
                with gr.Row():
                    fine_grained_box_x1 = gr.Number(label=local["label_fine_grained_box_x1"], value=0)
                    fine_grained_box_y1 = gr.Number(label=local["label_fine_grained_box_y1"], value=0)
                    fine_grained_box_x2 = gr.Number(label=local["label_fine_grained_box_x2"], value=0)
                    fine_grained_box_y2 = gr.Number(label=local["label_fine_grained_box_y2"], value=0)
                fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"],
                                                 label=local["label_fine_grained_color"], value="red")

            with gr.Column():
                # 渲染设置
                gr.Markdown(local["label_render_settings"])
                img_name = gr.Textbox(label=local["label_img_name"], value="ocr")
                pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"])

        # OCR
        gr.Markdown(local["label_ocr_settings"])
        with gr.Row():
            upload_img = gr.Image(type="filepath", label=local["label_upload_img"])
            with gr.Column():
                ocr_mode = gr.Dropdown(
                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                             "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                    label=local["label_ocr_mode"], value="ocr")
                do_ocr = gr.Button(local["btn_do_ocr"], variant="primary")
                result = gr.Textbox(label=local["label_result"])

    # 渲染器选项卡
    with gr.Tab(local["tab_renderer"]):
        with gr.Row():
            input_folder_path = gr.Textbox(label=local["label_input_folder_path"], value="imgs", interactive=True)
        with gr.Row():
            batch_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], value=True, interactive=True)
            batch_render_btn = gr.Button(local["btn_render"], variant="primary")

    # PDF 选项卡
    with gr.Tab("PDF"):
        gr.Markdown(local["info_developing"])
        with gr.Row():
            with gr.Column():
                pdf_file_name = gr.Textbox(value="input", interactive=False, label=local["label_pdf_file_name"])
                pdf_file = gr.File(label=local["label_pdf_file"], file_count="single", file_types=[".pdf"])
            with gr.Column():
                with gr.Group():
                    pdf_ocr_mode = gr.Dropdown(
                        choices=["split-to-image", "render"],
                        label=local["label_ocr_mode"], value="split-to-image", interactive=True)
                    dpi = gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150)
                    with gr.Row():
                        pdf_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=False)
                        pdf_pdf_merge_confirm = gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=False)
                pdf_ocr_btn = gr.Button(local["btn_pdf_ocr"], variant="primary")

    # 指南选项卡
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()

        gr.Markdown(instructions)

    # 点击进行 OCR 识别
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm],
        outputs=result
    )

    # 点击渲染
    batch_render_btn.click(
        fn=renderer,
        inputs=[input_folder_path, batch_pdf_convert_confirm],
        outputs=None
    )

    # 更新图片名称
    upload_img.change(
        fn=update_img_name,
        inputs=upload_img,
        outputs=img_name
    )

    # PDF OCR 保存 PDF 选项
    pdf_ocr_mode.change(
        fn=show_pdf_pdf_convert_confirm,
        inputs=pdf_ocr_mode,
        outputs=pdf_pdf_convert_confirm
    )

    # PDF OCR 合并 PDF 选项
    pdf_pdf_convert_confirm.change(
        fn=show_pdf_pdf_merge_confirm,
        inputs=pdf_pdf_convert_confirm,
        outputs=pdf_pdf_merge_confirm
    )


    # PDF OCR
    pdf_ocr_btn.click(
        fn=pdf_ocr,
        inputs=[pdf_ocr_mode, pdf_file, dpi, pdf_pdf_convert_confirm],
        outputs=None
    )

    # 更新 PDF 名称
    pdf_file.change(
        fn=update_pdf_name,
        inputs=pdf_file,
        outputs=pdf_file_name
    )

    # 加载模型
    load_model_btn.click(
        fn=load_model,
        inputs=None,
        outputs=model_status
    )

    # 卸载模型
    unload_model_btn.click(
        fn=unload_model,
        inputs=None,
        outputs=model_status
    )

# 启动 gradio 界面
demo.launch()
