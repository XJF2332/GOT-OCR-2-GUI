import re

def fix_tex_formatting(content):
    # 精准处理title和author命令的括号（保留section等命令的括号）
    content = re.sub(r'\\title\s*{(.*?)}', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'\\author\s*{(.*?)}', r'\1', content, flags=re.DOTALL)
    return content

def complete_tex(input_content: str) -> str:
    # 仅转换title和author命令，保留其他LaTeX结构
    modified_content = fix_tex_formatting(input_content)

    # 构建完整tex文档
    full_tex = (
        r'\documentclass{ctexart}' + '\n'
        r'\usepackage{amsmath}' + '\n'
        r'\usepackage{amssymb}' + '\n'
        r'\usepackage{graphicx}' + '\n'
        r'\usepackage{hyperref}' + '\n'
        r'\begin{document}' + '\n\n'
        + modified_content + '\n'
        r'\end{document}'
    )

    return full_tex