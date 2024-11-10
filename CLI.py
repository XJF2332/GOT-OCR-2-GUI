import json
import os

# 打开配置文件 (Load language configuration)
print("Loading language config...")
config_path = os.path.join("Locales", "cli", "config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

# 打开语言文件 (Load language file)
lang_file = os.path.join('Locales', 'cli', f'{lang}.json')
with open(lang_file, 'r', encoding='utf-8') as file:
    local = json.load(file)

# 导入transformers库 (Import required libraries)
print(local.get("info_import_libs", "Importing necessary libraries..."))
from transformers import AutoModel, AutoTokenizer
import re
import scripts.HTML2PDF as html2pdf

# 加载模型 (Load model)
print(local.get("load_models"))
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print(local.get("load_models_success"))

# 选择图片 (Function to select an image)
def select_image():
    img_folder = 'imgs'
    img_files = [f for f in os.listdir(img_folder) if
                 os.path.isfile(os.path.join(img_folder, f)) and f.lower().endswith(('.jpg', '.png'))]
    print(local.get("avaliable_imgs", "Available images:"))
    for i, file in enumerate(img_files):
        print(f"{i + 1}. {file}")
    choice = input(local.get("img_select", "Select an image (or type ---QUIT to exit): "))
    if choice == "---QUIT":
        print(local.get("img_select_quit", "Exiting..."))
        exit()
    else:
        try:
            choice = int(choice)
            if choice < 1 or choice > len(img_files):
                raise ValueError
            else:
                choice -= 1
        except (ValueError, IndexError):
            print(local.get("img_select_error", "Invalid selection. Exiting..."))
            exit()

    return os.path.join(img_folder, img_files[choice])


# 执行OCR (Function to perform OCR)
def do_ocr(image):
    if not os.path.exists("result"):
        os.makedirs("result")

    # 主菜单 (Main menu)
    print("")
    print(local.get("label_ocr_mode", "Select OCR mode:"))
    print(local.get("plaintext_ocr", "1. Plain text OCR"))
    print(local.get("format_ocr", "2. Formatted OCR"))
    print(local.get("finegrained_ocr", "3. Fine-grained OCR"))
    print(local.get("multicrop_ocr", "4. Multi-crop OCR"))
    print(local.get("render", "5. Render OCR with HTML/PDF output"))
    ocr_choice = input(local.get("ocr_mode_select", "Select an option: "))
    # 普通OCR (Perform plaintext OCR)
    if ocr_choice == '1':
        print("")
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print("")
        print(res)
        
    # 格式化OCR (Perform format OCR)
    elif ocr_choice == '2':
        print("")
        res = model.chat(tokenizer, image, ocr_type='format')
        print("")
        print(res)
    
    # Perform fine-grained OCR
    elif ocr_choice == '3':
        print("")
        fine_grained_choice = input(local.get("fine_grained_choice", "Select plain text (p) or formatted (f): "))
        # 普通
        if fine_grained_choice.lower() == 'p' or fine_grained_choice.lower() == 'f':
            fine_grained_mode = input(local.get("fine_grained_mode", "Use bounding box (b) or color (c)? "))
            # 使用框
            if fine_grained_mode.lower() == 'b':
                print("")
                box = eval(input(local.get("fine_grained_box", "Enter the bounding box coordinates: ")))
                res = model.chat(tokenizer, image, ocr_type=fine_grained_choice, ocr_box=box)
            elif fine_grained_mode.lower() == 'c':
                color = input(local.get("label_fine_grained_color", "Enter a color (e.g., red): "))
                res = model.chat(tokenizer, image, ocr_type=fine_grained_choice, ocr_color=color)
            else:
                print("")
                print(local.get("fine_grained_error", "Invalid mode. Defaulting to plain text OCR..."))
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print("")
                print(res)
    # 使用颜色 (Perform multi-crop OCR)
    elif ocr_choice == '4':
        print("")
        crop_mode = input(local.get("crop_mode", "Select plain text (p) or formatted (f): "))
        
        if crop_mode.lower() == 'p' or crop_mode.lower() == 'f':
            res = model.chat_crop(tokenizer, image, ocr_type=crop_mode)
        else:
            print("")
            print(local.get("crop_mode_error", "Invalid mode. Defaulting to plain text OCR..."))
            res = model.chat_crop(tokenizer, image, ocr_type='ocr')
        
            print("")
            print(res)
    
    # 渲染 (Render OCR)
    elif ocr_choice == '5':
        # 定义输出HTML路径 (Define the output HTML path)
        img_name = os.path.basename(image)
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = os.path.join("result", f"{img_name_no_ext}-gb2312.html")
        html_utf8_path = os.path.join("result", f"{img_name_no_ext}-utf8.html")
        html_utf8_local_path = os.path.join("result", f"{img_name_no_ext}-utf8-local.html")
        print("")
        conv = input(local.get("pdf_convert_ask", "Convert to PDF (y/n)? "))
        
        if conv.lower() == 'y':
            print("")
            print(local.get("render_mode_rendering", "Rendering OCR..."))
            model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
            print(local.get("render_mode_success", "OCR rendered successfully. HTML files: {html_gb2312_path}, {html_utf8_path}"))
            pdf_path = os.path.join("result", f"{img_name_no_ext}.pdf")
            html2pdf.all_in_one(html_gb2312_path, html_utf8_path, html_utf8_local_path, pdf_path)
            print("")
            print(local.get("pdf_convert_success", "PDF conversion successful. PDF file: {img_name_no_ext}"))
        
        elif conv.lower() == 'n':
            model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
            print(local.get("render_mode_success", "OCR rendered successfully. HTML files: {html_gb2312_path}, {html_utf8_path}"))
            
            html2pdf.convert_html_encoding(html_gb2312_path, html_utf8_path)
            html2pdf.repalce_html_content(html_utf8_path, html_utf8_local_path)
            print("")
            print(local.get("pdf_convert_refused", "PDF conversion refused. HTML files: {html_gb2312_path}, {html_utf8_path}"))
        else:
            print("")
            print(local.get("pdf_convert_error", "Invalid choice. Exiting..."))

    # 退出 (Quit)
    elif ocr_choice == '---QUIT':
        print("")
        print(local.get("ocr_mode_quit", "Exiting OCR mode..."))

    # 无效选择 (Invalid choice)
    else:
        print("")
        print(local.get("ocr_mode_error", "Invalid selection. Defaulting to plain text OCR..."))
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print(res)


# 主函数 (Main function)
def main():
    print(local.get("quit", "Type ---QUIT at any prompt to exit the program."))
    while True:
        image_file = select_image()
        do_ocr(image_file)

if __name__ == "__main__":
    main()
