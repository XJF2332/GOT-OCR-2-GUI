# GOT-OCR-2-GUI
## [See English version here](README-en.md)

![img.png](img.png)
## 关于此项目

模型权重：[镜像站](https://hf-mirror.com/stepfun-ai/GOT-OCR2_0)；[原站点](https://huggingface.co/stepfun-ai/GOT-OCR2_0)  
原GitHub：[GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/)  
感谢[ GLM4 ](https://chatglm.cn/main/alltoolsdetail?lang=zh)提供的一部分代码（技术太菜了，所以不得不用一下 AI ）  
~~其实 CLI 的开发比 GUI 还要慢，不过我现在打算先把 GUI 的改动同步到 CLI ，然后先更新 CLI ，等 CLI 稳定后再更新 GUI~~
CLI 和 GUI 的进度已经同步

点个star吧

## 转换为 pdf 的开发进度
- [x] 初步实现功能
- [x] 修复`LaTeX`的渲染问题（位于`GUI-EN`版本中）
- [ ] 修复`LaTeX`的渲染问题（位于`GUI-ZH_CN`版本中）
- [x] 修复`LaTeX`的渲染问题（位于`CLI-EN`版本中）
- [x] 修复`LaTeX`的渲染问题（位于`CLI-ZH_CN`版本中）

## 使用方法
> 如果这里面提到的文件夹你没有，那就新建一个
### 依赖
#### 使用`pip`安装
- 参考`requirements.txt`
```commandline
pip install -r requirements.txt
```
#### 其他
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)，下载压缩包，解压放进`wkhtmltopdf`文件夹中
> 这个是转 pdf 用的，不过在将来应该会弃用；  
> 文件结构应该是：
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
- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH#downloads)，下载压缩包，放进`edge_driver`文件夹中
> 这个是转 pdf 用的，但还在开发；  
> 大伙的电脑里应该都有 edge 吧？应该吧？这玩意可是预装的来着......  
> 文件结构应该是：
> ```
> GOT-OCR-2-GUI
> └─edge_driver
>    ├─msedgedriver.exe
>    └─...
> ```

### 下载模型文件
1. 下载到`models`文件夹中
2. 别少下载文件了
- 文件结构应该是：
```
GOT-OCR-2-GUI
├─models
│  ├─model.safetensors
│  ├─config.json
│  └─你在huggingface下载的其他文件
└─...
```
### 开始使用
1. 选一个你喜欢的脚本打开
2. 用 GUI 的可以不管，不过用 CLI 的各位记得把要OCR的图放进`imgs`文件夹里（ CLI 目前只检测`.jpg`和`.png`图片）

## 注意事项
- 脚本闪退的话可以试一下用`cmd`跑`python +文件名`，我自己测试时会出现闪退的情况，我也不知道为什么
- `result`文件夹里的`markdown-it.js`不要删除，否则 pdf 导出会出错！
- 确保你安装的`torch`是 gpu 版本

## 简单的教程
> GUI 的教程已经内置到了 UI 中，直接打开 GUI 就能看到了  
> 由于中文版 GUI 的功能暂不完善，这里只提供英文版教程

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

