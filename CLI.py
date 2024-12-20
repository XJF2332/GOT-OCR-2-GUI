print("正在初始化(Initializing)")

import logging
from datetime import datetime
import os
import json
import argparse
from time import sleep

##########################

# 加载配置文件 (Load configuration file)
config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 (The configuration file was not found)")
    print("程序将在3秒后退出")
    sleep(3)
    exit(1)

##########################

# 日志记录器 (Logger)
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logger = logging.getLogger(__name__)

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
        logger.warning("无效的日志级别，回滚到 INFO 级别 (Invalid log level, rolling back to INFO level)")
        logger.warning("请检查配置文件 (Please check the configuration file)")
        logger.setLevel(logging.INFO)
except KeyError:
    logger.warning(
        "配置文件中未找到日志级别，回滚到 INFO 级别 (The log level was not found in the configuration file, rolling back to INFO level)")
    logger.warning("请检查配置文件 (Please check the configuration file)")
    logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

logger.info("日志记录器已初始化 (The logger has been initialized)")

##########################


# 加载语言设置 (Load language settings)
try:
    with open(os.path.join("Locales", "cli", "config.json"), 'r', encoding='utf-8') as file:
        lang_config = json.load(file)
        lang = lang_config['language']
except FileNotFoundError:
    logger.warning(
        "语言配置文件未找到，回滚到简体中文 (The language configuration file was not found, rolling back to Simplified Chinese)")
    lang = 'zh_CN'

try:
    with open(os.path.join("Locales", "cli", f"{lang}.json"), 'r', encoding='utf-8') as file:
        local = json.load(file)
    with open(os.path.join("Locales", "cli", "instructions", f"{lang}.md"), 'r', encoding='utf-8') as file:
        instructions = file.read()
    logger.info(f"语言文件已加载 (The language file has been loaded): {lang}")
except FileNotFoundError:
    logger.critical(f"语言文件未找到 (The language file was not found): {lang}")
    print("程序将在3秒后退出")
    sleep(3)
    exit(1)

##########################

parser = argparse.ArgumentParser(description=instructions)
parser.add_argument('--object', '-O', help=local["help"]["object"], type=str, choices=['img', 'pdf'], default='img', required=False)
parser.add_argument('--image-path', '-I', help=local["help"]["image_path"], type=str, required=False)
parser.add_argument('--image-ocr-mode', '-IM', help=local["help"]["image_ocr_mode"], type=str,
                    choices=['ocr', 'format', 'fine-grained-ocr', 'fine-grained-format', 'fine-grained-color-ocr',
                             'fine-grained-color-format', 'multi-crop-ocr', 'multi-crop-format', 'render'],
                    default='ocr', required=False)
parser.add_argument('--fg-box-x1', '-FGX1', help=local["help"]["fg_box_x1"], type=int, required=False)
parser.add_argument('--fg-box-y1', '-FGY1', help=local["help"]["fg_box_y1"], type=int, required=False)
parser.add_argument('--fg-box-x2', '-FGX2', help=local["help"]["fg_box_x2"], type=int, required=False)
parser.add_argument('--fg-box-y2', '-FGY2', help=local["help"]["fg_box_y2"], type=int, required=False)

args = parser.parse_args()

##########################

print("正在加载(Loading)")

import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler
import scripts.PDFMerger as PDFMerger
import scripts.TempCleaner as TempCleaner
from transformers import AutoModel, AutoTokenizer

##########################

logger.info("[load_model] 正在加载模型 (Loading model)")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
logger.info("[load_model] 模型加载完成 (Model loading completed)")


##########################

