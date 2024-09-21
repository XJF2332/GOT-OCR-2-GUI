import os
from transformers import AutoModel, AutoTokenizer
import pdfkit
from bs4 import BeautifulSoup
import re

config = pdfkit.configuration(wkhtmltopdf='./wkhtmltopdf/bin/wkhtmltopdf.exe')

# Load the model and tokenizer
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()
print("Model loaded successfully.")


# img selection
def select_image():
    img_folder = 'imgs'
    img_files = [f for f in os.listdir(img_folder) if
                 os.path.isfile(os.path.join(img_folder, f)) and f.lower().endswith(('.jpg', '.png'))]
    print("Available images:")
    for i, file in enumerate(img_files):
        print(f"{i + 1}. {file}")
    choice = input("\nSelect an image by number: ")
    if choice == "---QUIT":
        print("Exiting...")
        exit()
    else:
        choice = int(choice)
        if choice < 1 or choice > len(img_files):
            print("Invalid choice. Exiting...")
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

def extract_style_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    style_tag = soup.find('style')
    return style_tag.string if style_tag else ''


def extract_const_text_from_script(script_content):
    # 使用正则表达式来匹配所有被双引号包围的字符串，并保留换行符
    string_pattern = r'(?<!\\)"(.*?)(?<!\\)"'
    matches = re.findall(string_pattern, script_content, re.DOTALL)
    # 将所有匹配的字符串连接起来，并替换掉转义引号
    const_text = ''.join(matches).replace('\\"', '"')
    # 替换JavaScript的换行符为HTML的换行符
    const_text = const_text.replace('\\n', '<br>')
    return const_text


def const_text_to_pdf(input_html_path, output_pdf_path):
    try:
        with open(input_html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 提取<style>标签内容
        style_content = extract_style_from_html(html_content)

        # 提取<script>标签内容
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script')
        script_content = script_tag.string if script_tag else ''

        # 提取const text内容
        const_text = extract_const_text_from_script(script_content)

        # 构建完整的HTML文档，包含提取的<style>标签和const text内容
        styled_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {style_content}
            </style>
        </head>
        <body>
            <pre>{const_text}</pre>
        </body>
        </html>
        """

        if not os.path.exists("./result"):
            os.makedirs("./result")

        # 将const text内容转换为PDF
        pdfkit.from_string(styled_text, output_pdf_path, configuration=config)
        return f"转换完成，PDF文件已保存为：{output_pdf_path}"
    except Exception as e:
        return f"转换失败：{e}"


# do OCR
def do_ocr(image):
    if not os.path.exists("./result"):
        os.makedirs("./result")

    # main menu
    print("-" * 10)
    print("Choose OCR type:")
    print("1. Plain OCR")
    print("2. Format OCR")
    print("3. Fine-grained OCR")
    print("4. Multi-crop OCR")
    print("5. Render\n")
    ocr_choice = input("Enter your choice (1-5) or ---QUIT to exit: ")
    # plain ocr
    if ocr_choice == '1':
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print(res)
    # format ocr
    elif ocr_choice == '2':
        res = model.chat(tokenizer, image, ocr_type='format')
        print(res)
    # fine-grained ocr
    elif ocr_choice == '3':
        fine_grained_choice = input("Plain(P) or Format(F) OCR: ")
        # plain fine-grained ocr
        if fine_grained_choice.lower() == 'p':
            fine_grained_mode = input("Use Box(B) or Color(C): ")
            # use box
            if fine_grained_mode.lower() == 'b':
                box = input("Enter OCR box coordinates [x1,y1,x2,y2]: ")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_box=box)
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                color = input("Enter color (red/blue/green): ")
                res = model.chat(tokenizer, image, ocr_type='ocr', ocr_color=color)
                print(res)
            # default to plain ocr
            else:
                print("Invalid choice. Defaulting to plain OCR.")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print(res)
        # format fine-grained ocr
        elif fine_grained_choice.lower() == 'f':
            fine_grained_mode = input("Use Box(B) or Color(C): ")
            # use box
            if fine_grained_mode.lower() == 'b':
                box = input("Enter OCR box coordinates [x1,y1,x2,y2]: ")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_box=box)
                print(res)
            # use color
            elif fine_grained_mode.lower() == 'c':
                color = input("Enter color (red/blue/green): ")
                res = model.chat(tokenizer, image, ocr_type='format', ocr_color=color)
                print(res)
            # default to format ocr
            else:
                print("Invalid choice. Defaulting to plain OCR.")
                res = model.chat(tokenizer, image, ocr_type='ocr')
                print(res)
        # default to plain ocr
        else:
            print("Invalid choice. Defaulting to plain OCR.")
            res = model.chat(tokenizer, image, ocr_type='ocr')
            print(res)
    # multi-crop ocr
    elif ocr_choice == '4':
        crop_mode = input("Plain(P) or Format(F) OCR: ")
        # plain multi-crop ocr
        if crop_mode.lower() == 'p':
            res = model.chat_crop(tokenizer, image, ocr_type='ocr')
            print(res)
        # format multi-crop ocr
        elif crop_mode.lower() == 'f':
            res = model.chat_crop(tokenizer, image, ocr_type='format')
            print(res)
        # default to plain ocr
        else:
            print("Invalid choice. Defaulting to plain OCR.")
            res = model.chat_crop(tokenizer, image, ocr_type='ocr')
            print(res)
    # render
    elif ocr_choice == '5':
        # define output html path
        img_name = os.path.basename(image)
        img_name_no_ext = os.path.splitext(img_name)[0]
        html_gb2312_path = f"./result/{img_name_no_ext}-gb2312.html"
        html_utf8_path = f"./result/{img_name_no_ext}-utf8.html"
        # render ocr results
        print("Rendering OCR results...")
        model.chat(tokenizer, image, ocr_type='format', render=True, save_render_file=html_gb2312_path)
        convert_html_encoding(html_gb2312_path, html_utf8_path)
        print(f"Rendered OCR results saved to {html_gb2312_path} and {html_utf8_path}")
        print("-"*10)
        conv = input("Convert HTML to PDF?(y/n): ")
        if conv.lower() == 'y':
            const_text_to_pdf(html_utf8_path, f"./result/{img_name_no_ext}.pdf")
            print(f"Converted PDF saved to {img_name_no_ext}.pdf")
        elif conv.lower() == 'n':
            print("Exiting program...")
        else:
            print("Invalid choice. Exiting program...")
    # quit
    elif ocr_choice == '---QUIT':
        print("Exiting program...")
    # invalid choice
    else:
        print("Invalid choice. Defaulting to plain OCR.")
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print(res)


def main():
    print("\nEnter ---QUIT at any time to exit the program.")
    while True:
        image_file = select_image()
        do_ocr(image_file)


if __name__ == "__main__":
    main()
