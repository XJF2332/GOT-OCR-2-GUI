# GOT-OCR-2-GUI

## [See English version here](README-en.md)

![img.png](img.png)

## 关于此项目

模型权重：[镜像站](https://hf-mirror.com/stepfun-ai/GOT-OCR2_0)，[原站点](https://huggingface.co/stepfun-ai/GOT-OCR2_0)  
原GitHub：[GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/)  
感谢[ GLM4 ](https://chatglm.cn/main/alltoolsdetail?lang=zh)提供的一部分代码（技术太菜了，所以不得不用一下 AI ）  
这个项目是在 Windows 下开发的，我本人没用过也不会 Linux，不能确保它能够在 Linux 下正常运行，如果你要在 Linux
下部署，可以参考一下这个 [issue](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/3)

点个star吧

## 最新开发进度

- [x] 初步实现 PDF 导出功能
- [x] 修复 PDF 中`LaTeX`的渲染问题
- [x] 实现用`.json`设置语言的功能
- [x] 写一个脚本来管理语言配置文件
- [x] 文件路径构建方法从格式化字符串变成`os.path.join`
- [x] 批量渲染脚本

## 使用方法

> 如果这里面提到的文件夹你没有，那就新建一个

### 依赖

#### torch
从[torch官网](https://pytorch.org/get-started/locally/)选择适合自己的**GPU版本**的torch安装即可  
我用的是 Stable 2.4.1 + cu124 ，建议你也用这个版本

#### 使用`pip`安装

```commandline
pip install -r requirements.txt
```

另，有人提到了自己使用`requirements.txt`安装依赖时出现了冲突问题，但我这里没有发现问题，`pipdeptree`
也没有显示任何冲突项，`requirements.txt`是直接`pip freeze`的我自己的虚拟环境的，按理来说应该没问题。  
但由于确实出现了这样的问题，这里再提供一个不带版本号的`requirements-noversion.txt`，你可以试试看：
更多信息请查看这个 [issue #4](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/4)

```commandline
pip install -r requirements-noversion.txt
```

#### 其他

- ~~[wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)，下载压缩包，解压放进`wkhtmltopdf`文件夹中~~

> 已经迁移到了 Edge WebDriver，此依赖项不需要再安装了

- [Edge WebDriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH#downloads)
  ，下载压缩包，放进`edge_driver`文件夹中

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

### 开始使用

1. 如果你想用命令行，那就用`CLI.py`
2. 如果你想用图形界面，那就用`GUI.py`
3. 如果你想修改语言设置，那就用`Language Config Manager.py`
4. 如果你想执行自动化的渲染操作，那就用`Renderer.py`，它会自动渲染`imgs`文件夹里所有的`.jpg`和`.png`图片

> 用 GUI 的可以不管，不过用 CLI 的各位记得把要OCR的图放进`imgs`文件夹里（ CLI 目前只检测`.jpg`和`.png`图片）

## 本地化支持

- 你可以在`Locales`文件夹中找到各种语言的`.json`文件，CLI 和 GUI 的语言文件是分开存储的
- 在`gui`子文件夹中，除了`语言.json`文件，还有一个`instructions`文件夹，里面是 GUI 的内置教程，命名为`语言.md`
- 要修改语言支持，只需要修改`config.json`中的`'language'`的值，可用的选择就是`语言.json`的不带扩展名的文件名
- 如果要添加语言支持，在 CLI 中，只需要添加新的`语言.json`（我强烈建议你使用已经存在的文件作为起点），在 GUI
  中，还需要配套的`语言.md`文件
- 你可以使用`Language Config Manager.py`来管理语言配置文件

## 注意事项

- 脚本闪退的话可以试一下用`cmd`跑`python +文件名`，我自己测试时会出现闪退的情况，我也不知道为什么
- `result`文件夹里的`markdown-it.js`不要删除，否则 pdf 导出会出错！

> 如果你不小心删除了，可以在`scripts`文件夹里找到备份，复制一份过去就行了

- 确保你安装的`torch`是 gpu 版本，因为脚本里用了`device_map='cuda'`

## 常见问题

- Q：什么是“HTML本地文件”？难道还有没保存在本地的HTML文件吗？  
- A：因为模型输出的HTML文件虽然保存在本地，但使用了外部脚本，因此即使文件在本地，还是需要网络来打开它。于是我把外部脚本下载了进来，就是前面提到的`mardown-it.js`
。这么做主要是防止网络问题造成的PDF导出失败。


- Q：为什么我的模型加载失败了？
- A：检查一下你是不是少了文件。从百度云下载的模型文件似乎缺少了文件，我建议你去前面提到的 Huggingface 下载。

- Q：有什么部署这个项目的建议吗？
- A：看这个[issue #5](https://github.com/XJF2332/GOT-OCR-2-GUI/issues/5)

## 简单的教程

> GUI 的教程已经内置到了 UI 中，直接打开 GUI 就能看到了

### **模式**

#### `OCR` 模式

- ocr: 标准OCR
- format: 带格式的OCR

#### `fine-grained` 模式

- fine-grained-ocr: 在特定框内进行OCR内容识别
- fine-grained-format: 在特定框内进行OCR内容及格式识别
- fine-grained-color-ocr: 在特定颜色的框内进行OCR内容识别（我还没尝试过，但看起来你需要先画一个红/绿/蓝框，然后在GUI中选择颜色）
- fine-grained-color-format: 在特定颜色的框内进行OCR内容及格式识别

#### `multi-crop` 模式

- 适用于更复杂的图像

#### `render` 模式

- 已存在的文件将被覆盖！！！点击按钮前请检查文件路径！！！
- 渲染OCR内容并将其保存为HTML文件
- 将保存为UTF8编码和GB2312编码文件
- 你可以将HTML转换为PDF

### **如何渲染**

1. CLI将自动获取图像名称
2. HTML文件将保存在 `result` 文件夹中
3. 如果你想将HTML转换为PDF，只需在CLI询问时输入 `y`


