import fitz
import json
import os
import glob

from pathlib import Path

def remove_suffix(file_name):
    return Path(file_name).stem

file_list=[]#新建一个空列表用于存放文件全路径
file_dir=r'./pdf/'#指定即将遍历的文件夹路径
for files in os.walk(file_dir):#遍历指定文件夹及其下的所有子文件夹
    for file in files[2]:#遍历每个文件夹里的所有文件，（files[2]:母文件夹和子文件夹下的所有文件信息，files[1]:子文件夹信息，files[0]:母文件夹信息）
        if os.path.splitext(file)[1]=='.PDF' or os.path.splitext(file)[1]=='.pdf':#检查文件后缀名,逻辑判断用==
            # file_list.append(file)#筛选后的文件名为字符串，将得到的文件名放进去列表，方便以后调用
            file_list.append(file_dir+file)#给文件名加入文件夹路径
            
print(file_list)

# 加载pdf 文件
#doc = fitz.open("/test/demo.pdf")
doc = fitz.open(file_list[0])


def covert2pic(file_path, zoom, png_path):
    doc = fitz.open(file_path)
    file_name= remove_suffix(file_path)
    total = doc.page_count
    for pg in range(total):
        page = doc[pg]
        zoom = int(zoom)  # 值越大，分辨率越高，文件越清晰
        rotate = int(0)

        trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).prerotate(rotate)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        if not os.path.exists(png_path):
            os.mkdir(png_path)
        save = os.path.join(png_path, file_name+'{}.png'.format(pg+1))
        pm.save(save)
    doc.close()


pdfPath = file_list[0]
imagePath = './imgs'
covert2pic(pdfPath, 200, imagePath)


