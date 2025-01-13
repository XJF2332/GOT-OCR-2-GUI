print("正在初始化 / Initializing")

import logging
from datetime import datetime
import os
import sys
import json
import argparse
from time import sleep
import subprocess

##########################

# 加载配置文件 / Load configuration file
config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 / The configuration file was not found")
    print("程序将在3秒后退出 / Program will exit in 3 seconds")
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
        logger.warning("无效的日志级别，回滚到 INFO 级别 / Invalid log level, rolling back to INFO level")
        logger.warning("请检查配置文件 / Please check the configuration file")
        logger.setLevel(logging.INFO)
except KeyError:
    logger.warning(
        "配置文件中未找到日志级别，回滚到 INFO 级别 / The log level was not found in the configuration file, rolling back to INFO level")
    logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

logger.info("日志记录器已初始化 / The logger has been initialized")

##########################


# 加载语言设置 (Load language settings)
try:
    with open(os.path.join("Locales", "cli", "config.json"), 'r', encoding='utf-8') as file:
        lang_config = json.load(file)
        lang = lang_config['language']
except FileNotFoundError:
    logger.warning(
        "语言配置文件未找到，回滚到简体中文 / Language configuration file not found, rolling back to Simplified Chinese")
    lang = 'zh_CN'

try:
    with open(os.path.join("Locales", "cli", f"{lang}.json"), 'r', encoding='utf-8') as file:
        local = json.load(file)
    with open(os.path.join("Locales", "cli", "instructions", f"{lang}.md"), 'r', encoding='utf-8') as file:
        instructions = file.read()
    logger.info(local['log']['info']['lang_file_loaded'])
except FileNotFoundError:
    logger.critical(f"语言文件未找到 / The language file was not found: {lang}")
    print("程序将在3秒后退出 / Program will exit in 3 seconds")
    sleep(3)
    exit(2)

##########################

# def ocr(image_path, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
#         fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm, clean_temp):
# 参数定义
parser = argparse.ArgumentParser(description="CLI application of GOT-OCR-2")
parser.add_argument('--detailed-help', '-DH', help=local["help"]["detailed_help"], required=False, action='store_true')
parser.add_argument('--path', '-P', help=local["help"]["path"], type=str, required=True)
parser.add_argument('--fg-box-x1', '-X1', help=local["help"]["fg_box_x1"], type=int, default=0, required=False)
parser.add_argument('--fg-box-y1', '-Y1', help=local["help"]["fg_box_y1"], type=int, default=0, required=False)
parser.add_argument('--fg-box-x2', '-X2', help=local["help"]["fg_box_x2"], type=int, default=0, required=False)
parser.add_argument('--fg-box-y2', '-Y2', help=local["help"]["fg_box_y2"], type=int, default=0, required=False)
parser.add_argument('--save-as-pdf', '-PDF', help=local["help"]["save_as_pdf"], type=bool, default=True, required=False)
parser.add_argument('--clean-temp', '-CT', help=local["help"]["clean_temp"], type=bool, default=True, required=False)
parser.add_argument('--fg-color', '-C', help=local["help"]["fg_color"], type=str,
                    choices=[
                        "red",
                        "green",
                        "blue"],
                    default="red", required=False)
parser.add_argument('--image-ocr-mode', '-IM', help=local["help"]["image_ocr_mode"], type=str,
                    choices=['ocr',
                             'format',
                             'fine-grained-ocr',
                             'fine-grained-format',
                             'fine-grained-color-ocr',
                             'fine-grained-color-format',
                             'multi-crop-ocr',
                             'multi-crop-format',
                             'render'],
                    default='ocr', required=False)
parser.add_argument('--pdf_ocr_mode', '-PM', help=local["help"]["pdf_ocr_mode"], type=str,
                    choices=[
                        "split",
                        "merge"
                        "render"
                    ], default='render', required=False)

# 帮助的特殊行为
if '--detailed-help' in sys.argv and len(sys.argv) == 2:
    print(instructions)
    input(local["instructions"]["quit"])
    exit(0)

args = parser.parse_args()

##########################

