import json
import os

# 加载语言设置 (Load language settings)
print("[Info-GUI] 正在加载语言设置 (Language settings are loading)")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# 加载配置文件 (Load configuration file)
print("[Info-GUI] 正在加载配置文件 (The configuration file is loading")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 导入库 (Import libraries)
print("[Info-GUI] " + local["info_import_libs"])
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler
import scripts.PDFMerger as PDFMerger

##########################

model = None
tokenizer = None

##########################

# 加载模型函数 (Loading model function)
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

##########################

# 卸载模型函数 (Unloading model function)
def unload_model():
    global model, tokenizer
    model = None
    tokenizer = None
    return local["info_model_not_loaded"]

##########################

# 决定是否加载模型 (Deciding whether to load the model)
if config["load_model_on_start"]:
    load_model()
else:
    print("[Info-GUI] " + local["info_model_load_skipped"])

# 主题 (Theme)
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
    print("[Warning-GUI] 海洋主题不可用，使用默认主题 (Ocean theme not available, using default theme")
    theme = gr.themes.Default()


##########################

# 更新图片名称 (Updating image name)
def update_img_name(image_uploaded):
    image_name_with_extension = os.path.basename(image_uploaded)
    return gr.Textbox(label=local["label_img_name"], value=image_name_with_extension)

##########################

# 更新 PDF 名称 (Updating PDF name)
def update_pdf_name(pdf_uploaded):
    pdf_name_with_extension = os.path.basename(pdf_uploaded)
    return gr.Textbox(label=local["label_pdf_file"], value=pdf_name_with_extension)

##########################

# 更新保存 PDF 勾选框可见性（PDF 标签页）/ Updating visibility of save as PDF checkbox (PDF tab)
def update_pdf_pdf_convert_confirm_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "render":
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=False, value=False)

##########################

# 更新合并 PDF 勾选框可见性（PDF 标签页） (Updating visibility of merge PDF checkbox (PDF tab))
def update_pdf_pdf_merge_confirm_visibility(pdf_convert_confirm):
    if pdf_convert_confirm:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=True)
    else:
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=False, value=False)

##########################

# 更新目标 DPI 输入框可见性（PDF 标签页） (Updating visibility of target DPI input box (PDF tab))
def update_pdf_pdf_dpi_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "merge":
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=False)
    else:
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=True)

##########################

# 提取prefix (Extracting prefix)
def extract_pdf_pattern(filename):
    """
    从文件名中提取前缀，如果文件名不满足格式 <string>_0.pdf, 则抛出 ValueError 异常
    :param filename: 文件名
    :return: 前缀
    """
    # 在最后一个下划线处分割文件名 (Split the filename at the last underscore)
    parts = filename.rsplit('_', 1)

    # 检查最后一部分是否为 '0.pdf' (Check if the last part is '0.pdf')
    if len(parts) == 2 and parts[1] == '0.pdf':
        return parts[0]
    else:
        raise ValueError("[GUI.extract_pdf_pattern] 输入不满足格式：<string>_0.pdf")

##########################

# 进行 OCR 识别 (Performing OCR recognition)
def ocr(image_uploaded, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, pdf_convert_confirm):
    # 构建 OCR 框 (Building OCR box)
    print("[Info-GUI.ocr] 正在构建框，如未选择 fine-grained 模式可以忽略这个信息")
    box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"

    # 默认值 (Default value)
    res = local["error_ocr_mode_none"]

    # 如果 result 文件夹不存在，则创建 (Creating the 'result' folder if it does not exist)
    if not os.path.exists("result"):
        print("[Debug-GUI.ocr] 检测到 result 文件夹不存在，正在创建 result 文件夹")
        os.makedirs("result")

    try:
        # 根据 OCR 类型进行 OCR 识别 (Performing OCR based on OCR type)
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

##########################

