import logging
from datetime import datetime
import os
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
scriptsLogger = logging.getLogger(__name__)

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
        scriptsLogger.setLevel(logging.DEBUG)
    elif lvl.lower() == 'warning':
        scriptsLogger.setLevel(logging.WARNING)
    elif lvl.lower() == 'error':
        scriptsLogger.setLevel(logging.ERROR)
    elif lvl.lower() == 'critical':
        scriptsLogger.setLevel(logging.CRITICAL)
    else:
        scriptsLogger.setLevel(logging.INFO)
except KeyError:
    scriptsLogger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
scriptsLogger.addHandler(console)

##########################


# 加载语言设置 / Load language settings
try:
    with open(os.path.join("Locales", "scripts", "config.json"), 'r', encoding='utf-8') as file:
        lang_config = json.load(file)
        lang = lang_config['language']
except FileNotFoundError:
    lang = 'zh_CN'

try:
    with open(os.path.join("Locales", "scripts", f"{lang}.json"), 'r', encoding='utf-8') as file:
        local = json.load(file)
except FileNotFoundError:
    print(f"语言文件未找到 / Language file not found: {lang}")