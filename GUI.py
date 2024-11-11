import os
import logging
from datetime import datetime

# 日志记录器 (Logger)
logger = logging.getLogger('GUI')
logger.setLevel(logging.DEBUG)

# 时间 (Time)
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# 文件处理器 (File handler)
if not os.path.exists("Logs"):
    os.makedirs("Logs")
log_name = os.path.join("Logs", f"log_{current_time}.log")
file_handler = logging.FileHandler(log_name, encoding='utf-8')

# 格式化器 (Formatter)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 控制台处理器 (Console handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug("日志记录器已初始化 (The logger has been initialized)")
print("正在加载 (Loading...)")

##########################

import json

# 加载语言设置 (Load language settings)
logger.info("正在加载语言设置 (The language settings are loading)")
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']
    logger.info(f"语言设置已加载 (The language settings have been loaded): {lang}")
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)
    logger.info(f"语言文件已加载 (The language file has been loaded): {lang}")

##########################

# 加载配置文件 (Load configuration file)
logger.info("正在加载配置文件 (The configuration file is loading)")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

##########################

# 导入库 (Import libraries)
logger.info("正在导入库 (The library is importing)")
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler
import scripts.PDFMerger as PDFMerger
import scripts.TempCleaner as TempCleaner

##########################

model = None
tokenizer = None


##########################

# 加载模型函数 (Loading model function)
def load_model():
    logger.info("正在加载模型 (The model is loading)")
    global model, tokenizer
    model = None
    tokenizer = None
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    logger.info("模型加载完成 (The model is loaded)")
    return local["info_model_already_loaded"]


##########################

# 卸载模型函数 (Unloading model function)
def unload_model():
    global model, tokenizer
    model = None
    tokenizer = None
    logger.info("模型已卸载 (The model has been unloaded)")
    return local["info_model_not_loaded"]


##########################

# 决定是否加载模型 (Deciding whether to load the model)
if config["load_model_on_start"]:
    load_model()
else:
    logger.warning("由于你的设置，模型加载已跳过 (The model loading has been skipped due to your settings)")

##########################

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
    logger.info("主题加载成功 (Successfully loaded theme)")
except AttributeError:
    logger.warning("主题加载失败，回滚到默认主题 (Theme loading failed, roll back to default theme")
    theme = gr.themes.Default()


##########################

# 更新图片名称 (Updating image name)
def update_img_name(image_uploaded):
    image_name_with_extension = os.path.basename(image_uploaded)
    logger.debug(f"[update_img_name] 图片名称已更新 (The image name has been updated): {image_name_with_extension}")
    return gr.Textbox(label=local["label_img_name"], value=image_name_with_extension)


##########################

# 更新 PDF 名称 (Updating PDF name)
def update_pdf_name(pdf_uploaded):
    pdf_name_with_extension = os.path.basename(pdf_uploaded)
    logger.debug(f"[update_pdf_name] PDF 名称已更新 (The PDF name has been updated): {pdf_name_with_extension}")
    return gr.Textbox(label=local["label_pdf_file"], value=pdf_name_with_extension)


##########################

# 更新保存 PDF 勾选框可见性（PDF 标签页）/ Updating visibility of save as PDF checkbox (PDF tab)
def update_pdf_pdf_convert_confirm_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "render":
        logger.debug(
            "[update_pdf_pdf_convert_confirm_visibility] PDF 标签页的保存 PDF 勾选框已启用 (The save PDF checkbox on the PDF tab has been enabled)")
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=True)
    else:
        logger.debug(
            "[update_pdf_pdf_convert_confirm_visibility] PDF 标签页的保存 PDF 勾选框已禁用 (The save PDF checkbox on the PDF tab has been disabled)")
        return gr.Checkbox(label=local["label_save_as_pdf"], interactive=True, visible=False, value=False)


##########################

