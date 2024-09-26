import json
import os

# 打印加载配置
print("Loading config...")

# 从config.json文件中加载配置
with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

# 从对应语言的json文件中加载本地化字符串
with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
    local = json.load(file)

# 打印导入库
print(local["import_libs"])

# 导入transformers库中的AutoModel和AutoTokenizer
from transformers import AutoModel, AutoTokenizer
# 导入gradio库
import gradio as gr
# 导入os库
import os
# 导入re库
import re
# 导入scripts.html2pdf中的output_pdf函数
import scripts.html2pdf as html2pdf

# 打印加载模型
print(local["load_model"])
# 从预训练模型中加载tokenizer
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
# 从预训练模型中加载模型
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)

# 将模型设置为评估模式并移动到GPU
model = model.eval().cuda()
# 打印模型加载成功
print(local["model_loaded"])


# 定义函数，将文件以GB2312编码读取，并以UTF-8编码写入新文件
def convert_html_encoding(input_file_path, output_file_path):
    # 以GB2312编码读取文件
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # 以UTF-8写入内容到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# 定义函数，替换html文件中的内容
def replace_html_content(input_file_path, output_file_path):
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)


# 定义函数，将html文件转换为pdf文件
def func_save_as_pdf(html_utf8_path, html_utf8_local_path, pdf_path):
    # 替换html文件中的内容
    replace_html_content(html_utf8_path, html_utf8_local_path)
    # 将html文件转换为pdf文件
    html2pdf.output_pdf(html_utf8_local_path, pdf_path)
    # 打印pdf保存成功
    success = local["pdf_save_success"].format(pdf_path=pdf_path)
    return success


# 定义函数，构建文件名
def build_name(img_name):
    # 构建html文件名
    html_gb2312_path = os.path.join("result", f"{img_name}-gb2312.html")
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    return [html_gb2312_path, html_utf8_path]


# 定义函数，提交文件名
def func_submit_name(img_name):
    # 构建html文件名
    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
    html_utf8_local_path = os.path.join("result", f"{img_name}-utf8-local.html")
    pdf_path = os.path.join("result", f"{img_name}-utf8.pdf")
    return html_utf8_path, html_utf8_local_path, pdf_path


# 定义函数，进行OCR识别
def ocr(image, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
        fine_grained_box_y2, OCR_type, fine_grained_color, img_name):
    # 构建OCR框
    box = [fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2, fine_grained_box_y2]

    # 初始化OCR结果
    res = local["ocr_mode_none"]

    # 构建html文件名
    html_gb2312_path = build_name(img_name)[0]
    html_utf8_path = build_name(img_name)[1]

    # 如果result文件夹不存在，则创建
    if not os.path.exists("result"):
        os.makedirs("result")

    # 根据OCR类型进行OCR识别
    if OCR_type == "ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr')
    elif OCR_type == "format":
        res = model.chat(tokenizer, image, ocr_type='format')
    elif OCR_type == "fine-grained-ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
    elif OCR_type == "fine-grained-format":
        res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
    elif OCR_type == "fine-grained-color-ocr":
        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=fine_grained_color)
    elif OCR_type == "fine-grained-color-format":
        res = model.chat(tokenizer, image, ocr_type='format', ocr_color=fine_grained_color)
    elif OCR_type == "multi-crop-ocr":
        res = model.chat_crop(tokenizer, image, ocr_type='ocr')
    elif OCR_type == "multi-crop-format":
        res = model.chat_crop(tokenizer, image, ocr_type='format')
    elif OCR_type == "render":
        # 进行渲染
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        # 将文件以GB2312编码读取，并以UTF-8编码写入新文件
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        # 打印渲染保存成功
        res = local["render_save_success"].format(html_utf8_path=html_utf8_path, html_gb2312_path=html_gb2312_path)
    return res


# gradio gui
with gr.Blocks() as demo:
    # OCR选项卡
    with gr.Tab(local["tab_ocr"]):
        # 行布局
        with gr.Row():
            # 列布局
            with gr.Column():
                # 显示细粒度设置
                gr.Markdown(local["fine_grained_settings"])
                # 行布局
                with gr.Row():
                    # 列布局
                    with gr.Column():
                        # 细粒度框x1
                        fine_grained_box_x1 = gr.Number(label=local["fine_grained_box_x1"], value=0)
                        # 细粒度框y1
                        fine_grained_box_y1 = gr.Number(label=local["fine_grained_box_y1"], value=0)
                    # 列布局
                    with gr.Column():
                        # 细粒度框x2
                        fine_grained_box_x2 = gr.Number(label=local["fine_grained_box_x2"], value=0)
                        # 细粒度框y2
                        fine_grained_box_y2 = gr.Number(label=local["fine_grained_box_y2"], value=0)
                # 细粒度颜色
                fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label=local["fine_grained_color"])
            # 列布局
            with gr.Column():
                # 显示渲染设置
                gr.Markdown(local["render_settings"])
                # 行布局
                with gr.Row():
                    # 图片名
                    img_name = gr.Textbox(label=local["img_name"], value="ocr")
                    # 提交图片名
                    submit_name = gr.Button(local["submit_img_name"])
                # 行布局
                with gr.Row():
                    # html文件路径
                    html_utf8_path = gr.Textbox(label=local["html_file_path"],
                                                value=os.path.join("result", "ocr-utf8.html"), interactive=False)
                    # html本地文件路径
                    html_utf8_local_path = gr.Textbox(label=local["html_local_file_path"],
                                                      value=os.path.join("result", "ocr-utf8-local.html"),
                                                      interactive=False)
                    # pdf文件路径
                    pdf_path = gr.Textbox(label=local["pdf_file_path"], value=os.path.join("result", "ocr-utf8.pdf"),
                                          interactive=False)

        # 显示OCR设置
        gr.Markdown(local["ocr_settings"])

        # 行布局
        with gr.Row():
            # 上传图片
            upload_img = gr.Image(type="filepath", label=local["upload_img"])
            # 列布局
            with gr.Column():
                # OCR模式
                ocr_mode = gr.Dropdown(
                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
                             "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
                    label=local["ocr_mode"])
                # 进行OCR识别
                do_ocr = gr.Button(local["do_ocr_btn"])
                # 显示OCR结果
                result = gr.Textbox(label=local["result"])
                # 行布局
                with gr.Row():
                    # 保存为pdf
                    save_as_pdf = gr.Button(local["save_as_pdf"])
                    # 显示pdf保存信息
                    save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)

    # 指南选项卡
    with gr.Tab(local["tab_instructions"]):
        # 从对应语言的md文件中加载指南
        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
            instructions = file.read()

        # 显示指南
        gr.Markdown(instructions)

    # 点击进行OCR识别
    do_ocr.click(
        fn=ocr,
        inputs=[upload_img, fine_grained_box_x1, fine_grained_box_y1, fine_grained_box_x2,
                fine_grained_box_y2, ocr_mode, fine_grained_color, img_name],
        outputs=result
    )
    # 点击保存为pdf
    save_as_pdf.click(
        fn=func_save_as_pdf,
        inputs=[html_utf8_path, html_utf8_local_path, pdf_path],
        outputs=save_as_pdf_info
    )
    # 点击提交图片名
    submit_name.click(
        fn=func_submit_name,
        inputs=[img_name],
        outputs=[html_utf8_path, html_utf8_local_path, pdf_path]
    )

# 启动gradio界面
demo.launch()
