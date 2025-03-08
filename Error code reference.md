# 错误码自查表 / Error codes reference book

## scripts\Renderer.py

| 错误码 / Error code | 错误 / Error                                                                          |
|------------------|-------------------------------------------------------------------------------------|
| 2                | 未加载模型或未上传图片 / No model loaded or no image uploaded                                  |
| 3                | 未知错误 / Unknown error                                                                |
| 4                | 替换 HTML 内容时未找到 utf8_path / utf8_path not found while replacing contents of the HTML |
| 5                | HTML 内容替换失败 / Failed to replace HTML content                                        |
| 6                | HTML 编码检测失败 / Failed to detect HTML encoding                                        |
| 7                | 转换 HTML 编码时遇到了未知错误 / Unknown error occurred while converting HTML encoding          |
| 8                | 替换 HTML 内容时遇到了未知错误 / Unknown error occurred while replacing HTML content            |
| 9                | 未找到 WebDriver / WebDriver not found                                                 |
| 10               | 生成 PDF 时遇到了未知错误 / Unknown error occurred while generating PDF                       |

## scripts\HTMP2PDF.py

### conv_html_enc()

| 错误码 / Error code | 错误 / Error                                  |
|------------------|---------------------------------------------|
| 1                | HTML编码检测失败 / Failed to detect HTML encoding |
| 2                | 未知错误 / Unknown error                        |

### replace_content()

| 错误码 / Error code | 错误 / Error           |
|------------------|----------------------|
| 1                | 未知错误 / Unknown Error |

### output_pdf()

| 错误码 / Error code | 错误 / Error                          |
|------------------|-------------------------------------|
| 1                | 未找到 WebDriver / WebDriver not found |
| 2                | 未知错误 / Unknown Error                |