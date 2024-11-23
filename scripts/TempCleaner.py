import os
import re
import send2trash
import json
from time import sleep
import logging

##################################

TempCleaner_logger = logging.getLogger(__name__)

config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 (The configuration file was not found)")
    print("程序将在3秒后退出")
    sleep(3)
    exit(1)

try:
    lvl = config['logger_level']
    if lvl.lower() == 'debug':
        TempCleaner_logger.setLevel(logging.DEBUG)
    elif lvl.lower() == 'info':
        TempCleaner_logger.setLevel(logging.INFO)
    elif lvl.lower() == 'warning':
        TempCleaner_logger.setLevel(logging.WARNING)
    elif lvl.lower() == 'error':
        TempCleaner_logger.setLevel(logging.ERROR)
    elif lvl.lower() == 'critical':
        TempCleaner_logger.setLevel(logging.CRITICAL)
    else:
        TempCleaner_logger.warning("无效的日志级别，回滚到 INFO 级别 (Invalid log level, rolling back to INFO level)")
        TempCleaner_logger.warning("请检查配置文件 (Please check the configuration file)")
        TempCleaner_logger.setLevel(logging.INFO)
except KeyError:
    TempCleaner_logger.warning("配置文件中未找到日志级别，回滚到 INFO 级别 (The log level was not found in the configuration file, rolling back to INFO level)")
    TempCleaner_logger.warning("请检查配置文件 (Please check the configuration file)")
    TempCleaner_logger.setLevel(logging.INFO)

##################################

def find_files(directory: str, regex_pattern: str):
    """
    查找目录中符合正则表达式的文件

    Args:
        directory: 要查找的目录
        regex_pattern: 正则表达式

    Returns:
        匹配的文件列表
    """
    pattern = re.compile(regex_pattern)
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern.search(file):
                matching_files.append(os.path.join(root, file))
                TempCleaner_logger.debug(f"找到临时文件：{os.path.join(root, file)}")
    return matching_files


def cleaner(directory: list[str], regex_pattern: list[str]):
    """
    清理目录中符合正则表达式的文件
    Args:
        directory: 要清理的目录
        regex_pattern: 正则表达式

    Returns:
        None
    """
    for dir in directory:
        for pattern in regex_pattern:
            for file in find_files(dir, pattern):
                send2trash.send2trash(file)
                TempCleaner_logger.info(f"删除临时文件：{file}")
