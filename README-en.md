# GOT-OCR-2 - GUI

## [中文版看这里](README.md)

![img.png](img.png)

## About this project

Model weights: [https://hf-mirror.com/stepfun-ai/GOT-OCR2\_0](https://hf-mirror.com/stepfun-ai/GOT-OCR2_0)  
Original GitHub: [https://github.com/Ucas-HaoranWei/GOT-OCR2.0/](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/)  
Thank GLM4 for providing some of the code (since I am really not good at it, so I have to use AI)  
Thank Yi-1.5-9B for translating README.md to English  
The development of a command-line interface (CLI) is actually slower than that of a graphical user interface (GUI), but I'm now planning to first synchronize the changes made to the GUI with the CLI, and then update the CLI first. Once the CLI is stable, I will then update the GUI

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

