import os
import re
import send2trash


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
    return matching_files


def cleaner(directory: str, regex_pattern: str):
    """
    清理目录中符合正则表达式的文件
    Args:
        directory: 要清理的目录
        regex_pattern: 正则表达式

    Returns:
        None
    """
    files = find_files(directory, regex_pattern)
    for file in files:
        send2trash.send2trash(file)
