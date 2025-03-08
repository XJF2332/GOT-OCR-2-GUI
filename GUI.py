print("正在加载 / Loading...")

import logging
from datetime import datetime
import scripts.Renderer as Renderer
import scripts.PDFHandler as PDFHandler
import scripts.PDFMerger as PDFMerger
import scripts.TempCleaner as TempCleaner
import scripts.got_cpp.got_ocr as got_cpp
from onnxruntime import get_available_providers
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import os
import glob
import json
from time import sleep

##########################

# 加载配置文件 / Load configuration file
config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 / Configuration file not found")
    print("程序将在3秒后退出 / Exit in 3 seconds")
    sleep(3)
    exit(1)

##########################

# 日志记录器 / Logger
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logger = logging.getLogger(__name__)

if not os.path.exists("Logs"):
    os.mkdir("Logs")

logging.basicConfig(
    filename=os.path.join("Logs", f"{current_time}.log"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
)

try:
    lvl = config['logger_level']
    if lvl.lower() == 'debug':
        logger.setLevel(logging.DEBUG)
    elif lvl.lower() == 'info':
        logger.setLevel(logging.INFO)
    elif lvl.lower() == 'warning':
        logger.setLevel(logging.WARNING)
    elif lvl.lower() == 'error':
        logger.setLevel(logging.ERROR)
    elif lvl.lower() == 'critical':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.warning("无效的日志级别，回滚到 INFO 级别 / Invalid log level, rolling back to INFO level")
        logger.warning("请检查配置文件 / Go check the configuration file")
        logger.setLevel(logging.INFO)
except KeyError:
    logger.warning("未找到日志级别，回滚到 INFO 级别 / Log level configuration not found, rolling back to INFO level")
    logger.warning("请检查配置文件 / Go check the configuration file")
    logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

logger.info("日志记录器已初始化 / Logger initialized")

##########################


# 加载语言设置 / Load language settings
try:
    with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
        lang_config = json.load(file)
        lang = lang_config['language']
except FileNotFoundError:
    logger.warning(
        "语言配置文件未找到，回滚到简体中文 / Language configuration file not found, rolling back to Simplified Chinese")
    lang = 'zh_CN'

try:
    with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
        local = json.load(file)
        logger.info(local['log']['info']['lang_file_loaded'].format(lang=lang))
except FileNotFoundError:
    logger.critical(f"语言文件未找到 / Language file not found): {lang}")
    print("程序将在3秒后退出 / Exit in 3 seconds")
    sleep(3)
    exit(1)

##########################

model = None
tokenizer = None


##########################

# 加载模型函数 / Loading model function
def load_model():
    logger.info(local['log']['info']['model_loading'])
    global model, tokenizer
    model = None
    tokenizer = None
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    logger.info(local['log']['info']['model_loaded'])
    return local["info"]["model_already_loaded"]


##########################

# 卸载模型函数 / Unloading model function
def unload_model():
    global model, tokenizer
    model = None
    tokenizer = None
    logger.info(local['log']['info']['model_unloaded'])
    return local["info"]["model_not_loaded"]


##########################

# 决定是否加载模型 / Deciding whether to load the model
if config["load_model_on_start"]:
    load_model()
else:
    logger.warning(local['log']['warning']['model_loading_skipped'])

##########################

# 主题 / Theme
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
    logger.info(local['log']['info']['theme_loaded'])
except AttributeError:
    logger.warning(local['log']['warning']['theme_loading_failed'])
    theme = gr.themes.Default()


##########################

# 更新图片名称 / Update image name
def update_img_name(image_uploaded):
    try:
        image_name_ext = os.path.basename(image_uploaded)
        logger.debug(local['log']['info']['img_name_updated'].format(name=image_name_ext))
    except:
        image_name_ext = local["info"]["image_cleared"]
        logger.debug(local['log']['info']['image_name_cleared'])
    return gr.Markdown(value=image_name_ext)


##########################

# 更新 PDF 名称 / Update PDF name
def update_pdf_name(pdf_uploaded):
    pdf_name_with_extension = os.path.basename(pdf_uploaded)
    logger.debug(local['log']['info']['pdf_name_updated'].format(name=pdf_name_with_extension))
    return gr.Textbox(label=local["label"]["pdf_file"], value=pdf_name_with_extension)


##########################

# 更新保存 PDF 勾选框可见性（PDF 标签页）/ Update visibility of save as PDF checkbox (PDF tab)
def update_pdf_conv_conf_visibility(pdf_ocr_mode_update):
    if pdf_ocr_mode_update == "render":
        logger.debug(local['log']['debug']['save_pdf_checkbox_enabled'])
        return gr.Checkbox(label=local["label"]["save_as_pdf"], interactive=True, visible=True)
    else:
        logger.debug(local['log']['debug']['save_pdf_checkbox_disabled'])
        return gr.Checkbox(label=local["label"]["save_as_pdf"], interactive=True, visible=False, value=False)


##########################

# 更新合并 PDF 勾选框可见性（PDF 标签页）/ Updating visibility of merge PDF checkbox (PDF tab)
def update_pdf_merge_conf_visibility(pdf_convert_confirm_update):
    if pdf_convert_confirm_update:
        logger.debug(local['log']['debug']['merge_pdf_checkbox_enabled'])
        return gr.Checkbox(label=local["label"]["merge_pdf"], interactive=True, visible=True)
    else:
        logger.debug(local['log']['debug']['merge_pdf_checkbox_disabled'])
        return gr.Checkbox(label=local["label"]["merge_pdf"], interactive=True, visible=False, value=False)


##########################

# 更新目标 DPI 输入框可见性（PDF 标签页）/ Update visibility of target DPI input box (PDF tab)
def update_pdf_dpi_visibility(pdf_ocr_mode_update):
    if pdf_ocr_mode_update == "merge":
        logger.debug(local['log']['debug']['dpi_input_box_disabled'])
        return gr.Number(label=local["label"]["target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=False)
    else:
        logger.debug(local['log']['debug']['dpi_input_box_enabled'])
        return gr.Number(label=local["label"]["target_dpi"], minimum=72, maximum=300, step=1, value=150, visible=True)


##########################

# 提取prefix / Extracting prefix
def extract_pdf_pattern(filename):
    """
    从文件名中提取前缀，如果文件名不满足格式 <string>_0.pdf, 则抛出 ValueError 异常
    (Extracts the prefix from the filename, if the filename does not meet the format <string>_0.pdf, a ValueError exception is raised)
    :param filename: 文件名 (Filename)
    :return: 前缀 (Prefix)
    """
    # 在最后一个下划线处分割文件名 (Split the filename at the last underscore) 
    parts = filename.rsplit('_')
    logger.debug(local['log']['debug']['filename_split_res'].format(res=parts))

    # 检查最后一部分是否为 '0.pdf' (Check if the last part is '0.pdf') 
    if len(parts) == 2 and parts[1] == '0.pdf':
        return parts[0]
    else:
        logger.error(local['log']['error']['pdf_filename_format_error'])
        raise ValueError(local["error"]["pdf_filename_format_error"])


##########################

class OCRHandler:
    def __init__(self):
        # self.safetensors_model = None
        # self.safetensors_tokenizer = None
        pass

    @staticmethod
    def render_old(image_path, pdf_conv_conf, temp_clean):
        """
        渲染模式（旧版）
        Render mode (old)

        Args:
            image_path: 输入图像路径 / Input image path
            pdf_conv_conf: 是否保存为 PDF / Whether to save as PDF
            temp_clean: 是否清理临时文件 / Whether to clean temp files

        Returns:
            运行状态
            Status
        """
        try:
            gr.Info(local["info"]["render_start"].format(img_file = os.path.basename(image_path)))
            success = Renderer.render(model=model, tokenizer=tokenizer, img_path=image_path, conv_to_pdf=pdf_conv_conf,
                                    wait=config["pdf_render_wait"], time=config["pdf_render_wait_time"])
            image_name_ext = os.path.basename(image_path)
            logger.debug(local['log']['debug']['got_img_name'].format(img_name=image_name_ext))

            if success == 0:
                res = local["info"]["render_success"].format(img_file=image_name_ext)
                logger.info(local['log']['info']['render_completed'])
                if temp_clean and pdf_conv_conf:
                    logger.info(f"[ocr] {local['log']['info']['temp_cleaning']}")
                    TempCleaner.cleaner(["result"],
                                        [f"{os.path.splitext(image_name_ext)[0]}-gb2312.html",
                                        f"{os.path.splitext(image_name_ext)[0]}-utf8.html",
                                        f"{os.path.splitext(image_name_ext)[0]}-utf8-local.html"])
                if temp_clean and not pdf_conv_conf:
                    logger.info(f"[ocr] {local['log']['info']['temp_cleaning']}")
                    TempCleaner.cleaner(["result"], [f"{os.path.splitext(image_name_ext)[0]}-gb2312.html"])
                else:
                    logger.info(f"[ocr] {local['log']['info']['temp_cleaning_skipped']}")
            else:
                res = local["error"]["render_fail"].format(img_file=image_name_ext) + f": {str(success)}"

            return res
        except Exception as e:
            logger.error(local['log']['error']['render_failed'].format(image=image_name_ext))
            return local["error"]["render_failed"].format(error=e)
    
    @staticmethod
    def ocr_fg(image_path, fg_box_x1, fg_box_y1, fg_box_x2, fg_box_y2, mode, fg_color):
        """
        指定区域的 OCR 识别
        OCR recognition for specified area

        Args:
            image_path: 输入图像路径 / Input image path
            fg_box_x1: 指定区域 x 坐标 1 / The first x coordinate of the specified area
            fg_box_y1: 指定区域 y 坐标 1 / The first y coordinate of the specified area
            fg_box_x2: 指定区域 x 坐标 2 / The second x coordinate of the specified area
            fg_box_y2: 指定区域 y 坐标 2 / The second y coordinate of the specified area
            mode: OCR 模式 / OCR mode
            fg_color: 指定颜色 / Specified color
        """
        logger.info(local['log']['info']['fg_ocr_start'])
        logger.debug(local['log']['debug']['current_ocr_mode'].format(ocr_mode=mode))
        if mode == "fine-grained-ocr":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            logger.debug(local['log']['debug']['current_ocr_box'].format(ocr_box=box))
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_box=box)
        elif mode == "fine-grained-format":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            logger.debug(local['log']['debug']['current_ocr_box'].format(ocr_box=box))
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_box=box)
        elif mode == "fine-grained-color-ocr":
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_color=fg_color)
        elif mode == "fine-grained-color-format":
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_color=fg_color)

        return res
    
    @staticmethod
    def ocr_crop(image_path, mode):
        logger.info(local['log']['info']['crop_ocr_start'])
        logger.debug(local['log']['debug']['current_ocr_mode'].format(ocr_mode=mode))
        if mode == "multi-crop-ocr":
            res = model.chat_crop(tokenizer, image_path, ocr_type='ocr')
        elif mode == "multi-crop-format":
            res = model.chat_crop(tokenizer, image_path, ocr_type='format')

        return res
    
    @staticmethod
    def ocr():
        pass

