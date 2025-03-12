# 错误码自查表 / Error codes reference book

## scripts\Renderer.py

| 错误码 / Error code | 错误 / Error                                                                          |
|------------------|-------------------------------------------------------------------------------------|
| 2                | 未加载模型或未上传图片 / No model loaded or no image uploaded                                  |
| 3                | 未知错误 / Unknown error                                                                |
| 4                | 替换 HTML 内容时未找到 utf8_path / utf8_path not found while replacing contents of the HTML |
| 5                | HTML 内容替换失败 / Failed to replace HTML content                                        |
| 9                | 未找到 WebDriver / WebDriver not found                                                 |

## scripts\HTMP2PDF.py

### conv_html_enc()

| 错误码 / Error code | 错误 / Error                                  |
|------------------|---------------------------------------------|
| 11               | HTML编码检测失败 / Failed to detect HTML encoding |
| 12               | 未知错误 / Unknown error                        |

### replace_content()

| 错误码 / Error code | 错误 / Error           |
|------------------|----------------------|
| 13               | 未知错误 / Unknown Error |

### output_pdf()

| 错误码 / Error code | 错误 / Error                          |
|------------------|-------------------------------------|
| 14               | 未找到 WebDriver / WebDriver not found |
| 15               | 未知错误 / Unknown Error                |

### aio()

| 错误码 / Error code | 错误 / Error           |
|------------------|----------------------|
| 16               | 未知错误 / Unknown Error |