# 更新合并 PDF 勾选框可见性（PDF 标签页） (Updating visibility of merge PDF checkbox (PDF tab))
def update_pdf_pdf_merge_confirm_visibility(pdf_convert_confirm):
    if pdf_convert_confirm:
        logger.debug(
            "[update_pdf_pdf_merge_confirm_visibility] PDF 标签页的合并 PDF 勾选框已启用 (The merge PDF checkbox on the PDF tab has been enabled)")
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=True)
    else:
        logger.debug(
            "[update_pdf_pdf_merge_confirm_visibility] PDF 标签页的合并 PDF 勾选框已禁用 (The merge PDF checkbox on the PDF tab has been disabled)")
        return gr.Checkbox(label=local["label_merge_pdf"], interactive=True, visible=False, value=False)


##########################

# 更新目标 DPI 输入框可见性（PDF 标签页） (Updating visibility of target DPI input box (PDF tab))
def update_pdf_pdf_dpi_visibility(pdf_ocr_mode):
    if pdf_ocr_mode == "merge":
        logger.debug(
            "[update_pdf_pdf_dpi_visibility] PDF 标签页的目标 DPI 输入框已禁用 (The target DPI input box on the PDF tab has been disabled)")
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=False)
    else:
        logger.debug(
            "[update_pdf_pdf_dpi_visibility] PDF 标签页的目标 DPI 输入框已启用 (The target DPI input box on the PDF tab has been enabled)")
        return gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=True)


##########################

# 提取prefix (Extracting prefix)
def extract_pdf_pattern(filename):
    """
    从文件名中提取前缀，如果文件名不满足格式 <string>_0.pdf, 则抛出 ValueError 异常 (Extracts the prefix from the filename, if the filename does not meet the format <string>_0.pdf, a ValueError exception is raised)
    :param filename: 文件名 (Filename)
    :return: 前缀 (Prefix)
    """
    # 在最后一个下划线处分割文件名 (Split the filename at the last underscore) 
    parts = filename.rsplit('_', 1)
    logger.debug(f"[extract_pdf_pattern] 文件名分割结果 (The result of splitting the filename): {parts}")

    # 检查最后一部分是否为 '0.pdf' (Check if the last part is '0.pdf') 
    if len(parts) == 2 and parts[1] == '0.pdf':
        return parts[0]
    else:
        logger.error(
            "[extract_pdf_pattern] 文件名不满足格式 <string>_0.pdf (Filename does not meet the format <string>_0.pdf)")
        raise ValueError("输入不满足格式：<string>_0.pdf (Input does not meet the format: <string>_0.pdf)")


##########################