# 执行PDF OCR (Performing PDF OCR)
def pdf_ocr(mode, pdf_file, target_dpi, pdf_convert, pdf_merge):
    pdf_name = os.path.basename(pdf_file)
    # ---------------------------------- #
    # 分割模式
    if mode == "split-to-image":
        print("[Info-GUI] 正在分割 PDF 文件")
        success = PDFHandler.split_pdf(pdf_path=pdf_file, img_path="imgs", target_dpi=target_dpi)
        if success:
            print("[Info-GUI] PDF 文件分割成功")
            gr.Info(message=local["info_pdf_split_success"].format(pdf_file=pdf_name))
        else:
            print("[Error-GUI] PDF 文件分割失败")
            raise gr.Error(duration=0, message=local["error_pdf_split_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 渲染模式
    elif mode == "render":
        print(f"[Info-GUI] 开始渲染PDF文件：{pdf_name}")
        gr.Info(message=local["info_pdf_render_start"].format(pdf_file=pdf_name))
        success = PDFHandler.pdf_renderer(model=model, tokenizer=tokenizer, pdf_path=pdf_file, target_dpi=target_dpi,
                                          pdf_convert=pdf_convert, wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        # 渲染成功判定
        if success:
            print(f"[Info-GUI] PDF 文件渲染成功：{pdf_name}")
            gr.Info(message=local["info_pdf_render_success"].format(pdf_file=pdf_name))
            # 渲染成功则合并
            if pdf_merge: # 决定是否要合并
                print(f"[Info-GUI] 开始合并 PDF 文件：{pdf_name}")
                gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
                success = PDFMerger.merge_pdfs(prefix=pdf_name)
                # 合并成功判定
                if success:
                    print(f"[Info-GUI] PDF 文件合并成功：{pdf_name}")
                    gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
                else:
                    print(f"[Error-GUI] PDF 文件合并失败：{pdf_name}")
                    raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))
            else: # 不合并
                gr.Warning(message=local["info_pdf_merge_skip"].format(pdf_file=pdf_name))
                print(f"[Info-GUI] 跳过合并 PDF 文件：{pdf_name}")
        else: # 渲染失败
            print(f"[Error-GUI] PDF 文件渲染失败：{pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_render_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 合并模式
    elif mode == "merge":
        print(f"[Info-GUI] 开始合并 PDF 文件：{pdf_name}")
        gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
        prefix = extract_pdf_pattern(pdf_name)
        success = PDFMerger.merge_pdfs(prefix=prefix)
        # 合并成功判定
        if success:
            print(f"[Info-GUI] PDF 文件合并成功：{pdf_name}")
            gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
        else:
            print(f"[Error-GUI] PDF 文件合并失败：{pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))

##########################

# 渲染器 (Renderer)
def renderer(imgs_path, pdf_convert_confirm):
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

    # 逐个发送图片给 renderer 的 render 函数 (Sending images one by one to the 'render' function of renderer)
    for image_path in image_files:
        print(f"[Info-GUI] 开始渲染：{image_path}")
        success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                  convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                  time=config["pdf_render_wait_time"])
        if success:
            print(f"[Info-GUI] 成功渲染：{image_path}")
        else:
            raise gr.Error(duration=0, message=local["error_render_fail"].format(img_file=image_path))

##########################

# gradio gui (Gradio GUI)
with gr.Blocks(theme=theme) as demo:
    # 模型面板 (Model panel)
    with gr.Row(variant="panel", equal_height=True):
        # 根据配置文件决定模型初始状态显示
        if config["load_model_on_start"]:
            model_status = gr.Textbox(local["info_model_already_loaded"], show_label=False)
        else:
            model_status = gr.Textbox(local["info_model_not_loaded"], show_label=False)
            unload_model_btn = gr.Button(local["btn_unload_model"], variant="secondary")
            load_model_btn = gr.Button(local["btn_load_model"], variant="primary")

    # OCR 选项卡 (OCR tab)
    with gr.Tab(local["tab_ocr"]):
        # 特殊模式设置
        with gr.Row():
            # Fine-grained 设置
            with gr.Column():
                # Fine-grained 设置 (Fine-grained settings)
                gr.Markdown(local["label_fine_grained_settings"])
                with gr.Row():
                    fine_grained_box_x1 = gr.Number(label=local["label_fine_grained_box_x1"], value=0)
                    fine_grained_box_y1 = gr.Number(label=local["label_fine_grained_box_y1"], value=0)
                    fine_grained_box_x2 = gr.Number(label=local["label_fine_grained_box_x2"], value=0)
                    fine_grained_box_y2 = gr.Number(label=local["label_fine_grained_box_y2"], value=0)
                    fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"],
                                                    label=local["label_fine_grained_color"], value="red")

            with gr.Column():
                # 渲染设置 (Rendering settings)
                gr.Markdown(local["label_render_settings"])
                img_name = gr.Textbox(label=local["label_img_name"], value="ocr")
                pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"])
        # OCR 相关
        gr.Markdown(local["label_ocr_settings"])
        with gr.Row():
            # 上传图片
            upload_img = gr.Image(type="filepath", label=local["label_upload_img"])
            # 其他组件
            with gr.Column():
                # 模式
                ocr_mode = gr.Dropdown(
                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr", "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                    label=local["label_ocr_mode"], value="format")

                do_ocr = gr.Button(local["btn_do_ocr"], variant="primary")
                result = gr.Textbox(label=local["label_result"])

    # 渲染器选项卡 (Renderer tab)
    with gr.Tab(local["tab_renderer"]):
        with gr.Row():
            # 输入
            input_folder_path = gr.Textbox(label=local["label_input_folder_path"], value="imgs", interactive=True)
        with gr.Row():
            # PDF 转换设置
            batch_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], value=True, interactive=True)
            # 按钮
            batch_render_btn = gr.Button(local["btn_render"], variant="primary")

    # PDF 选项卡 (PDF tab)
    with gr.Tab("PDF"):
        with gr.Row():
            # PDF 文件
            with gr.Column():
                pdf_file_name = gr.Textbox(value="input.pdf", interactive=False, label=local["label_pdf_file_name"])
                pdf_file = gr.File(label=local["label_pdf_file"], file_count="single", file_types=[".pdf"])
            # OCR 设置
            with gr.Column():
                # 模式和 DPI
                with gr.Group():
                    pdf_ocr_mode = gr.Dropdown(
                        choices=["split-to-image", "render", "merge"],
                        label=local["label_ocr_mode"], value="split-to-image", interactive=True)
                    dpi = gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150)
                    # PDF 转换设置
                    with gr.Row():
                        # 渲染结果为 PDF
                        pdf_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], interactive=True,
                                                              visible=False)
                        # 合并每一页
                        pdf_pdf_merge_confirm = gr.Checkbox(label=local["label_merge_pdf"], interactive=True,
                                                            visible=False)
                # 按钮
                pdf_ocr_btn = gr.Button(local["btn_pdf_ocr"], variant="primary")

    # 指南选项卡 (Instructions tab)
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南 (Loading instructions from the corresponding language md file)
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()
        gr.Markdown(instructions)

    # 点击进行 OCR 识别 (Click to perform OCR recognition)
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm],
        outputs=result
    )

    # 点击渲染 (Click to render)
    batch_render_btn.click(
        fn=renderer,
        inputs=[input_folder_path, batch_pdf_convert_confirm],
        outputs=None
    )

    # 更新图片名称 (Updating image name)
    upload_img.change(
        fn=update_img_name,
        inputs=upload_img,
        outputs=img_name
    )

    # 更新 PDF OCR 保存 PDF 选项 (Updating save as PDF option for PDF OCR)
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_convert_confirm_visibility,
        inputs=pdf_ocr_mode,
        outputs=pdf_pdf_convert_confirm
    )

    # 更新 PDF OCR DPI 输入框 (Updating target DPI input box for PDF OCR)
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_dpi_visibility,
        inputs=pdf_ocr_mode,
        outputs=dpi
    )

    # 更新 PDF OCR 合并 PDF 选项 (Updating merge PDF option for PDF OCR)
    pdf_pdf_convert_confirm.change(
        fn=update_pdf_pdf_merge_confirm_visibility,
        inputs=pdf_pdf_convert_confirm,
        outputs=pdf_pdf_merge_confirm
    )

    # 执行PDF OCR (Performing PDF OCR)
    pdf_ocr_btn.click(
        fn=pdf_ocr,
        inputs=[pdf_ocr_mode, pdf_file, dpi, pdf_pdf_convert_confirm, pdf_pdf_merge_confirm],
        outputs=None
    )

    # 更新 PDF 名称 (Updating PDF name)
    pdf_file.change(
        fn=update_pdf_name,
        inputs=pdf_file,
        outputs=pdf_file_name
    )

    # 加载模型 (Loading model)
    load_model_btn.click(
        fn=load_model,
        inputs=None,
        outputs=model_status
    )

    # 卸载模型 (Unloading model)
    unload_model_btn.click(
        fn=unload_model,
        inputs=None,
        outputs=model_status
    )
    # ----------------------------------- #

##########################

# 启动 gradio 界面 (Starting the Gradio interface)
demo.launch()
