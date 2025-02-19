import os
import re
import send2trash
from scripts import local, scriptsLogger

##################################

TempCleaner_logger = scriptsLogger.getChild("TempCleaner")


##################################

def find_files(directory: str, regex_pattern: str):
    """
    Find files that matches the regex
    查找目录中符合正则表达式的文件

    Args:
        directory: 要查找的目录 / Directory to find
        regex_pattern: 正则表达式 / RegEx

    Returns:
        匹配的文件列表 / List of matched files
    """
    pattern = re.compile(regex_pattern)
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern.search(file):
                matching_files.append(os.path.join(root, file))
                TempCleaner_logger.debug(local["TempCleaner"]["debug"]["find_files"].format(path=os.path.join(root, file)))
    return matching_files


def cleaner(directory: list[str], regex_pattern: list[str]):
    """
    Clean matched files in the directory
    清理目录中符合正则表达式的文件

    Args:
        directory: 要清理的目录 / Directory to be cleaned
        regex_pattern: 正则表达式 / RegEx

    Returns:
        返回值-含义 / Returns-Meaning
        0-正常 / 0-Success
        1-错误 / 1-Failed
    """
    try:
        TempCleaner_logger.info(local["TempCleaner"]["info"]["cleaning"])
        for dir in directory:
            for pattern in regex_pattern:
                for file in find_files(dir, pattern):
                    send2trash.send2trash(file)
                    TempCleaner_logger.debug(local["TempCleaner"]["debug"]["del_files"].format(path=file))
        return 0
    except Exception as e:
        TempCleaner_logger.error(e)
        return 1