# 打开配置文件
print("Loading config...")
config_path = os.path.join("Locales", "cli", "config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

# 打开语言文件
lang_file = os.path.join('Locales', 'cli', f'{lang}.json')
with open(lang_file, 'r', encoding='utf-8') as file:
    local = json.load(file)

# 导入transformers库
print(local["info_import_libs"])
from transformers import AutoModel, AutoTokenizer
import scripts.Renderer as Render

# 加载模型
print(local["load_models"])
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print(local["load_models_success"])

pdf_convert = input(local["pdf_convert_ask"])
if pdf_convert == "y" or pdf_convert == "Y":
    convert_confirm = True
else:
    convert_confirm = False

# 读取imgs文件夹下的jpg和png图片
imgs_path = os.path.join(os.getcwd(), 'imgs')
image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

# 逐个发送图片给renderer的render函数
allres=''
for image_path in image_files:
    success,res = Render.render(model, tokenizer, image_path, convert_confirm)
    if success:
        print(local["renderer_success"].format(img_path=image_path))
        allres= allres + '\n' + res
        print(allres)
    else:
        print(local["renderer_fail"].format(img_path=image_path))

#print(allres)







## 从config.json文件中加载配置
#print("Loading config...")
#with open(os.path.join("Locales", "gui", "config.json"), 'r', encoding='utf-8') as file:
#    config = json.load(file)
#    lang = config['language']

## 从对应语言的json文件中加载本地化字符串
#with open(os.path.join("Locales", "gui", f"{lang}.json"), 'r', encoding='utf-8') as file:
#    local = json.load(file)

## 导入库
#print(local["info_import_libs"])
#from transformers import AutoModel, AutoTokenizer
#import gradio as gr
#import os
#import re
#import scripts.html2pdf as html2pdf

## 加载模型
#print(local["info_load_model"])
#tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
#model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
#                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
#model = model.eval().cuda()
#print(local["info_model_loaded"])


## 将文件以GB2312编码读取，并以UTF-8编码写入新文件
#def convert_html_encoding(input_file_path, output_file_path):
#    # 以GB2312编码读取文件
#    with open(input_file_path, 'r', encoding='gb2312') as file:
#        content = file.read()

#    # 以UTF-8写入内容到新文件
#    with open(output_file_path, 'w', encoding='utf-8') as file:
#        file.write(content)


## 替换html文件中的内容
#def replace_html_content(input_file_path, output_file_path):
#    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
#    replacement = 'markdown-it.js'
#    with open(input_file_path, 'r', encoding='utf-8') as file:
#        content = file.read()
#    new_html_content = re.sub(pattern, replacement, content)
#    with open(output_file_path, 'w', encoding='utf-8') as file:
#        file.write(new_html_content)


## 将html文件转换为pdf文件
#def func_save_as_pdf(html_utf8_path, html_utf8_local_path, pdf_path):
#    # 替换html文件中的内容
#    replace_html_content(html_utf8_path, html_utf8_local_path)
#    # 将html文件转换为pdf文件
#    html2pdf.output_pdf(html_utf8_local_path, pdf_path)
#    # 打印pdf保存成功
#    success = local["info_pdf_save_success"].format(pdf_path=pdf_path)
#    return success


## 构建文件名
#def build_name(img_name):
#    # 构建html文件名
#    html_gb2312_path = os.path.join("result", f"{img_name}-gb2312.html")
#    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
#    return [html_gb2312_path, html_utf8_path]


## 提交文件名
#def func_submit_name(img_name):
#    # 构建html文件名
#    html_utf8_path = os.path.join("result", f"{img_name}-utf8.html")
#    html_utf8_local_path = os.path.join("result", f"{img_name}-utf8-local.html")
#    pdf_path = os.path.join("result", f"{img_name}-utf8.pdf")
#    return html_utf8_path, html_utf8_local_path, pdf_path


## 进行OCR识别
#def ocr(image, label_fine_grained_box_x1, label_fine_grained_box_y1, label_fine_grained_box_x2,
#        label_fine_grained_box_y2, OCR_type, label_fine_grained_color, img_name):
#    # 构建OCR框
#    box = [label_fine_grained_box_x1, label_fine_grained_box_y1, label_fine_grained_box_x2, label_fine_grained_box_y2]

#    # 未选择模式
#    res = local["error_ocr_mode_none"]

#    # 构建html文件名
#    html_gb2312_path = build_name(img_name)[0]
#    html_utf8_path = build_name(img_name)[1]

#    # 如果result文件夹不存在，则创建
#    if not os.path.exists("result"):
#        os.makedirs("result")

#    # 根据OCR类型进行OCR识别
#    if OCR_type == "ocr":
#        res = model.chat(tokenizer, image, ocr_type='ocr')
#    elif OCR_type == "format":
#        res = model.chat(tokenizer, image, ocr_type='format')
#    elif OCR_type == "fine-grained-ocr":
#        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
#    elif OCR_type == "fine-grained-format":
#        res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
#    elif OCR_type == "fine-grained-color-ocr":
#        res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=label_fine_grained_color)
#    elif OCR_type == "fine-grained-color-format":
#        res = model.chat(tokenizer, image, ocr_type='format', ocr_color=label_fine_grained_color)
#    elif OCR_type == "multi-crop-ocr":
#        res = model.chat_crop(tokenizer, image, ocr_type='ocr')
#    elif OCR_type == "multi-crop-format":
#        res = model.chat_crop(tokenizer, image, ocr_type='format')
#    elif OCR_type == "render":
#        # 进行渲染
#        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
#        # 将文件以GB2312编码读取，并以UTF-8编码写入新文件
#        convert_html_encoding(html_gb2312_path, html_utf8_path)
#        # 打印渲染保存成功
#        res = local["info_render_save_success"].format(html_utf8_path=html_utf8_path, html_gb2312_path=html_gb2312_path)
#    return res


## gradio gui
#with gr.Blocks() as demo:
#    # OCR选项卡
#    with gr.Tab(local["tab_ocr"]):
#        with gr.Row():
#            with gr.Column():
#                # Fine-grained 设置
#                gr.Markdown(local["label_fine_grained_settings"])
#                with gr.Row():
#                    with gr.Column():
#                        label_fine_grained_box_x1 = gr.Number(label=local["label_fine_grained_box_x1"], value=0)
#                        label_fine_grained_box_y1 = gr.Number(label=local["label_fine_grained_box_y1"], value=0)
#                    with gr.Column():
#                        label_fine_grained_box_x2 = gr.Number(label=local["label_fine_grained_box_x2"], value=0)
#                        label_fine_grained_box_y2 = gr.Number(label=local["label_fine_grained_box_y2"], value=0)
#                label_fine_grained_color = gr.Dropdown(choices=["red", "green", "blue"], label=local["label_fine_grained_color"])
#            with gr.Column():
#                # 渲染设置
#                gr.Markdown(local["label_render_settings"])
#                with gr.Row():
#                    img_name = gr.Textbox(label=local["img_name"], value="ocr")
#                    submit_name = gr.Button(local["btn_submit_img_name"])
#                with gr.Row():
#                    html_utf8_path = gr.Textbox(label=local["label_html_file_path"],
#                                                value=os.path.join("result", "ocr-utf8.html"), interactive=False)
#                    html_utf8_local_path = gr.Textbox(label=local["label_html_local_file_path"],
#                                                      value=os.path.join("result", "ocr-utf8-local.html"),
#                                                      interactive=False)
#                    pdf_path = gr.Textbox(label=local["label_pdf_file_path"], value=os.path.join("result", "ocr-utf8.pdf"),
#                                          interactive=False)
#        # OCR设置
#        gr.Markdown(local["label_ocr_settings"])

#        with gr.Row():
#            label_upload_img = gr.Image(type="filepath", label=local["label_upload_img"])
#            with gr.Column():
#                ocr_mode = gr.Dropdown(
#                    choices=["ocr", "format", "fine-grained-ocr", "fine-grained-format", "fine-grained-color-ocr",
#                             "fine-grained-color-format", "multi-crop-ocr", "multi-crop-format", "render"],
#                    label=local["label_ocr_mode"])
#                do_ocr = gr.Button(local["btn_do_ocr"])
#                label_result = gr.Textbox(label=local["label_result"])
#                with gr.Row():
#                    btn_save_as_pdf = gr.Button(local["btn_save_as_pdf"])
#                    save_as_pdf_info = gr.Textbox(show_label=False, interactive=False)
#    # 指南选项卡
#    with gr.Tab(local["tab_instructions"]):
#        # 从对应语言的md文件中加载指南
#        with open(os.path.join('Locales', 'gui', 'instructions', f'{lang}.md'), 'r', encoding='utf-8') as file:
#            instructions = file.read()
#        # 显示指南
#        gr.Markdown(instructions)

#    # 点击进行OCR识别
#    do_ocr.click(
#        fn=ocr,
#        inputs=[upload_img, label_fine_grained_box_x1, label_fine_grained_box_y1, label_fine_grained_box_x2,
#                label_fine_grained_box_y2, ocr_mode, label_fine_grained_color, img_name],
#        outputs=result
#    )
#    # 点击保存为pdf
#    save_as_pdf.click(
#        fn=func_save_as_pdf,
#        inputs=[html_utf8_path, html_utf8_local_path, pdf_path],
#        outputs=save_as_pdf_info
#    )
#    # 点击提交图片名
#    submit_name.click(
#        fn=func_submit_name,
#        inputs=[img_name],
#        outputs=[html_utf8_path, html_utf8_local_path, pdf_path]
#    )

## 启动gradio界面
#demo.launch()