# 参数处理
# OCR对象
path = args.path
if path.endswith('.pdf'):
    ocr_object = "pdf"
    logger.debug(local['log']['debug']['pdf_detected'].format(path=path))
    logger.info(local['log']['info']['ocr_object_pdf'])
    print(local['feedbacks']['ocr_object_pdf'])
elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg'):
    ocr_object = "image"
    logger.debug(local['log']['debug']['image_detected'].format(path=path))
    logger.info(local['log']['info']['ocr_object_image'])
    print(local['feedbacks']['ocr_object_image'])
elif os.path.isdir(path):
    logger.critical(local['log']['critical']['dir_not_supported'].format(path=path))
    logger.critical(local['instructions']['timed_quit'])
    sleep(3)
    exit(3)
elif not os.path.exists(path):
    logger.critical(local['log']['critical']['file_not_found'].format(path=path))
    logger.critical(local['instructions']['timed_quit'])
    sleep(3)
    exit(4)
else:
    logger.critical(local["log"]["critical"]["unsupported_file_type"].format(path=path))
    logger.critical(local["instructions"]["timed_quit"])
    sleep(3)
    exit(5)

##########################

print(local["feedbacks"]["loading"])

import glob
import scripts.Renderer as Renderer
import scripts.PDF2ImagePlusRenderer as PDFHandler
import scripts.PDFMerger as PDFMerger
import scripts.TempCleaner as TempCleaner
from transformers import AutoModel, AutoTokenizer

##########################

logger.info(local["log"]["info"]["model_loading"])
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
logger.info(local["log"]["info"]["model_loaded"])


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
    logger.debug(f"[extract_pdf_pattern] {local['log']['debug']['filename_split_res'].format(res=parts)}")

    # 检查最后一部分是否为 '0.pdf' (Check if the last part is '0.pdf')
    if len(parts) == 2 and parts[1] == '0.pdf':
        return parts[0]
    else:
        logger.error(
            f"[extract_pdf_pattern] {local['log']['error']['filename_format_error'].format(format='<string>_0.pdf')}")
        raise ValueError(local["error"]["filename_format_error"].format(format='<string>_0.pdf'))


##########################

# 进行 OCR 识别 / Performing OCR recognition
def ocr(image_path, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, ocr_mode, fine_grained_color, pdf_convert_confirm, clean_temp):
    # 默认值 (Default value)
    ocr_res = local["error"]["ocr_mode_none"]

    if not os.path.exists("result"):
        os.makedirs("result")
        logger.info(f"[ocr] {local['log']['warning']['folder_created'].format(folder='result')}")

    try:
        # 根据 OCR 类型进行 OCR 识别 (Performing OCR based on OCR type)
        logger.info(f"[ocr] {local['log']['info']['performing_ocr']}")
        if ocr_mode == "ocr":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='ocr')}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='ocr')
        elif ocr_mode == "format":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='format')}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='format')
        elif ocr_mode == "fine-grained-ocr":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='fine-grained-ocr')}")
            # 构建 OCR 框 (Building OCR box)
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            logger.debug(f"[ocr] {local['log']['debug']['fg_box'].format(box=box)}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_box=box)
        elif ocr_mode == "fine-grained-format":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='fine-grained-format')}")
            # 构建 OCR 框 (Building OCR box)
            box = f"[{fine_grained_box_x1}, {fine_grained_box_y1}, {fine_grained_box_x2}, {fine_grained_box_y2}]"
            logger.debug(f"[ocr] {local['log']['debug']['fg_box'].format(box=box)}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='format', ocr_box=box)
        elif ocr_mode == "fine-grained-color-ocr":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='fine-grained-color-ocr')}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_color=fine_grained_color)
        elif ocr_mode == "fine-grained-color-format":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='fine-grained-color-format')}")
            ocr_res = model.chat(tokenizer, image_path, ocr_type='format', ocr_color=fine_grained_color)
        elif ocr_mode == "multi-crop-ocr":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='multi-crop-ocr')}")
            ocr_res = model.chat_crop(tokenizer, image_path, ocr_type='ocr')
        elif ocr_mode == "multi-crop-format":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='multi-crop-format')}")
            ocr_res = model.chat_crop(tokenizer, image_path, ocr_type='format')
        elif ocr_mode == "render":
            logger.debug(f"[ocr] {local['log']['debug']['ocr_mode'].format(mode='render')}")
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=image_path,
                                      convert_to_pdf=pdf_convert_confirm, wait=config["pdf_render_wait"],
                                      time=config["pdf_render_wait_time"])
            image_name_with_extension = os.path.basename(image_path)
            logger.debug(f"[ocr] {local['log']['debug']['got_image_name'].format(name=image_name_with_extension)}")
            if success:
                ocr_res = local["log"]["info"]["render_success"].format(img_file=image_name_with_extension)
                logger.info(f"[ocr] {local['log']['info']['render_completed'].format(file=image_name_with_extension)}")
                if clean_temp and pdf_convert_confirm:
                    logger.info(f"[ocr] {local['log']['info']['cleaning_temp']}")
                    TempCleaner.cleaner(["result"],
                                        [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8.html",
                                         f"{os.path.splitext(image_name_with_extension)[0]}-utf8-local.html"])
                if clean_temp and not pdf_convert_confirm:
                    logger.info(f"[ocr] {local['log']['info']['cleaning_temp']}")
                    TempCleaner.cleaner(["result"], [f"{os.path.splitext(image_name_with_extension)[0]}-gb2312.html"])
                else:
                    logger.info(f"[ocr] {local['log']['info']['temp_clean_skipped']}")
            else:
                ocr_res = local["error"]["render_fail"].format(file=image_name_with_extension)
        logger.info(local['log']['info']['ocr_completed'])
        return ocr_res
    except AttributeError:
        logger.error(f"[ocr] {local['log']['error']['no_model_or_img']}")
        return local["error"]["no_model_or_img"]
    except Exception as e:
        logger.error(f"[ocr] {local['log']['error']['ocr_failed']}: {e}")
        return str(e)


