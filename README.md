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
- [x] 现在已经可以用`Locales`中的`.json`文件来给 CLI 设置语言了
- [x] 在 GUI 中实现用`.json`设置语言的功能
- [x] 写一个脚本来管理 CLI 和 GUI 的语言配置文件

## 使用方法

> 如果这里面提到的文件夹你没有，那就新建一个

### 依赖

#### 使用`pip`安装

- 参考`requirements.txt`

```commandline
pip install -r requirements.txt
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
├─models
│  ├─model.safetensors
│  ├─config.json
│  └─你在huggingface下载的其他文件
└─...
```

### 开始使用

1. 选一个你喜欢的脚本打开
2. 用 GUI 的可以不管，不过用 CLI 的各位记得把要OCR的图放进`imgs`文件夹里（ CLI 目前只检测`.jpg`和`.png`图片）

## 本地化支持

- 你可以在`Locales`文件夹中找到各种语言的`.json`文件，CLI 和 GUI 的语言文件是分开存储的
- 在`gui`子文件夹中，除了`语言.json`文件，还有一个`instructions`文件夹，里面是 GUI 的内置教程，命名为`语言.md`
- 要修改语言支持，只需要修改`config.json`中的`'language'`的值，可用的选择就是`语言.json`的不带扩展名的文件名
- 如果要添加语言支持，在 CLI 中，只需要添加新的`语言.json`（我强烈建议你使用已经存在的文件作为起点），在 GUI
  中，还需要配套的`语言.md`文件
- 你可以使用`language-config-manager.py`来管理语言配置文件

## 注意事项

- 脚本闪退的话可以试一下用`cmd`跑`python +文件名`，我自己测试时会出现闪退的情况，我也不知道为什么
- `result`文件夹里的`markdown-it.js`不要删除，否则 pdf 导出会出错！

> 如果你不小心删除了，可以在`scripts`文件夹里找到备份，复制一份过去就行了

- 确保你安装的`torch`是 gpu 版本

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


