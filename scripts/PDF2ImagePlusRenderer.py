import fitz
import json
import os
import glob

from pathlib import Path


def main():
    print("Loading config......")
    config_path = os.path.join("Configs", "Config.json")
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)


    def remove_suffix(file_name):
        return Path(file_name).stem


    file_list = []  # 新建一个空列表用于存放文件全路径
    file_dir = r'pdf'  # 指定即将遍历的文件夹路径
    for files in os.walk(file_dir):  # 遍历指定文件夹及其下的所有子文件夹
        for file in files[2]:  # 遍历每个文件夹里的所有文件，（files[2]:母文件夹和子文件夹下的所有文件信息，files[1]:子文件夹信息，files[0]:母文件夹信息）
            if os.path.splitext(file)[1] == '.PDF' or os.path.splitext(file)[1] == '.pdf':  # 检查文件后缀名,逻辑判断用==
                # file_list.append(file)#筛选后的文件名为字符串，将得到的文件名放进去列表，方便以后调用
                file_list.append(file_dir + file)  # 给文件名加入文件夹路径

    print(file_list)

    # 加载 pdf 文件
    doc = fitz.open(file_list[0])


    def covert2pic(file_path, zoom, png_path):
        doc = fitz.open(file_path)
        file_name = remove_suffix(file_path)
        total = doc.page_count
        for pg in range(total):
            page = doc[pg]
            zoom = int(zoom)  # 值越大，分辨率越高，文件越清晰
            rotate = int(0)

            trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).prerotate(rotate)
            pm = page.get_pixmap(matrix=trans, alpha=False)
            if not os.path.exists(png_path):
                os.mkdir(png_path)
            save = os.path.join(png_path, file_name + '{}.png'.format(pg + 1))
            pm.save(save)
        doc.close()


    pdfPath = file_list[0]
    imagePath = 'imgs'
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
    allres = ''
    for image_path in image_files:
        success = Render.render(model=model, tokenizer=tokenizer, image_path=image_path, convert_to_pdf=convert_confirm,
                                wait=config["pdf_render_wait"], time=config["pdf_render_wait_time"])
        if success:
            print(local["renderer_success"].format(img_path=image_path))
        else:
            print(local["renderer_fail"].format(img_path=image_path))

if __name__ == '__main__':
    main()