# 进行 OCR 识别 (Performing OCR recognition)
def ocr(image_uploaded, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, pdf_convert_confirm, clean_temp):
    # 默认值 (Default value)
    res = local["error_ocr_mode_none"]

    # 如果 result 文件夹不存在，则创建 (Creating the 'result' folder if it does not exist)
    if not os.path.exists("result"):
        os.makedirs("result")
        logger.info("[ocr] result 文件夹不存在，已创建 (Result folder doesn't exists, created)")

    try:
        # 根据 OCR 类型进行 OCR 识别 (Performing OCR based on OCR type)
        logger.info("[ocr] 正在执行 OCR (Performing OCR)")
        if OCR_type == "ocr":
            logger.debug("[ocr] 当前 OCR 模式：ocr (Current ocr mode: ocr)")
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr')
        elif OCR_type == "format":
            logger.debug("[ocr] 当前 OCR 模式：format (Current ocr mode: format)")
            res = model.chat(tokenizer, image_uploaded, ocr_type='format')
        elif OCR_type == "fine-grained-ocr":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-ocr (Current ocr mode: fine-grained-ocr)")
            # 构建 OCR 框 (Building OCR box)
            logger.debug("正在构建 OCR 框 (Building OCR box)")
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr', ocr_box=box)
        elif OCR_type == "fine-grained-format":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-format (Current ocr mode: fine-grained-format)")
            # 构建 OCR 框 (Building OCR box)
            logger.debug("正在构建 OCR 框 (Building OCR box)")
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            res = model.chat(tokenizer, image_uploaded, ocr_type='format', ocr_box=box)
        elif OCR_type == "fine-grained-color-ocr":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-color-ocr (Current ocr mode: fine-grained-color-ocr)")
            res = model.chat(tokenizer, image_uploaded, ocr_type='ocr', ocr_color=fine_grained_color)
        elif OCR_type == "fine-grained-color-format":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-color-format (Current ocr mode: fine-grained-color-format)")
            res = model.chat(tokenizer, image_uploaded, ocr_type='format', ocr_color=fine_grained_color)
        elif OCR_type == "multi-crop-ocr":
            logger.debug("[ocr] 当前 OCR 模式：multi-crop-ocr (Current ocr mode: multi-crop-ocr)")
            res = model.chat_crop(tokenizer, image_uploaded, ocr_type='ocr')
        elif OCR_type == "multi-crop-format":
            logger.debug("[ocr] 当前 OCR 模式：multi-crop-format (Current ocr mode: multi-crop-format)")
            res = model.chat_crop(tokenizer, image_uploaded, ocr_type='format')
        elif OCR_type == "render":
            logger.debug("[ocr] 当前 OCR 模式：render (Current ocr mode: render)")
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_uploaded,
                                      convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                      time=config["pdf_render_wait_time"])
            image_name_with_extension = os.path.basename(image_uploaded)
            logger.debug(f"[ocr] 获取到图像名称 (Got image name): {image_name_with_extension}")
            if success:
                res = local["info_render_success"].format(img_file=image_name_with_extension)
                logger.info("[ocr] 渲染已完成 (Render completed)")
                logger.info("[ocr] 正在清理临时文件 (Cleaning temporary files)")
                if clean_temp and pdf_convert_confirm:
                    TempCleaner.cleaner(["result"],
                                        [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8-local.html"])
                if clean_temp and not pdf_convert_confirm:
                    TempCleaner.cleaner(["result"], [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html"])
                else:
                    logger.info("[ocr] 跳过临时文件清理 (Skip cleaning temporary files)")
            else:
                res = local["error_render_fail"].format(img_file=image_name_with_extension)
        logger.info("[ocr] OCR 已完成 (OCR completed)")
        return res
    except AttributeError:
        logger.error(f"[ocr] OCR 失败，你看起来没有加载模型 (OCR failed, you seem to have not loaded the model)")
        return local["error_no_model"]
    except Exception as e:
        logger.error(f"[ocr] OCR 失败 (OCR failed): {e}")
        return str(e)


##########################

# 执行PDF OCR (Performing PDF OCR)
def pdf_ocr(mode, pdf_file, target_dpi, pdf_convert, pdf_merge, clean_temp):
    logger.info("[pdf_ocr] 开始执行 PDF OCR (Starting PDF OCR)")
    pdf_name = os.path.basename(pdf_file)
    logger.debug(f"[pdf_ocr] 获取到 PDF 名称 (Got PDF name): {pdf_name}")
    # ---------------------------------- #
    # 分割模式 (Split mode)
    if mode == "split-to-image":
        logger.debug("[pdf_ocr] 当前模式：split-to-image (Current mode: split-to-image)")
        logger.info("[pdf_ocr] 开始分割 PDF 文件 (Starting to split PDF file)")
        success = PDFHandler.split_pdf(pdf_path=pdf_file, img_path="imgs", target_dpi=target_dpi)
        if success:
            logger.info("[pdf_ocr] PDF 文件分割成功 (PDF file split successfully)")
            gr.Info(message=local["info_pdf_split_success"].format(pdf_file=pdf_name))
        else:
            logger.error("[pdf_ocr] PDF 文件分割失败 (PDF file split failed)")
            raise gr.Error(duration=0, message=local["error_pdf_split_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 渲染模式 (Rendering mode)
    elif mode == "render":
        logger.debug("[pdf_ocr] 当前模式：render (Current mode: render)")
        logger.info(f"[pdf_ocr] 开始渲染 PDF 文件 (Starting to render PDF file)：{pdf_name}")
        gr.Info(message=local["info_pdf_render_start"].format(pdf_file=pdf_name))
        success = PDFHandler.pdf_renderer(model=model, tokenizer=tokenizer, pdf_path=pdf_file, target_dpi=target_dpi,
                                          pdf_convert=pdf_convert, wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        # 渲染成功判定 (Rendering success determination)
        if success:
            logger.info(f"[pdf_ocr] PDF 文件渲染成功 (PDF file rendered successfully)：{pdf_name}")
            gr.Info(message=local["info_pdf_render_success"].format(pdf_file=pdf_name))
            # 渲染成功则合并 (Render successfully and then merge)
            if pdf_merge:  # 决定是否要合并 (Deciding whether to merge or not)
                logger.info(f"[pdf_ocr] 开始合并 PDF 文件 (Starting to merge PDF file)：{pdf_name}")
                gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
                success = PDFMerger.merge_pdfs(prefix=pdf_name)
                # 合并成功判定 (Merging success determination)
                if success:
                    logger.info(f"[pdf_ocr] PDF 文件合并成功 (PDF file merged successfully)：{pdf_name}")
                    gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
                    # 合并成功，清理临时文件 (Merged successfully, cleaning up temporary files)
                    if clean_temp:
                        logger.info("[pdf_ocr] 开始清理临时文件 (Starting to clean up temporary files)")
                        TempCleaner.cleaner(["result"], [f"{extract_pdf_pattern(pdf_name)}_\d+.pdf"])
                        logger.debug(f"获取到临时文件特征 (Got temp file pattern)：{extract_pdf_pattern(pdf_name)}_\d+.pdf")
                else:
                    logger.error(f"[pdf_ocr] PDF 文件合并失败 (PDF file merge failed)：{pdf_name}")
                    raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))
            else:  # 不合并 (Not merging)
                logger.info(f"[pdf_ocr] 跳过合并 PDF 文件 (Skipping merging PDF file)：{pdf_name}")
                gr.Info(message=local["info_pdf_merge_skip"].format(pdf_file=pdf_name))
        else:  # 渲染失败 (Failed to render)
            logger.error(f"[pdf_ocr] PDF 文件渲染失败 (PDF file render failed)：{pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_render_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 合并模式 (Merging mode)
    elif mode == "merge":
        logger.debug("[pdf_ocr] 当前模式：merge (Current mode: merge)")
        gr.Info(message=local["info_pdf_merge_start"].format(pdf_file=pdf_name))
        prefix = extract_pdf_pattern(pdf_name)
        success = PDFMerger.merge_pdfs(prefix=prefix)
        # 合并成功判定 (Merging success determination)
        if success:
            logger.info(f"[pdf_ocr] PDF 文件合并成功 (PDF file merged successfully)：{pdf_name}")
            gr.Info(message=local["info_pdf_merge_success"].format(pdf_file=pdf_name))
            if clean_temp:
                # 合并成功，清理临时文件 (Merged successfully, cleaning up temporary files)
                logger.info("[pdf_ocr] 开始清理临时文件 (Starting to clean up temporary files)")
                TempCleaner.cleaner(["result"], [f"{extract_pdf_pattern(pdf_name)}_\d+.pdf"])
                logger.debug(f"获取到临时文件特征 (Got temp file pattern)：{extract_pdf_pattern(pdf_name)}_\d+.pdf")
            else:
                logger.info(f"[Info-GUI] 跳过清理临时文件 (Skipping cleaning up temporary files)")
                print(f"[Info-GUI] 跳过清理临时文件" + " (Skipping cleaning up temporary files)")
        else:
            logger.error(f"[pdf_ocr] PDF 文件合并失败 (PDF file merge failed)：{pdf_name}")
            raise gr.Error(duration=0, message=local["error_pdf_merge_fail"].format(pdf_file=pdf_name))


##########################

# 渲染器 (Renderer)
def renderer(imgs_path, pdf_convert_confirm, clean_temp):
    # 获取图片文件列表 (Get a list of image files)
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))
    logger.debug(f"获取到图片文件列表 (Got image file list)：{image_files}")

    # 逐个发送图片给 renderer 的 render 函数 (Sending images one by one to the 'render' function of renderer)
    for image_path in image_files:
        logger.info(f"[Info-GUI.renderer] 开始渲染：{image_path}")
        success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                  convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                  time=config["pdf_render_wait_time"])
        if success:
            logger.info(f"[Info-GUI.renderer] 渲染成功：{image_path}")
            if clean_temp and pdf_convert_confirm:
                logger.info("[Info-GUI.renderer] 开始清理临时文件 (Starting to clean up temporary files)")
                TempCleaner.cleaner(["result"],
                                    [f"{os.path.splitext(os.path.basename(image_path))[0]}-gb2312.html",
                                     f"{os.path.splitext(os.path.basename(image_path))[0]}-utf8.html",
                                     f"{os.path.splitext(os.path.basename(image_path))[0]}-utf8-local.html"])
            if clean_temp and not pdf_convert_confirm:
                logger.info("[Info-GUI.renderer] 开始清理临时文件 (Starting to clean up temporary files)")
                TempCleaner.cleaner(["result"], [f"{os.path.splitext(os.path.basename(image_path))[0]}-gb2312.html"])
            else:
                logger.info(f"[Info-GUI.renderer] 跳过清理临时文件 (Skipping cleaning up temporary files)")
        else:
            logger.error(f"[Info-GUI.renderer] 渲染失败：{image_path}")
            raise gr.Error(duration=0, message=local["error_render_fail"].format(img_file=image_path))


##########################

# Gradio GUI
with gr.Blocks(theme=theme) as demo:
    # ---------------------------------- #
    # 模型面板 (Model panel)
    with gr.Row(variant="panel", equal_height=True):
        # 根据配置文件决定模型初始状态显示 (Decide model initial state display based on configuration file)
        if config["load_model_on_start"]:
            model_status = gr.Textbox(local["info_model_already_loaded"], show_label=False)
        else:
            model_status = gr.Textbox(local["info_model_not_loaded"], show_label=False)
            # 模型按钮 (Model buttons)
        unload_model_btn = gr.Button(local["btn_unload_model"], variant="secondary")
        load_model_btn = gr.Button(local["btn_load_model"], variant="primary")
    # ---------------------------------- #
    # OCR 选项卡 (OCR tab)
    with gr.Tab(local["tab_ocr"]):
        # 特殊模式设置 (Special mode settings)
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
            # 渲染设置 (Rendering settings)
            with gr.Column():
                gr.Markdown(local["label_render_settings"])
                img_name = gr.Textbox(label=local["label_img_name"], value="ocr")
                with gr.Row(equal_height=True):
                    pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"])
                    clean_temp_render = gr.Checkbox(label=local["label_clean_temp"])
        # OCR 相关 (OCR Settings)
        gr.Markdown(local["label_ocr_settings"])
        with gr.Row():
            # 上传图片 (Upload Image)
            upload_img = gr.Image(type="filepath", label=local["label_upload_img"])
            # 其他组件 (Other Components)
            with gr.Column():
                # 模式 (Mode)
                ocr_mode = gr.Dropdown(
                    choices=[(local["mode_ocr"], "ocr"), (local["mode_format"], "format"),
                             (local["mode_fine-grained-ocr"], "fine-grained-ocr"),
                             (local["mode_fine-grained-format"], "fine-grained-format"),
                             (local["mode_fine-grained-color-ocr"], "fine-grained-color-ocr"),
                             (local["mode_fine-grained-color-format"], "fine-grained-color-format"),
                             (local["mode_multi-crop-ocr"], "multi-crop-ocr"),
                             (local["mode_multi-crop-format"], "multi-crop-format"), (local["mode_render"], "render")],
                    label=local["label_ocr_mode"], value="ocr")
                # OCR (Buttons and Results)
                do_ocr = gr.Button(local["btn_do_ocr"], variant="primary")
                result = gr.Textbox(label=local["label_result"])
    # ---------------------------------- #
    # 渲染器选项卡 (Renderer tab)
    with gr.Tab(local["tab_renderer"]):
        # 输入 (Input folder path)
        input_folder_path = gr.Textbox(label=local["label_input_folder_path"], value="imgs", interactive=True)
        with gr.Row(equal_height=True):
            # PDF 转换设置 (Save as PDF settings)
            batch_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], value=True, interactive=True)
            # 清理临时文件 (Clean temporary files)
            clean_temp_renderer = gr.Checkbox(label=local["label_clean_temp"], value=True, interactive=True)
            # 按钮 (Render button)
            batch_render_btn = gr.Button(local["btn_render"], variant="primary", scale=2)
    # PDF 选项卡 (PDF tab)
    with gr.Tab("PDF"):
        with gr.Row():
            # PDF 文件 (PDF file path)
            with gr.Column():
                pdf_file_name = gr.Textbox(value="input.pdf", interactive=False, label=local["label_pdf_file_name"])
                pdf_file = gr.File(label=local["label_pdf_file"], file_count="single", file_types=[".pdf"])
            # OCR 设置 (set up OCR)
            with gr.Column():
                # 模式和 DPI (mode and DPI)
                with gr.Group():
                    pdf_ocr_mode = gr.Dropdown(
                        choices=["split-to-image", "render", "merge"],
                        label=local["label_ocr_mode"], value="split-to-image", interactive=True)
                    dpi = gr.Number(label=local["label_target_dpi"], minimum=72, maximum=300, step=1, value=150)
                    # PDF 转换设置 (PDF conversion settings)
                    with gr.Row():
                        # 渲染结果为 PDF (Render the result as PDF)
                        pdf_pdf_convert_confirm = gr.Checkbox(label=local["label_save_as_pdf"], interactive=True,
                                                              visible=False)
                        # 合并每一页 (Merge per page)
                        pdf_pdf_merge_confirm = gr.Checkbox(label=local["label_merge_pdf"], interactive=True,
                                                            visible=False)
                # 按钮 (Buttons)
                with gr.Row(equal_height=True):
                    pdf_ocr_btn = gr.Button(local["btn_pdf_ocr"], variant="primary", scale=2)
                    clean_temp = gr.Checkbox(label=local["label_clean_temp"], value=True, interactive=True)
    # 指南选项卡 (Instructions tab)
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南 (Loading instructions from the corresponding language md file)
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()
        gr.Markdown(instructions)
    # ---------------------------------- #
    # 点击进行 OCR 识别 (Click to perform OCR recognition)
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm, clean_temp_render],
        outputs=result
    )
    # ---------------------------------- #
    # 点击渲染 (Click to render)
    batch_render_btn.click(
        fn=renderer,
        inputs=[input_folder_path, batch_pdf_convert_confirm, clean_temp_renderer],
        outputs=None
    )
    # ---------------------------------- #
    # 更新图片名称 (Updating image name)
    upload_img.change(
        fn=update_img_name,
        inputs=upload_img,
        outputs=img_name
    )
    # ---------------------------------- #
    # 更新 PDF OCR 保存 PDF 选项 (Updating save as PDF option for PDF OCR)
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_convert_confirm_visibility,
        inputs=pdf_ocr_mode,
        outputs=pdf_pdf_convert_confirm
    )
    # ----------------------------------- #
    # 更新 PDF OCR DPI 输入框 (Updating target DPI input box for PDF OCR)
    pdf_ocr_mode.change(
        fn=update_pdf_pdf_dpi_visibility,
        inputs=pdf_ocr_mode,
        outputs=dpi
    )
    # ----------------------------------- #
    # 更新 PDF OCR 合并 PDF 选项 (Updating merge PDF option for PDF OCR)
    pdf_pdf_convert_confirm.change(
        fn=update_pdf_pdf_merge_confirm_visibility,
        inputs=pdf_pdf_convert_confirm,
        outputs=pdf_pdf_merge_confirm
    )
    # ----------------------------------- #
    # 执行PDF OCR (Performing PDF OCR)
    pdf_ocr_btn.click(
        fn=pdf_ocr,
        inputs=[pdf_ocr_mode, pdf_file, dpi, pdf_pdf_convert_confirm, pdf_pdf_merge_confirm, clean_temp],
        outputs=None
    )
    # ----------------------------------- #
    # 更新 PDF 名称 (Updating PDF name)
    pdf_file.change(
        fn=update_pdf_name,
        inputs=pdf_file,
        outputs=pdf_file_name
    )
    # ----------------------------------- #
    # 加载模型 (Loading model)
    load_model_btn.click(
        fn=load_model,
        inputs=None,
        outputs=model_status
    )
    # ----------------------------------- #
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
