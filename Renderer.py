import json
import os
import sys

# 加载配置文件
print("Loading config...")

# 获取配置文件路径
config_path = os.path.join("Locales", "cli", "config.json")

# 打开配置文件
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

# 获取语言文件路径
lang_file = os.path.join('Locales', 'cli', f'{lang}.json')

# 打开语言文件
with open(lang_file, 'r', encoding='utf-8') as file:
    local = json.load(file)

# 导入transformers库
from transformers import AutoModel, AutoTokenizer
import re
import scripts.html2pdf as html2pdf

# 打印语言文件中的load_models
print(local["load_models"])
# 加载模型
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
# 将模型设置为评估模式并移动到GPU
model = model.eval().cuda()
# 打印语言文件中的load_models_success
print(local["load_models_success"])

# 转换HTML编码
def convert_html_encoding(input_file_path, output_file_path):
    # gb2312
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # utf8
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# 替换HTML内容
def repalce_html_content(input_file_path, output_file_path):
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)

# 执行OCR并渲染为PDF
def do_ocr_and_render(image):
    if not os.path.exists("result"):
        os.makedirs("result")

    # 定义输出HTML路径
    img_name = os.path.basename(image)
    img_name_no_ext = os.path.splitext(img_name)[0]
    html_gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
    html_utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
    html_utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")
    # 渲染OCR结果
    print("Rendering OCR result...")
    model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
    convert_html_encoding(html_gb2312_path, html_utf8_path)
    print(f"Rendered HTML saved at {html_gb2312_path} and {html_utf8_path}")

    # 转换为PDF
    repalce_html_content(html_utf8_path, html_utf8_local_path)
    pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
    html2pdf.output_pdf(html_utf8_local_path, pdf_path)
    print(f"Converted PDF saved at {pdf_path}")

# 从命令行获取参数
if len(sys.argv) < 2:
    print("Usage: python script.py <image_path>")
    sys.exit()

image_path = sys.argv[1]

# 执行OCR并渲染为PDF
do_ocr_and_render(image_path)
