## 使用说明
### **模式**
#### `OCR` 模式
- ocr: 标准OCR
- format: 带格式化的OCR
#### `fine-grained` 模式
- fine-grained-ocr: 在特定框内进行OCR内容识别
- fine-grained-format: 在特定框内进行OCR内容识别并格式化
- fine-grained-color-ocr: 在特定颜色的框内进行OCR内容识别（我还没尝试过这个，但看起来你需要先画一个红/绿/蓝色的框，然后在GUI中选择颜色）
- fine-grained-color-format: 在特定颜色的框内进行OCR内容识别并格式化
#### `multi-crop` 模式
- 适用于更复杂的图像
#### `render` 模式
- 已存在的文件将被覆盖！！！点击按钮前请检查文件路径！！！
- 渲染OCR内容并将其保存为HTML文件
- 将保存为UTF8编码和GB2312编码的文件
- 你可以将HTML转换为PDF
### **如何渲染**
1. 在文本框中输入图像名称，这将变成输出文件的基本名称
2. 你会发现下面的三个文本框发生了变化，这意味着名称已被应用
3. 点击“保存为PDF”按钮以将HTML文件保存为PDF文件