##########################

# 执行 PDF OCR / Performing PDF OCR
def pdf_ocr(mode, pdf, target_dpi, pdf_convert, pdf_merge, temp_clean):
    """

    Args:
        mode: pdf ocr 模式
        pdf: pdf 文件路径
        target_dpi: 分割 pdf 为图片时使用的 dpi
        pdf_convert: 是否把渲染结果转换为 pdf
        pdf_merge: 是否合并转换后的 pdf
        temp_clean: 是否清理临时文件

    Returns:

    """
    logger.info(local['log']['info']['pdf_ocr_start'])
    print(local['feedbacks']['pdf_ocr_start'])
    if not pdf:
        logger.error(local['log']['error']['no_pdf_uploaded'])
        raise ValueError(local["error"]["no_pdf"])
    pdf_name = os.path.basename(pdf)
    logger.debug(local['log']['debug']['got_pdf_name'].format(name=pdf_name))
    # ---------------------------------- #
    # 分割模式 / Split mode
    if mode == "split-to-image":
        logger.debug(local['log']['debug']['pdf_mode_split'])
        logger.info(local['log']['info']['pdf_split_start'].format(pdf=pdf_name))
        print(local['feedbacks']['pdf_splitting_started'])
        success = PDFHandler.split_pdf(pdf_path=pdf, img_path="imgs", target_dpi=target_dpi)
        if success:
            logger.info(local['log']['info']['pdf_split_success'].format(pdf=pdf_name))
            print(local['feedbacks']['pdf_split_success'])
        else:
            logger.error(local['log']['error']['pdf_split_fail'])
    # ---------------------------------- #
    # 渲染模式 / Render mode
    elif mode == "render":
        logger.debug(local['log']['debug']['pdf_mode_render'])
        logger.info(local['log']['info']['pdf_render_started'].format(pdf=pdf_name))
        print(local['feedbacks']['pdf_render_started'].format(pdf=pdf_name))
        success = PDFHandler.pdf_renderer(model=model,
                                          tokenizer=tokenizer,
                                          pdf_path=pdf,
                                          target_dpi=target_dpi,
                                          pdf_convert=pdf_convert,
                                          wait=config["pdf_render_wait"],
                                          time=config["pdf_render_wait_time"])
        # 渲染成功判定 / Rendering success determination
        if success:
            logger.info(local['log']['info']['pdf_render_success'].format(pdf=pdf_name))
            print(local['feedbacks']['pdf_render_success'].format(pdf=pdf_name))
            # 自动合并 / Auto merge
            pattern_pdf = f"{os.path.splitext(pdf_name)[0]}_0.pdf"
            pattern_html = f"{os.path.splitext(pdf_name)[0]}_\d+-.*\.html"
            pattern_pdf_temp = f"{os.path.splitext(pdf_name)[0]}_\d+-.*\.html"
            if pdf_merge:  # 决定是否要合并 / Deciding whether to merge or not
                logger.info(local['log']['info']['pdf_merge_started'].format(pdf=pdf_name))
                success = PDFMerger.merge_pdfs(prefix=extract_pdf_pattern(pattern_pdf))
                # 合并成功判定 / Merging success determination
                if success:
                    logger.info(local['log']['info']['pdf_merge_success'].format(pdf=pdf_name))
                    print(local['feedbacks']['pdf_merge_success'].format(pdf=pdf_name))
                    # 合并成功，清理临时文件 / Merged successfully, cleaning up temporary files
                    if temp_clean:
                        logger.info(local['log']['info']['pdf_temp_cleaning'])
                        logger.debug(local['log']['debug']['got_temp_file_pattern'].format(
                            pattern=[pattern_pdf_temp, pattern_html]))
                        TempCleaner.cleaner(["result"], [pattern_pdf_temp, pattern_html])
                    else:
                        logger.info(local['log']['info']['pdf_temp_cleaning_skipped'])
                else:
                    logger.error(local['log']['error']['pdf_merge_fail'].format(pdf=pdf_name))
                    raise RuntimeError(local['error']['pdf_merge_fail'].format(pdf=pdf_name))
            else:  # 不合并 / Not merging
                logger.info(local['log']['info']['merge_skipped'].format(pdf=pdf_name))
        else:  # 渲染失败 / Failed to render
            logger.error(local['log']['error']['pdf_render_fail'].format(pdf=pdf_name))
            raise RuntimeError(local['error']['pdf_render_fail'].format(pdf=pdf_name))
    # ---------------------------------- #
    # 合并模式 / Merging mode
    elif mode == "merge":
        logger.debug(local['log']['debug']['pdf_mode_merge'])
        print(local['feedbacks']['pdf_merge_start'].format(pdf=pdf_name))
        prefix = extract_pdf_pattern(pdf_name)
        success = PDFMerger.merge_pdfs(prefix=prefix)
        # 合并成功判定 / Merging success determination
        if success:
            logger.info(local['log']['info']['pdf_merge_success'].format(pdf=pdf_name))
            print(local['feedbacks']['pdf_merge_success'].format(pdf=pdf_name))
            if temp_clean:
                # 合并成功，清理临时文件 / Merged successfully, cleaning up temporary files
                logger.info(local['log']['info']['pdf_temp_cleaning'])
                logger.debug(local['log']['debug']['got_temp_file_pattern'].format(
                    pattern=f'{extract_pdf_pattern(pdf_name)}_\d+.pdf'))
                TempCleaner.cleaner(["result"], [f"{extract_pdf_pattern(pdf_name)}_\d+.pdf"])
            else:
                logger.info(local['log']['info']['pdf_temp_cleaning_skipped'])
        else:
            logger.error(local['log']['error']['pdf_merge_failed'].format(name=pdf_name))

##########################

if ocr_object == "image":
    res = ocr(image_path=args.path, fine_grained_box_x1=args.fg_box_x1, fine_grained_box_y1=args.fg_box_y1,
              fine_grained_box_x2=args.fg_box_x2, fine_grained_box_y2=args.fg_box_y2, fine_grained_color=args.fg_color,
              ocr_mode=args.image_ocr_mode, pdf_convert_confirm=args.save_as_pdf, clean_temp=args.clean_temp)
    print(res)
elif ocr_object == "pdf":
    pdf_ocr(mode=args.pdf_ocr_mode, pdf=args.path, target_dpi=150, pdf_convert=True, pdf_merge=True, temp_clean=True)