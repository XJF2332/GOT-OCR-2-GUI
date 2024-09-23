# GOT-OCR-2 - GUI

## [中文版看这里](README.md)

![img_1.png](img_1.png)

## About this project

Model weights: [Mirror Site](https://hf-mirror.com/stepfun-ai/GOT-OCR2_0); [Original Site](https://huggingface.co/stepfun-ai/GOT-OCR2_0)  
Original GitHub: [GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/)  
Thank [GLM4](https://chatglm.cn/main/alltoolsdetail?lang=zh) for providing some of the code (since I am really not good at it, so I have to use AI)  
Thank [Yi-1.5](https://github.com/01-ai/Yi-1.5) for translating README.md to English  
~~The development of a command-line interface (CLI) is actually slower than that of a graphical user interface (GUI), but I'm now planning to first synchronize the changes made to the GUI with the CLI, and then update the CLI first. Once the CLI is stable, I will then update the GUI~~
CLI and GUI are now synchronized

Click a star, please

## Development process of pdf conversion
- [x] It works!
- [x] Fixed `LaTeX` rendering (on GUI-EN)
- [ ] Fixed `LaTeX` rendering (on GUI-ZH_CN)
- [x] Fixed `LaTeX` rendering (on CLI-EN)
- [x] Fixed `LaTeX` rendering (on CLI-ZH_CN)

## How to use

> If you don't have the folder mentioned here, create a new one

### Dependencies

#### Use `pip` to install
- see `requirements.txt`
```commandline
pip install -r requirements.txt
```

#### Other
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html), download `.7z` file, unzip it and put it into `wkhtmltopdf` folder
> This is for pdf outputting, but it will be removed in the future  
> The file structure should be:
> ```
> GOT-OCR-2-GUI
> ├─wkhtmltopdf
> │  ├─bin
> │  │  ├─wkhtmltopdf.exe
> │  │  ├─wkhtmltox.dll
> │  │  ├─libwkhtmltox.a
> │  │  └─wkhtmltoimage.exe
> │  └─include
> │     └─wkhtmltox
> │        └─...
> ```
- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH#downloads), download the `.zip` file, unzip it and put it into `msedgedriver` folder)
> This requires the Edge browser to be installed on your computer, which is preinstalled on Windows.  
> The file structure should be:
> ```
> GOT-OCR-2-GUI
> └─edge_driver
>    ├─msedgedriver.exe
>    └─...
> ```

### Download model file

1.  Download to `models` folder
2.  Stop downloading fewer files
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

1.  Choose a script you like to open
2.  You can ignore those using GUI, but for the CLI users, please put the images you want to OCR into the `imgs` folder (the CLI currently only detects `.jpg` and `.png` images).

## Tips
- DO NOT DELETE `markdown-it.js` inside `result` folder, or pdf outputting may fail
- If the script crashes, you can try running `cmd` with `python + file name`, I encountered crashes during testing, but I don't know why
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
- fine-grained-color-ocr: OCR content within a box of a specific color (I haven't tried this, but it seems like you would need to draw a red/green/blue box first and then select the color in the GUI)
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
