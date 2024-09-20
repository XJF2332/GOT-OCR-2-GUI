import os
from transformers import AutoModel, AutoTokenizer
import pdfkit
from bs4 import BeautifulSoup
import re

# Load the model and tokenizer
print("正在加载模型...")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print("模型加载成功")


# img selection
def select_image():
    img_folder = 'imgs'
    img_files = [f for f in os.listdir(img_folder) if
                 os.path.isfile(os.path.join(img_folder, f)) and f.lower().endswith(('.jpg', '.png'))]
    print("检测到的图像：")
    for i, file in enumerate(img_files):
        print(f"{i + 1}. {file}")
    choice = input("输入序号选择图像：")
    if choice == "---QUIT":
        print("正在退出...")
        exit()
    else:
        choice = int(choice)
        if choice < 1 or choice > len(img_files):
            print("选择无效")
            exit()
        else:
            choice = choice - 1

    return os.path.join(img_folder, img_files[choice])


# convert html encoding
def convert_html_encoding(input_file_path, output_file_path):
    # gb2312
    with open(input_file_path, 'r', encoding='gb2312') as file:
        content = file.read()

    # utf8
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# do OCR
def do_ocr(image):
    if not os.path.exists("./result"):
        os.makedirs("./result")

    # main menu
    print("-" * 10)
    print("选择OCR模式：")
    print("1. 普通OCR")
    print("2. 格式化OCR")
    print("3. 框选OCR")
    print("4. Multi-crop OCR")
    print("5. 渲染为HTML")
    ocr_choice = input("输入序号(1-5)或“---QUIT”来退出：")
    # plain ocr
    if ocr_choice == '1':
        print("")
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print("")
        print(res)
    # format ocr
    elif ocr_choice == '2':
        print("")
        res = model.chat(tokenizer, image, ocr_type='format')
        print("")
        print(res)
    # fine-grained ocr
    elif ocr_choice == '3':
        print("")
        fine_grained_choice = input("普通（P）还是格式化（F）OCR：")
        # plain fine-grained ocr
        if fine_grained_choice.lower() == 'p':
            print("")
            fine_grained_mode = input("框选（B）还是颜色（C）：")
            # use box
            if fine_grained_mode.lower() == 'b':
                print("")
                box = input("输入框的坐标[x1,y1,x2,y2]：")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
                print("")
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                print("")
                color = input("输入颜色（red/blue/green）：")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=color)
                print("")
                print(res)
            # default to plain ocr
            else:
                print("")
                print("无效选择，使用默认值（普通OCR）")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print("")
                print(res)
        # format fine-grained ocr
        elif fine_grained_choice.lower() == 'f':
            print("")
            fine_grained_mode = input("框选（B）还是颜色（C）：")
            # use box
            if fine_grained_mode.lower() == 'b':
                print("")
                box = input("输入框的坐标[x1,y1,x2,y2]：")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
                print("")
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                print("")
                color = input("输入颜色（red/blue/green）：")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_color=color)
                print("")
                print(res)
            # default to format ocr
            else:
                print("")
                print("无效选择，使用默认值（普通OCR）")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print("")
                print(res)
        # default to plain ocr
        else:
            print("")
            print("无效选择，使用默认值（普通OCR）")
            res = model.chat(tokenizer, image, ocr_type='ocr')
            print("")
            print(res)
    # multi-crop ocr
    elif ocr_choice == '4':
        print("")
        crop_mode = input("普通（P）还是格式化（F）OCR：")
        # plain multi-crop ocr
        if crop_mode.lower() == 'p':
            print("")
            res = model.chat_crop(tokenizer, image, ocr_type='ocr')
            print("")
            print(res)
        # format multi-crop ocr
        elif crop_mode.lower() == 'f':
            print("")
            res = model.chat_crop(tokenizer, image, ocr_type='format')
            print("")
            print(res)
        # default to plain ocr
        else:
            print("")
            print("无效选择，使用默认值（普通OCR）")
            res = model.chat_crop(tokenizer, image, ocr_type='ocr')
            print("")
            print(res)
    # render
    elif ocr_choice == '5':
        # define output html path
        img_name = os.path.basename(image)
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = f"./result/{img_name_no_ext}-gb2312.html"
        html_utf8_path = f"./result/{img_name_no_ext}-utf8.html"
        # render ocr results
        print("")
        print("正在渲染结果...")
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        print(f"渲染结果已保存为 {html_gb2312_path} 和 {html_utf8_path}")
    elif ocr_choice == '---QUIT':
        print("")
        print("正在退出...")
    else:
        print("")
        print("无效选择，使用默认值（普通OCR）")
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print("")
        print(res)
    print("")


def main():
    while True:
        print("\n输入“---QUIT”来退出程序\n")
        while True:
            image_file = select_image()
            do_ocr(image_file)


if __name__ == "__main__":
    main()