##########################

# 进行 OCR 识别 / Performing OCR recognition
def ocr(image_path, fg_box_x1, fg_box_y1, fg_box_x2, fg_box_y2, mode, fg_color, pdf_conv_conf, temp_clean):
    # 默认值 / Default value
    res = local["error"]["ocr_mode_none"]

    gr.Info(message=local["info"]["ocr_started"])

    # 如果 result 文件夹不存在，则创建 / Creating the 'result' folder if it does not exist
    if not os.path.exists("result"):
        os.makedirs("result")
        logger.info(local['log']['info']['res_folder_created'])

    try:
        # 根据 OCR 类型进行 OCR 识别 / Performing OCR based on OCR type
        logger.info(local['log']['info']['ocr_started'])
        logger.debug(local['log']['debug']['current_ocr_mode'].format(ocr_mode=mode))
        if mode == "ocr":
            res = model.chat(tokenizer, image_path, ocr_type='ocr')
        elif mode == "format":
            res = model.chat(tokenizer, image_path, ocr_type='format')
        elif mode == "fine-grained-ocr":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            logger.debug(local['log']['debug']['current_ocr_box'].format(ocr_box=box))
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_box=box)
        elif mode == "fine-grained-format":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            logger.debug(local['log']['debug']['current_ocr_box'].format(ocr_box=box))
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_box=box)
        elif mode == "fine-grained-color-ocr":
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_color=fg_color)
        elif mode == "fine-grained-color-format":
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_color=fg_color)
        elif mode == "multi-crop-ocr":
            res = model.chat_crop(tokenizer, image_path, ocr_type='ocr')
        elif mode == "multi-crop-format":
            res = model.chat_crop(tokenizer, image_path, ocr_type='format')
        elif mode == "render":
            res = OCRHandler.render_old(image_path=image_path, pdf_conv_conf=pdf_conv_conf, temp_clean=temp_clean)
        logger.info(local['log']['info']['ocr_completed'])
        return res
    except AttributeError as e:
        print(e)
        logger.error(local['log']['error']['no_model_or_img'])
        return local["error"]["no_model_or_img"]
    except Exception as e:
        logger.error(local['log']['error']['ocr_failed'].format(error=e))
        return local["error"]["ocr_failed"].format(error=e)


