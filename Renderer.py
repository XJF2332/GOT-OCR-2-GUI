import json
import os
import glob

# 打开语言配置文件
print("Loading language config...")
lang_config_path = os.path.join("Locales", "cli", "config.json")
with open(lang_config_path, 'r', encoding='utf-8') as file:
    lang_config = json.load(file)
    lang = lang_config['language']

# 打开语言文件
lang_file = os.path.join('Locales', 'cli', f'{lang}.json')
with open(lang_file, 'r', encoding='utf-8') as file:
    local = json.load(file)

# 打开配置文件
print("Loading config......")
config_path = os.path.join("Configs", "Config.json")
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 导入transformers库
print(local["import_libs"])
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
if pdf_convert == "y":
    convert_confirm = True
else:
    convert_confirm = False

# 读取imgs文件夹下的jpg和png图片
imgs_path = os.path.join(os.getcwd(), 'imgs')
image_files = glob.glob(os.path.join(imgs_path, '*.jpg')) + glob.glob(os.path.join(imgs_path, '*.png'))

# 逐个发送图片给renderer的render函数
for image_path in image_files:
    success = Render.render(model=model, tokenizer=tokenizer, image_path=image_path, convert_to_pdf=convert_confirm,
                            wait=config["pdf_render_wait"], time=config["pdf_render_wait_time"])
    if success:
        print(local["renderer_success"].format(img_path=image_path))
    else:
        print(local["renderer_fail"].format(img_path=image_path))
