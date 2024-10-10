import json
import os

# 从config.json文件中加载配置
print("Loading language config...")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']

# 从对应语言的json文件中加载本地化字符串
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# 加载配置文件
print("Loading config......")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 导入库
print(local["info_import_libs"])
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import scripts.Renderer as Render

# 加载模型
if config["load_model_on_start"]:
    print(local["info_load_model"])
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    print(local["info_model_loaded"])
else:
    model = None
    tokenizer = None
    print(local["info_model_load_skipped"])


theme = gr.themes.Base(
    primary_hue="violet",
    secondary_hue="indigo",
    radius_size="sm",
).set(
    background_fill_primary='*neutral_50',
    border_color_accent='*neutral_50',
    color_accent_soft='*neutral_50',
    shadow_drop='none',
    shadow_drop_lg='none',
    shadow_inset='none',
    shadow_spread='none',
    shadow_spread_dark='none',
    layout_gap='*spacing_xl',
    checkbox_background_color='*primary_50',
    checkbox_background_color_focus='*primary_200'
)


# 更新图片名称
def update_img_name(image_uploaded):
    image_name_with_extension = os.path.basename(image_uploaded)
    return gr.Textbox(label=local["label_img_name"], value=image_name_with_extension)


# 进行OCR识别
def ocr(image_uploaded, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, pdf_convert_confirm):

    # 构建OCR框
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    # 默认值
    res = local["error_ocr_mode_none"]

    # 如果result文件夹不存在，则创建
    if not os.path.exists("result"):
        os.makedirs("result")

    try:
        # 根据OCR类型进行OCR识别
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
            success = Render.render(model=model, tokenizer=tokenizer, image_path=image_uploaded,
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


# 渲染器
def renderer(imgs_path, pdf_convert_confirm):
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

    # 逐个发送图片给renderer的render函数
    for image_path in image_files:
        gr.Info(message=local["info_render_start"].format(img_file=image_path))
        success = Render.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                time=config["pdf_render_wait_time"])
        if success:
            gr.Info(message=local["info_render_success"].format(img_file=image_path))
        else:
            gr.Error(message=local["error_render_fail"].format(img_file=image_path))


# gradio gui
with gr.Blocks(theme=theme) as demo:

    # OCR选项卡
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

    # 指南选项卡
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()

        gr.Markdown(instructions)

    # 点击进行OCR识别
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

# 启动gradio界面
demo.launch()
