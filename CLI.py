import json

print("Loading config...")

with open('Locales/cli/config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
    lang = config['language']

with open(f'Locales/cli/{lang}.json', 'r', encoding='utf-8') as file:
    local = json.load(file)

print(local["import_libs"])

import os
from transformers import AutoModel, AutoTokenizer
import re
import scripts.html2pdf as html2pdf

# Load the model and tokenizer
print(local["load_models"])
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print(local["load_models_success"])


# img selection
def select_image():
    img_folder = 'imgs'
    img_files = [f for f in os.listdir(img_folder) if
                 os.path.isfile(os.path.join(img_folder, f)) and f.lower().endswith(('.jpg', '.png'))]
    print(local["avaliable_imgs"])
    for i, file in enumerate(img_files):
        print(f"{i + 1}. {file}")
    choice = input(local["img_select"])
    if choice == "---QUIT":
        print(local["img_select_quit"])
        exit()
    else:
        choice = int(choice)
        if choice < 1 or choice > len(img_files):
            print(local["img_select_error"])
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


def repalce_html_content(input_file_path, output_file_path):
    pattern = r'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js'
    replacement = 'markdown-it.js'
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_html_content = re.sub(pattern, replacement, content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(new_html_content)


# do OCR
def do_ocr(image):
    if not os.path.exists("./result"):
        os.makedirs("./result")

    # main menu
    print("")
    print(local["ocr_mode"])
    print(local["plaintext_ocr"])
    print(local["format_ocr"])
    print(local["finegrained_ocr"])
    print(local["multicrop_ocr"])
    print(local["render"])
    ocr_choice = input(local["ocr_mode_select"])
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
        fine_grained_choice = input(local["fine_grained_choice"])
        # plain fine-grained ocr
        if fine_grained_choice.lower() == 'p':
            print("")
            fine_grained_mode = input(local["fine_grained_mode"])
            # use box
            if fine_grained_mode.lower() == 'b':
                print("")
                box = eval(input(local["fine_grained_box"]))
                print("")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
                print("")
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                print("")
                color = input(local["fine_grained_color"])
                print("")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=color)
                print("")
                print(res)
            # default to plain ocr
            else:
                print("")
                print(local["fine_grained_error"])
                print("")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print(res)
        # format fine-grained ocr
        elif fine_grained_choice.lower() == 'f':
            print("")
            fine_grained_mode = input(local["fine_grained_mode"])
            # use box
            if fine_grained_mode.lower() == 'b':
                print("")
                box = eval(input(local["fine_grained_box"]))
                print("")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
                print("")
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                print("")
                color = input(local["fine_grained_color"])
                print("")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_color=color)
                print("")
                print(res)
            # default to format ocr
            else:
                print("")
                print(local["fine_grained_error"])
                print("")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print("")
                print(res)
        # default to plain ocr
        else:
            print("")
            print(local["fine_grained_error"])
            print("")
            res = model.chat(tokenizer, image, ocr_type='ocr')
            print("")
            print(res)
    # multi-crop ocr
    elif ocr_choice == '4':
        print("")
        crop_mode = input(local["crop_mode"])
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
            print(local["crop_mode_error"])
            print("")
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
        html_utf8_local_path = f"./result/{img_name_no_ext}-utf8-local.html"
        # render ocr results
        print("")
        print(local["render_mode_rendering"])
        print("")
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        print("")
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        print("")
        # print(f"Rendered OCR results saved to {html_gb2312_path} and {html_utf8_path}")
        print(local["render_mode_success"].format(html_gb2312_path=html_gb2312_path, html_utf8_path=html_utf8_path))
        print("")
        conv = input(local["pdf_convert_ask"])
        if conv.lower() == 'y':
            repalce_html_content(html_utf8_path, html_utf8_local_path)
            html2pdf.output_pdf(html_utf8_local_path, f"./result/{img_name_no_ext}.pdf")
            print("")
            # print(f"Converted PDF saved to ./results/{img_name_no_ext}.pdf\n")
            print(local["pdf_convert_success"].format(img_name_no_ext=img_name_no_ext))
        elif conv.lower() == 'n':
            print("")
            print(local["pdf_convert_refused"])
        else:
            print("")
            print(local["pdf_convert_error"])
    # quit
    elif ocr_choice == '---QUIT':
        print("")
        print(local["ocr_mode_quit"])
    # invalid choice
    else:
        print("")
        print(local["ocr_mode_error"])
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print(res)


def main():
    print(local["quit"])
    while True:
        image_file = select_image()
        do_ocr(image_file)


if __name__ == "__main__":
    main()
