# GOT-OCR-2 - GUI

## [中文版看这里](README.md)

![img.png](img.png)

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
- [x] Fixed rendering issues with `LaTeX` in PDFs
- [x] Set the language using the `.json` files in `Locales`
- [x] Write a script to manage language configuration files
- [x] Turn file path constructing method of CLI into `os.path.join` instead of formatted string
- [ ] Turn file path constructing method of GUI into `os.path.join` instead of formatted string

## How to use

> If you don't have the folder mentioned here, create a new one

### Dependencies

#### Use `pip` to install
```commandline
pip install -r requirements.txt
```
And, someone said that he encountered conflicting dependencies after installing. But I didn't find any conflicting dependencies in the `requirements.txt` file, and `pipdeptree` shows that nothing is conflicting. I used `pip freeze` to create this `requirements.txt` file, so it should be fine.  
However, this problem really happened, so I provided a `requirements-noversion.txt` that doesn't contain version numbers.
For more information, see this [issue #4](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/4)
```commandline
pip install -r requirements-noversion.txt
```

#### Other

- ~~[wkhtmltopdf](https://wkhtmltopdf.org/downloads.html), download `.7z` file, unzip it and put it into `wkhtmltopdf`
  folder~~

> Switched to Edge WebDriver, so you don't need to install this anymore

- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH#downloads),
  download the `.zip` file, unzip it and put it into `msedgedriver` folder)

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
├─models
│  ├─model.safetensors
│  ├─config.json
│  └─other files you downloaded from huggingface
└─...
```

### Start Using

1. Choose a script you like to open
2. You can ignore those using GUI, but for the CLI users, please put the images you want to OCR into the `imgs` folder (
   the CLI currently only detects `.jpg` and `.png` images).

## Localization Support

- You can find various language `.json` files in the `Locales` folder, with CLI and GUI language files stored
  separately.
- In the `gui` subfolder, in addition to the `language.json` file, there is also an `instructions` folder that contains
  the built-in tutorials for the GUI, named as `language.md`.
- To modify language support, simply change the value of `'language'` in the `config.json` file. The available options
  correspond to the file names without extensions in the `language.json` files.
- If you wish to add language support, for the CLI, just add a new `language.json` file (I strongly recommend using an
  existing file as a starting point). For the GUI, you will also need the corresponding `language.md` file.
- You can run `language-config-manager.py` to manage the language configuration files.

## Tips

- DO NOT DELETE `markdown-it.js` inside `result` folder, or pdf outputting may fail

> If you deleted it, you can find a backup in `scripts` folder. Just copy it to `result` folder.

- If the script crashes, you can try running `cmd` with `python + file name`, I encountered crashes during testing, but
  I don't know why
- Make sure hat you installed the gpu version of `torch`

## Simple Tutorial

> For GUI users, the tutorial is in the GUI, you can just open the GUI and follow the instructions

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

1. CLI will automaticlly get image name
2. HTML files will be saved in `result` folder
3. If you want to convert HTML to PDF, just enter `y` when the CLI ask you
