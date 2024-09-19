import os
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('models', trust_remote_code=True)
model = AutoModel.from_pretrained('models', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda',
                                  use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()


def select_image():
    img_folder = 'imgs'
    img_files = [f for f in os.listdir(img_folder) if
                 os.path.isfile(os.path.join(img_folder, f)) and f.lower().endswith(('.jpg', '.png'))]
    print("Available images:")
    for i, file in enumerate(img_files):
        print(f"{i + 1}. {file}")
    choice = int(input("\nSelect an image by number: ")) - 1
    return os.path.join(img_folder, img_files[choice])


def get_ocr_type():
    print("-" * 10)
    print("Choose OCR type:")
    print("1. Plain OCR")
    print("2. Format OCR")
    print("3. Fine-grained OCR")
    print("4. Multi-crop OCR\n")
    ocr_choice = input("Enter your choice (1-4) or ---QUIT to exit: ")
    if ocr_choice == '1':
        return 'ocr'
    elif ocr_choice == '2':
        return 'format'
    elif ocr_choice == '3':
        return 'fine-grained'
    elif ocr_choice == '4':
        return 'multi-crop'
    elif ocr_choice == '---QUIT':
        return '---QUIT'
    else:
        print("Invalid choice. Defaulting to plain OCR.")
        return 'ocr'


def get_additional_params(ocr_type):
    if ocr_type == 'fine-grained':
        ocr_box = input("Enter OCR box coordinates [x1,y1,x2,y2] or leave blank for full image: ")
        ocr_color = input("Enter color to filter by (e.g., 'red') or leave blank for no filter: ")
        return ocr_box, ocr_color
    return None, None


def perform_ocr(model, tokenizer, image_file, ocr_type, ocr_box=None, ocr_color=None):
    if ocr_type == 'ocr' or ocr_type == 'format':
        res = model.chat(tokenizer, image_file, ocr_type=ocr_type)
    elif ocr_type == 'fine-grained':
        res = model.chat(tokenizer, image_file, ocr_type=ocr_type, ocr_box=ocr_box, ocr_color=ocr_color)
    elif ocr_type == 'multi-crop':
        res = model.chat_crop(tokenizer, image_file, ocr_type='ocr')
    return res


def main():
    while True:
        print("\nEnter ---QUIT at any time to exit the program.")
        image_file = select_image()
        ocr_type = get_ocr_type()
        if ocr_type == '---QUIT':
            print("Exiting the program.")
            break
        ocr_box, ocr_color = get_additional_params(ocr_type)
        res = perform_ocr(model, tokenizer, image_file, ocr_type, ocr_box, ocr_color)
        print(res)
        print("\nRender OCR Result?(y/n)")
        if input().lower() == 'y':
            render = model.chat(tokenizer, image_file, ocr_type='format', render=True,
                                save_render_file=f'./{image_file}.html')
            print(f"Rendered OCR Result saved to ./{image_file}.html")


if __name__ == "__main__":
    main()
