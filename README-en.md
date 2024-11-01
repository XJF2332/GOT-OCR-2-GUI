# GOT-OCR-2 - GUI

## [中文版看这里](README.md)

![img.png](img.png)

**⚠️Development of CLI has been paused. I will make it able to receive params from command line so that it will be more
suitable for automatic jobs after I finished the development of GUI.⚠️**

## About this project

Model
weights: [Mirror Site](https://hf-mirror.com/stepfun-ai/GOT-OCR2_0), [Original Site](https://huggingface.co/stepfun-ai/GOT-OCR2_0)  
Original GitHub: [GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/)  
Thank [GLM4](https://chatglm.cn/main/alltoolsdetail?lang=zh) for providing some of the code (since I am really not good
at it, so I have to use AI)  
Thank [Yi-1.5](https://github.com/01-ai/Yi-1.5) for translating README.md to English  
This project was developed under Windows, so I can't guarantee that it will work on Linux. If you want to use it on
Linux, you can check this [issue](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/3)

Click a star, please

## Latest Development Progress

- [x] Preliminary implementation of PDF export feature
- [x] Fixed LaTeX rendering issues in PDF
- [x] Implemented functionality to set language using `.json`
- [x] Wrote a script to manage language configuration files
- [x] Batch rendering script
- [x] PDF processing, split into individual page pngs first, then batch render to generate pdf for each page
- [x] Integrated the batch renderer into the GUI
- [x] More configuration options
- [x] Refactored the PDF processing script
- [x] Pulled an `Alpha` branch, put unfinished tasks into this
- [x] PDF processing should be able to render a whole PDF, not one PDF per page
- [ ] Support for `llama-cpp-python`, hoping to accelerate inference
- [ ] html to word functionality, preserve formulas for editing

## How to use

If you don't have the folder mentioned here, **create a new one**

### Dependencies

This environment was tested under **python 3.11.9**.

#### torch

Choose a suitable **GPU version** of `torch` and from [PyTorch](https://pytorch.org/get-started/locally/) and install
it.  
I am using stable 2.4.1 + cu124, so I suggest you to use this version.

#### FlashAttention
Not a must-have, but if you want to install it, check [#12](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/12)

#### PyMuPDF

I have tested that if you install it directly through `requiremtns.txt`, then you will get
`ModuleNotFoundError: No module named 'frontend'` error. But if you install it separately in commandline, it will work
fine. I don't know the reason why, just try it yourself.
By the way, if you still get the `ModuleNotFoundError`, try to uninstall and reinstall `fitz` and `PyMuPDF` separately.
I have tested that `pip install -U` won't work. Strange.

```commandline
pip install fitz
pip install PyMuPDF
```

#### Use `pip` to install

```commandline
pip install -r requirements.txt
```

And, someone said that he encountered conflicting dependencies after installing. But I didn't find any conflicting
dependencies in the `requirements.txt` file, and `pipdeptree` shows that nothing is conflicting. I used `pip freeze` to
create this `requirements.txt` file, so it should be fine.  
However, this problem really happened, so I provided a `requirements-noversion.txt` that doesn't contain version
numbers.
For more information, see this [issue #4](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/4)

```commandline
pip install -r requirements-noversion.txt
```

#### Other

- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH#downloads),
  download the `.zip` file, unzip it and put it into `msedgedriver` folder

> This requires the Edge browser to be installed on your computer, which is preinstalled on Windows.  
> The file structure should be:
> ```
> GOT-OCR-2-GUI
> └─edge_driver
>    ├─msedgedriver.exe
>    └─...
> ```

### Download model file

1. Download to `models` folder
2. Stop downloading fewer files

- The file structure should be:

```
GOT-OCR-2-GUI
└─models
   ├─config.json
   ├─generation_config.json
   ├─got_vision_b.py
   ├─model.safetensors
   ├─modeling_GOT.py
   ├─qwen.tiktoken
   ├─render_tools.py
   ├─special_tokens_map.json
   ├─tokenization_qwen.py
   └─tokenizer_config.json
```

### Getting Started

1. If you want to use the command line, then use `CLI.py`.
2. If you want to use the graphical interface, then use `GUI.py`.
3. If you want to modify settings, then use `Config Manager.py`.
4. If you want to perform automated rendering operations, then use `Renderer.py`, which will automatically render all
   `.jpg` and `.png` images in the `imgs` folder.

> Those using the GUI can ignore this, but for those using the CLI, remember to place the images you want to OCR into
> the `imgs` folder (the CLI currently only detects `.jpg` and `.png` files).

## Localization Support

- You can find various language `.json` files in the `Locales` folder, with CLI and GUI language files stored
  separately.
- In the `gui` subfolder, in addition to the `language.json` file, there is also an `instructions` folder that contains
  the built-in tutorials for the GUI, named as `language.md`.
- To modify language support, simply change the value of `'language'` in the `config.json` file. The available options
  correspond to the file names without extensions in the `language.json` files.
- If you wish to add language support, for the CLI, just add a new `language.json` file (I strongly recommend using an
  existing file as a starting point). For the GUI, you will also need the corresponding `language.md` file.
- You can run `Config Manager.py` to manage the language and other configuration files.

## Tips

- DO NOT DELETE `markdown-it.js` inside `result` folder, or pdf outputting may fail

> If you deleted it, you can find a backup in `scripts` folder. Just copy it to `result` folder.

- If the script crashes, you can try running `cmd` with `python + file name`, I encountered crashes during testing, but
  I don't know why
- Make sure hat you installed the gpu version of `torch`

## Common Questions

- Q: What is an "HTML local file"? Are there HTML files that are not saved locally?
- A: Although the HTML files output by the model are saved locally, they use external scripts. Therefore, even if the
  file is on your local machine, you still need an internet connection to open it. I have downloaded the external
  script, which is the previously mentioned `markdown-it.js`. The main reason for doing this is to prevent PDF export
  failures due to network issues.


- Q: Why did my model fail to load?
- A: Check if you are missing any files. It seems that the model files downloaded from Baidu Cloud are missing some
  files. I recommend you download from the previously mentioned Huggingface instead.

- Q：Any suggestions on deploying this repo?
- A: See this [issue #5](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/5)

## Simple Tutorial

For GUI users, the tutorial is in the GUI, you can **just open the GUI** and follow the instructions.   
Here are tutorials for CLI users.

### **Modes**

#### `OCR` Modes

- ocr: Standard OCR
- format: OCR with formatting

#### `Fine-Grained` Modes

- fine-grained-ocr: OCR content within a specific box
- fine-grained-format: OCR and format content within a specific box
- fine-grained-color-ocr: OCR content within a box of a specific color (I haven't tried this, but it seems like you
  would need to draw a red/green/blue box first and then select the color in the GUI)
- fine-grained-color-format: OCR and format content within a box of a specific color

#### `Multi-Crop` Modes

- Suitable for more complex images

#### `Render` Modes

- Exist files will be overwritten!!!Check the file path before clicking the button!!!
- Render OCR content and save it as an HTML file
- Will be saved as UTF8 encoding and GB2312 encoding files
- You can convert HTML to PDF

### **How to render**

1. CLI will automatically get image name
2. HTML files will be saved in `result` folder
3. If you want to convert HTML to PDF, just enter `y` when the CLI ask you

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=XJF2332/GOT-OCR-2-GUI&type=Date)](https://star-history.com/#XJF2332/GOT-OCR-2-GUI&Date)