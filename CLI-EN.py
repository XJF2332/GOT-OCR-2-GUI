import os
from transformers import AutoModel, AutoTokenizer
import pdfkit
from bs4 import BeautifulSoup
import re

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
    elif ocr_choice == '---QUIT':
        print("Exiting program...")
    else:
        print("Invalid choice. Defaulting to plain OCR.")
        res = model.chat(tokenizer, image, ocr_type='ocr')
        print(res)


def main():
    while True:
        print("\nEnter ---QUIT at any time to exit the program.")
        while True:
            image_file = select_image()
            do_ocr(image_file)
            Continue = input("Continue? (y/n): ")
            if Continue.lower() == 'n':
                break
            elif Continue.lower() == 'y':
                continue
            else:
                print("Invalid choice, stopping.")
                break


if __name__ == "__main__":
    main()