# 提取prefix (Extracting prefix)
def extract_pdf_pattern(filename):
    """
    从文件名中提取前缀，如果文件名不满足格式 <string>_0.pdf, 则抛出 ValueError 异常
    (Extracts the prefix from the filename, if the filename does not meet the format <string>_0.pdf, a ValueError exception is raised)
    :param filename: 文件名 (Filename)
    :return: 前缀 (Prefix)
    """
    # 在最后一个下划线处分割文件名 (Split the filename at the last underscore)
    parts = filename.rsplit('_')
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
def ocr(image_path, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm, clean_temp):
    # 默认值 (Default value)
    res = local["error"]["ocr_mode_none"]

    if not os.path.exists("result"):
        os.makedirs("result")
        logger.info("[ocr] result 文件夹不存在，已创建 (Result folder doesn't exists, created)")

    try:
        # 根据 OCR 类型进行 OCR 识别 (Performing OCR based on OCR type)
        logger.info("[ocr] 正在执行 OCR (Performing OCR)")
        if ocr_mode == "ocr":
            logger.debug("[ocr] 当前 OCR 模式：ocr (Current ocr mode: ocr)")
            res = model.chat(tokenizer, image_path, ocr_type='ocr')
        elif ocr_mode == "format":
            logger.debug("[ocr] 当前 OCR 模式：format (Current ocr mode: format)")
            res = model.chat(tokenizer, image_path, ocr_type='format')
        elif ocr_mode == "fine-grained-ocr":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-ocr (Current ocr mode: fine-grained-ocr)")
            # 构建 OCR 框 (Building OCR box)
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            logger.debug(f"[ocr] 当前 OCR 框 (Current ocr box): {box}")
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_box=box)
        elif ocr_mode == "fine-grained-format":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-format (Current ocr mode: fine-grained-format)")
            # 构建 OCR 框 (Building OCR box)
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            logger.debug(f"[ocr] 当前 OCR 框 (Current ocr box): {box}")
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_box=box)
        elif ocr_mode == "fine-grained-color-ocr":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-color-ocr (Current ocr mode: fine-grained-color-ocr)")
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_color=fine_grained_color)
        elif ocr_mode == "fine-grained-color-format":
            logger.debug("[ocr] 当前 OCR 模式：fine-grained-color-format (Current ocr mode: fine-grained-color-format)")
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_color=fine_grained_color)
        elif ocr_mode == "multi-crop-ocr":
            logger.debug("[ocr] 当前 OCR 模式：multi-crop-ocr (Current ocr mode: multi-crop-ocr)")
            res = model.chat_crop(tokenizer, image_path, ocr_type='ocr')
        elif ocr_mode == "multi-crop-format":
            logger.debug("[ocr] 当前 OCR 模式：multi-crop-format (Current ocr mode: multi-crop-format)")
            res = model.chat_crop(tokenizer, image_path, ocr_type='format')
        elif ocr_mode == "render":
            logger.debug("[ocr] 当前 OCR 模式：render (Current ocr mode: render)")
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                      convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                      time=config["pdf_render_wait_time"])
            image_name_with_extension = os.path.basename(image_path)
            logger.debug(f"[ocr] 获取到图像名称 (Got image name): {image_name_with_extension}")
            if success:
                res = local["info_render_success"].format(img_file=image_name_with_extension)
                logger.info("[ocr] 渲染已完成 (Render completed)")
                if clean_temp and pdf_convert_confirm:
                    logger.info("[ocr] 正在清理临时文件 (Cleaning temporary files)")
                    TempCleaner.cleaner(["result"],
                                        [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8-local.html"])
                if clean_temp and not pdf_convert_confirm:
                    logger.info("[ocr] 正在清理临时文件 (Cleaning temporary files)")
                    TempCleaner.cleaner(["result"], [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html"])
                else:
                    logger.info("[ocr] 跳过临时文件清理 (Skip cleaning temporary files)")
            else:
                res = local["error_render_fail"].format(img_file=image_name_with_extension)
        logger.info("[ocr] OCR 已完成 (OCR completed)")
        return res
    except AttributeError:
        logger.error(
            f"[ocr] 你看起来没有加载模型，或没有上传图片 (You seem to have not loaded the model or uploaded an image)")
        return local["error_no_model_or_img"]
    except Exception as e:
        logger.error(f"[ocr] OCR 失败 (OCR failed): {e}")
        return str(e)


##########################
# test
test_res = ocr(args.image_path, 0,0,0,0, args.image_ocr_mode, 'red', False, False)
print(test_res)