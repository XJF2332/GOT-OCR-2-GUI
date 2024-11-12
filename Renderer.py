import os
import logging
from datetime import datetime

############################

# 日志记录器
logger = logging.getLogger('Renderer')
logger.setLevel(logging.DEBUG)

# 时间 (Time)
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# 文件处理器 (File handler)
if not os.path.exists("Logs"):
    os.makedirs("Logs")
log_name = os.path.join("Logs", f"log_Renderer_{current_time}.log")
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

############################

import json
import glob

# 打开语言配置文件
logger.info("正在加载语言配置 (Loading language configurations)")
lang_config_path = os.path.join("Locales", "cli", "config.json")
try:
    with open(lang_config_path, 'r', encoding='utf-8') as file:
        lang_config = json.load(file)
        lang = lang_config['language']
        logger.info(f"当前语言 (Current language): {lang}")
except FileNotFoundError:
    logger.critical("语言配置文件未找到 (Language configuration file not found)")
    exit(1)

# 打开语言文件
try:
    lang_file = os.path.join('Locales', 'cli', f'{lang}.json')
    with open(lang_file, 'r', encoding='utf-8') as file:
        local = json.load(file)
        logger.info(f"语言文件加载成功 (Language file loaded successfully)")
except FileNotFoundError:
    logger.critical("语言文件未找到 (Language file not found)")
    exit(1)
except NameError:
    logger.critical("无效的语言配置 (Language configuration is invalid)")
    exit(1)

# 打开配置文件
logger.info("正在加载配置 (Loading configurations)")
config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        logger.info("配置文件加载成功 (Configuration file loaded successfully)")
except FileNotFoundError:
    logger.critical(local["critical_config_notfound"])
    exit(1)

# 导入transformers库
logger.info("正在导入库 (Importing libraries)")
from transformers import AutoModel, AutoTokenizer
import scripts.Renderer as Render

# 加载模型
logger.info("正在加载模型 (Loading models)")
try:
    tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
    model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                      use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    logger.info("模型加载成功 (Model loaded successfully)")
    print(local["info_load_models_success"])
except Exception as e:
    logger.critical(local["critical_load_models_fail"])
    exit(1)

pdf_convert = input(local["pdf_convert_ask"])
if pdf_convert.lower() == "y":
    convert_confirm = True
else:
    convert_confirm = False

# 读取imgs文件夹下的jpg和png图片
imgs_path = os.path.join(os.getcwd(), 'imgs')
image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))
logger.debug(f"图片文件列表 (Image file list): {image_files}")

# 逐个发送图片给renderer的render函数
for image_path in image_files:
    logger.info(f"正在渲染图片 (Rendering image): {image_path}")
    success = Render.render(model=model, tokenizer=tokenizer, image_path=image_path, convert_to_pdf=convert_confirm,
                            wait=config["pdf_render_wait"], time=config["pdf_render_wait_time"])
    if success:
        logger.info(f"图片渲染成功 (Image rendering successful): {image_path}")
        print(local["renderer_success"].format(img_path=image_path))
    else:
        logger.error(f"图片渲染失败 (Image rendering failed): {image_path}")
        print(local["renderer_fail"].format(img_path=image_path))