##########################

# 执行 PDF OCR / Performing PDF OCR
def pdf_ocr(mode, pdf, target_dpi, pdf_convert, pdf_merge, temp_clean):
    logger.info(local['log']['info']['pdf_ocr_start'])
    if not pdf:
        logger.error(local['log']['error']['no_pdf_uploaded'])
        raise gr.Error(duration=0, message=local["error"]["no_pdf"])
    pdf_name = os.path.basename(pdf)
    logger.debug(local["log"]["debug"]["got_pdf_name"].format(name=pdf_name))
    # ---------------------------------- #
    # 分割模式 / Split mode
    if mode == "split-to-image":
        logger.debug(local['log']['debug']['pdf_mode_split'])
        logger.info(local['log']['info']['pdf_splitting_started'])
        success = PDFHandler.split_pdf(pdf_path=pdf, img_path="imgs", target_dpi=target_dpi)
        if success:
            logger.info(local['log']['info']['pdf_split_success'])
            gr.Info(message=local["info"]["pdf_split_success"].format(pdf_file=pdf_name))
        else:
            logger.error(local["log"]["error"]["pdf_split_fail"])
            raise gr.Error(duration=0, message=local["error"]["pdf_split_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 渲染模式 / Render mode
    elif mode == "render":
        logger.debug(local['log']['debug']['pdf_mode_render'])
        logger.info(local["log"]["info"]["pdf_render_started"].format(pdf=pdf_name))
        gr.Info(message=local["info"]["pdf_render_start"].format(pdf_file=pdf_name))
        success = PDFHandler.pdf_renderer(model=model,
                                          tokenizer=tokenizer,
                                          pdf_path=pdf,
                                          dpi=target_dpi,
                                          pdf_conv=pdf_convert,
                                          wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        # 渲染成功判定 / Rendering success determination
        if success:
            logger.info(local["log"]["info"]["pdf_render_success"].format(pdf=pdf_name))
            gr.Info(message=local["info"]["pdf_render_success"].format(pdf_file=pdf_name))
            # 自动合并 / Auto merge
            pattern_pdf = f"{os.path.splitext(pdf_name)[0]}_0.pdf"
            pattern_html = f"{os.path.splitext(pdf_name)[0]}_\d+-.*\.html"
            pattern_pdf_temp = f"{os.path.splitext(pdf_name)[0]}_\d+-.*\.html"
            if pdf_merge:  # 决定是否要合并 / Deciding whether to merge or not
                logger.info(local["log"]["info"]["pdf_merge_started"].format(pdf=pdf_name))
                gr.Info(message=local["info"]["pdf_merge_start"].format(pdf_file=pdf_name))
                success = PDFMerger.merge_pdfs(prefix=extract_pdf_pattern(pattern_pdf))
                # 合并成功判定 / Merging success determination
                if success:
                    logger.info(local["log"]["info"]["pdf_merge_success"].format(pdf=pdf_name))
                    gr.Info(message=local["info"]["pdf_merge_success"].format(pdf_file=pdf_name))
                    # 合并成功，清理临时文件 / Merged successfully, cleaning up temporary files
                    if temp_clean:
                        logger.info(local['log']['info']['pdf_temp_cleaning'])
                        logger.debug(local['log']['debug']['got_temp_file_pattern'].format(
                            pattern=[pattern_pdf_temp, pattern_html]))
                        TempCleaner.cleaner(["result"], [pattern_pdf_temp, pattern_html])
                else:
                    logger.error(local['log']['error']['pdf_merge_failed'].format(name=pdf_name))
                    raise gr.Error(duration=0, message=local["error"]["pdf_merge_fail"].format(pdf_file=pdf_name))
            else:  # 不合并 / Not merging
                logger.info(local['log']['info']['merge_skipped'].format(name=pdf_name))
                gr.Info(message=local["info_pdf_merge_skip"].format(pdf_file=pdf_name))
        else:  # 渲染失败 / Failed to render
            logger.error(local['log']['error']['pdf_render_failed'].format(name=pdf_name))
            raise gr.Error(duration=0, message=local["error"]["pdf_render_fail"].format(pdf_file=pdf_name))
    # ---------------------------------- #
    # 合并模式 / Merging mode
    elif mode == "merge":
        logger.debug(local['log']['debug']['pdf_mode_merge'])
        gr.Info(message=local["info"]["pdf_merge_start"].format(pdf_file=pdf_name))
        prefix = extract_pdf_pattern(pdf_name)
        success = PDFMerger.merge_pdfs(prefix=prefix)
        # 合并成功判定 / Merging success determination
        if success:
            logger.info(local["log"]["info"]["pdf_merge_success"].format(pdf=pdf_name))
            gr.Info(message=local["info"]["pdf_merge_success"].format(pdf_file=pdf_name))
            if temp_clean:
                # 合并成功，清理临时文件 / Merged successfully, cleaning up temporary files
                logger.info(local['log']['info']['pdf_temp_cleaning'])
                logger.debug(local['log']['debug']['got_temp_file_pattern'].format(
                    pattern=f'{extract_pdf_pattern(pdf_name)}_\d+.pdf'))
                TempCleaner.cleaner(["result"], [f"{extract_pdf_pattern(pdf_name)}_\d+.pdf"])
            else:
                logger.info(local['log']['info']['pdf_temp_cleaning_skipped'])
        else:
            # logger.error(f"[pdf_ocr] PDF 文件合并失败 (PDF file merge failed)：{pdf_name}")
            logger.error(local['log']['error']['pdf_merge_failed'].format(name=pdf_name))
            raise gr.Error(duration=0, message=local["error"]["pdf_merge_fail"].format(pdf_file=pdf_name))


##########################

# 渲染器 / Renderer
def renderer(imgs_path, pdf_convert_confirm, clean_temp):
    # 获取图片文件列表 / Get a list of image files
    image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))
    logger.debug(local['log']['debug']['got_image_list'].format(list=image_files))
    # 逐个发送图片给 renderer 的 render 函数 / Sending images one by one to the 'render' function of renderer
    for image_path in image_files:
        logger.info(local['log']['info']['renderer_started'].format(image=image_path))
        success = Renderer.render(model=model, tokenizer=tokenizer, img_path=image_path,
                                  conv_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                  time=config["pdf_render_wait_time"])
        if success == 1:
            logger.info(local['log']['info']['renderer_success'].format(image=image_path))
            if clean_temp and pdf_convert_confirm:
                logger.info(local['log']['info']['renderer_temp_cleaning'])
                TempCleaner.cleaner(["result"],
                                    [f"{os.path.splitext(os.path.basename(image_path))[0]}-gb2312.html",
                                     f"{os.path.splitext(os.path.basename(image_path))[0]}-utf8.html",
                                     f"{os.path.splitext(os.path.basename(image_path))[0]}-utf8-local.html"])
            if clean_temp and not pdf_convert_confirm:
                logger.info(local['log']['info']['renderer_temp_cleaning'])
                TempCleaner.cleaner(["result"], [f"{os.path.splitext(os.path.basename(image_path))[0]}-gb2312.html"])
            else:
                logger.info(local['log']['info']['renderer_temp_cleaning_skipped'])
        elif success == 2:
            logger.error(local['log']['error']['renderer_no_model_or_img'])
            raise gr.Error(duration=0, message=local["error"]["no_model_or_img"])
        elif success == 3:
            logger.error(local['log']['error']['renderer_failed'])
            raise gr.Error(duration=0, message=local["error"]["render_fail"].format(img_file=image_path))


##########################

# Gradio GUI
with gr.Blocks(theme=theme) as demo:
    # ---------------------------------- #
    # 模型面板 / Model panel
    with gr.Row(variant="panel", equal_height=True):
        # 根据配置文件决定模型初始状态显示 / Decide model initial state display based on configuration file
        if config["load_model_on_start"]:
            model_status = gr.Textbox(local["info"]["model_already_loaded"], show_label=False)
        else:
            model_status = gr.Textbox(local["info"]["model_not_loaded"], show_label=False)
            # 模型按钮 / Model buttons
        unload_model_btn = gr.Button(local["btn"]["unload_model"], variant="secondary")
        load_model_btn = gr.Button(local["btn"]["load_model"], variant="primary")
    # ---------------------------------- #
    # OCR 选项卡 / OCR tab
    with gr.Tab(local["tab"]["ocr"]):
        # OCR 相关 / OCR Settings
        with gr.Row():
            with gr.Column():
                # 上传图片 / Upload Image
                img_name = gr.Markdown(local["label"]["img_name_placeholder"])
                upload_img = gr.Image(type="filepath", label=local["label"]["upload_img"])
            # 其他组件 / Other Components
            with gr.Column():
                # 模式 / Mode
                ocr_mode = gr.Dropdown(
                    choices=[(local["mode"]["ocr"], "ocr"), (local["mode"]["format"], "format"),
                             (local["mode"]["fine-grained-ocr"], "fine-grained-ocr"),
                             (local["mode"]["fine-grained-format"], "fine-grained-format"),
                             (local["mode"]["fine-grained-color-ocr"], "fine-grained-color-ocr"),
                             (local["mode"]["fine-grained-color-format"], "fine-grained-color-format"),
                             (local["mode"]["multi-crop-ocr"], "multi-crop-ocr"),
                             (local["mode"]["multi-crop-format"], "multi-crop-format"), (local["mode"]["render"], "render")],
                    label=local["label"]["ocr_mode"], value="ocr")
                # OCR 按钮 / Buttons and Results
                do_ocr = gr.Button(local["btn"]["do_ocr"], variant="primary")
                result = gr.Textbox(label=local["label"]["result"])
    # 渲染器选项卡 / Renderer tab
    with gr.Tab(local["tab"]["renderer"]):
        # 输入 / Input folder path
        input_folder_path = gr.Textbox(label=local["label"]["input_folder_path"], value="imgs", interactive=True)
        with gr.Row(equal_height=True):
            # PDF 转换设置 / PDF convert settings
            batch_pdf_convert_confirm = gr.Checkbox(label=local["label"]["save_as_pdf"], value=True, interactive=True)
            # 清理临时文件 / temp clean
            clean_temp_renderer = gr.Checkbox(label=local["label"]["clean_temp"], value=True, interactive=True)
            # 按钮 / Render button
            batch_render_btn = gr.Button(local["btn"]["render"], variant="primary", scale=2)
    # PDF 选项卡 / PDF tab
    with gr.Tab("PDF"):
        with gr.Row():
            # PDF 文件 / PDF file path
            with gr.Column():
                pdf_file_name = gr.Textbox(value="input.pdf", interactive=False, label=local["label"]["pdf_file_name"])
                pdf_file = gr.File(label=local["label"]["pdf_file"], file_count="single", file_types=[".pdf"])
            # OCR 设置 / set up OCR
            with gr.Column():
                # 模式和 DPI / mode and DPI
                with gr.Group():
                    pdf_ocr_mode = gr.Dropdown(
                        choices=["split-to-image", "render", "merge"],
                        label=local["label"]["ocr_mode"], value="split-to-image", interactive=True)
                    dpi = gr.Number(label=local["label"]["target_dpi"], minimum=72, maximum=300, step=1, value=150)
                    # PDF 转换设置 / PDF conversion settings
                    with gr.Row():
                        # 渲染结果为 PDF / Render the result as PDF
                        pdf_pdf_convert_confirm = gr.Checkbox(label=local["label"]["save_as_pdf"], interactive=True,
                                                              visible=False)
                        # 合并每一页 / Merge per page
                        pdf_pdf_merge_confirm = gr.Checkbox(label=local["label"]["merge_pdf"], interactive=True,
                                                            visible=False)
                # 按钮 / Buttons
                with gr.Row(equal_height=True):
                    pdf_ocr_btn = gr.Button(local["btn"]["pdf_ocr"], variant="primary", scale=2)
                    clean_temp = gr.Checkbox(label=local["label"]["clean_temp"], value=True, interactive=True)
    # GGUF 选项卡 /  GGUF tab
    with gr.Tab("GGUF"):
        gguf_list = os.listdir(os.path.join("gguf", "decoders"))
        dropdown_choices = [(f, os.path.join("gguf", "decoders", f)) for f in gguf_list]
        execution_providers = get_available_providers()
        with gr.Row():
            gguf_models = gr.Dropdown(label=local["label"]["gguf_models"], choices=dropdown_choices, value=dropdown_choices[0][1] if dropdown_choices != [] else None, interactive=True)
            execution_providers = gr.Dropdown(label=local["label"]["execution_providers"], choices=execution_providers, value=execution_providers[0], interactive=True, multiselect=True, max_choices=1)
        with gr.Row():
            upload_img_gguf = gr.Image(type="filepath", label=local["label"]["upload_img"])
            encoder_path = gr.Textbox(value=os.path.join("gguf", "Encoder.onnx"), visible=False)
            with gr.Column():
                ocr_gguf_btn = gr.Button(local["btn"]["ocr_gguf"], variant="primary")
                gguf_result = gr.Textbox(label=local["label"]["gguf_result"], interactive=False)
    # 设置选项卡 / Settings tab
    with gr.Tab(local["tab"]["settings"]):
        # 特殊模式设置 / Special mode settings
        with gr.Row():
            # Fine-grained 设置 / Fine-grained settings
            with gr.Column():
                gr.Markdown(local["label"]["fine_grained_settings"])
                with gr.Row():
                    fine_grained_box_x1 = gr.Number(label=local["label"]["fine_grained_box_x1"], value=0)
                    fine_grained_box_y1 = gr.Number(label=local["label"]["fine_grained_box_y1"], value=0)
                    fine_grained_box_x2 = gr.Number(label=local["label"]["fine_grained_box_x2"], value=0)
                    fine_grained_box_y2 = gr.Number(label=local["label"]["fine_grained_box_y2"], value=0)
                fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"],
                                                 label=local["label"]["fine_grained_color"], value="red")
            # 渲染设置 / Rendering settings
            with gr.Column():
                gr.Markdown(local["label"]["render_settings"])
                with gr.Row(equal_height=True):
                    pdf_convert_confirm = gr.Checkbox(label=local["label"]["save_as_pdf"])
                    clean_temp_render = gr.Checkbox(label=local["label"]["clean_temp"])
                gr.Markdown(local["label"]["new_render_settings"])
                gr.Markdown(local["info"]["developing"])
                use_new_render_mode = gr.Checkbox(label=local["label"]["use_new_render_mode"])
                save_format = gr.Dropdown(choices=["DOCX", "Markdown", "Tex"], label=local["label"]["save_format"],
                                          multiselect=True)
    # 指南选项卡 / Instructions tab
    with gr.Tab(local["tab"]["instructions"]):
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()
        gr.Markdown(instructions)
    # ---------------------------------- #
    # 事件 / events
    # ---------------------------------- #
    # OCR / OCR
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm, clean_temp_render],
        outputs=result
    )
    # ---------------------------------- #
    # 渲染 / Render
    batch_render_btn.click(
        fn=renderer,
        inputs=[input_folder_path, batch_pdf_convert_confirm, clean_temp_renderer],
        outputs=None
    )
    # ---------------------------------- #
    # 更新图片名称 / Updating image name
    upload_img.change(
        fn=update_img_name,
        inputs=upload_img,
        outputs=img_name
    )
    # ---------------------------------- #
    # 更新 PDF OCR 保存 PDF 选项 / Updating save as PDF option for PDF OCR
    pdf_ocr_mode.change(
        fn=update_pdf_conv_conf_visibility,
        inputs=pdf_ocr_mode,
        outputs=pdf_pdf_convert_confirm
    )
    # ----------------------------------- #
    # 更新 PDF OCR DPI 输入框 / Updating target DPI input box for PDF OCR
    pdf_ocr_mode.change(
        fn=update_pdf_dpi_visibility,
        inputs=pdf_ocr_mode,
        outputs=dpi
    )
    # ----------------------------------- #
    # 更新 PDF OCR 合并 PDF 选项 / Updating merge PDF option for PDF OCR
    pdf_pdf_convert_confirm.change(
        fn=update_pdf_merge_conf_visibility,
        inputs=pdf_pdf_convert_confirm,
        outputs=pdf_pdf_merge_confirm
    )
    # ----------------------------------- #
    # 执行PDF OCR / Performing PDF OCR
    pdf_ocr_btn.click(
        fn=pdf_ocr,
        inputs=[pdf_ocr_mode, pdf_file, dpi, pdf_pdf_convert_confirm, pdf_pdf_merge_confirm, clean_temp],
        outputs=None
    )
    # ----------------------------------- #
    # 更新 PDF 名称 / Updating PDF name
    pdf_file.change(
        fn=update_pdf_name,
        inputs=pdf_file,
        outputs=pdf_file_name
    )
    # ----------------------------------- #
    # 加载模型 / Loading model
    load_model_btn.click(
        fn=load_model,
        inputs=None,
        outputs=model_status
    )
    # ----------------------------------- #
    # 卸载模型 / Unloading model
    unload_model_btn.click(
        fn=unload_model,
        inputs=None,
        outputs=model_status
    )
    # ----------------------------------- #
    ocr_gguf_btn.click(
        fn=got_cpp.main,
        inputs=[encoder_path, gguf_models, upload_img_gguf, execution_providers],
        outputs=gguf_result
    )

##########################

demo.launch()
