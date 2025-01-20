# GOT-OCR-2的CLI应用

## 错误码对照表

| 错误码 | 错误信息          |
|-----|---------------|
| 1   | 配置文件未找到       |
| 2   | 语言文件未找到       |
| 3   | 输入的路径不受支持：目录  |
| 4   | 未找到输入路径所指向的文件 |
| 5   | 输入文件类型不受支持    |

## 参数解释

### 图片 OCR 模式

**指定方式**：`--image-ocr-mode`或`-IM`  
**类型**：字符串  
**可选项**：

| 参数                          | 解释                       |
|-----------------------------|--------------------------|
| `ocr`                       | 最简单的不带格式的 OCR            |
| `format`                    | 带格式的 OCR                 |
| `fine-grained-ocr`          | 用坐标框选 OCR 区域并执行不带格式的 OCR |
| `fine-grained-format`       | 用坐标框选 OCR 区域并执行格式化 OCR   |
| `fine-grained-color-ocr`    | 用颜色框选 OCR 区域并执行不带格式的 OCR |
| `fine-grained-color-format` | 用颜色框选 OCR 区域并执行格式化 OCR   |
| `multi-crop-ocr`            | 更适合复杂内容的 OCR，不带格式        |
| `multi-crop-format`         | 更适合复杂内容的 OCR，带格式         |
| `render`                    | 把 OCR 结果渲染成 HTML 和 PDF   |

### PDF 模式

**指定方式**：`--pdf-ocr-mode`或`-PM`
**类型**：字符串
**可选项**：

| 参数       | 解释                                                 |
|----------|----------------------------------------------------|
| `split`  | 把 PDF 拆分成图片，这个选项和下面的`merge`都不会执行 OCR               |
| `merge`  | 把独立的 PDF 合并成一个 PDF，你必须选择满足`<string>_0.pdf`的 PDF 文件 |
| `render` | 对 PDF 执行 OCR，并渲染成 HTML 和 PDF，它会产生很多临时文件            |

### 其他参数

### `--detailed-help` (`-DH`)
- **作用**: 显示这个帮助文档
- **必须**: 否
- **默认值**: False
- **类型**: `store_true`
- **示例**: `.\CLI.py --detailed-help`

### `--path` (`-P`)
- **作用**: 指定输入文件的路径，可以是图片或者 PDF
- **必须**: 是
- **默认值**: 无
- **类型**: `str`
- **示例**: `.\CLI.py --path path\to\your\image\or\pdf`

### `--fg-box-x1` (`-X1`), `--fg-box-y1` (`-Y1`), `--fg-box-x2` (`-X2`), `--fg-box-y2` (`-Y2`)
- **作用**: 指定用于`fine-grained`模式的框的 X1/Y1/X2/Y2 坐标
- **必须**: 否
- **默认值**: 0
- **类型**: `int`
- **示例**: `.\CLI.py --fg-box-x1 0 --fg-box-y1 0 --fg-box-x2 100 --fg-box-y2 100 --path path\to\your\image`

### `--fg-color` (`-C`)
- **作用**: 指定用于`fine-grained-color`模式的框的颜色，你得先把框画好
- **必须**: 否
- **默认值**：`red`
- **可选项**：`red`, `green`, `blue`
- **类型**: `str`
- **示例**: `.\CLI.py --fg-color red --path path\to\your\image`

### `--no-pdf` (`-NP`)
- **作用**: 不要把结果保存为 PDF，只在`render`模式下生效
- **必须**: 否
- **默认值**: False
- **类型**: `store_false`
- **示例**: `.\CLI.py --path path\to\your\image --image-ocr-mode render --no-pdf`

### `--clean-temp` (`-CT`)
- **作用**: 是否在执行完成后清理临时文件，只对`render`模式有效
- **必须**: 否
- **默认值**: False
- **类型**: `store_true`
- **示例**: `.\CLI.py --path path\to\your\image --image-ocr-mode render --clean-temp`

### `--dpi` (`-D`)
- **作用**: 指定 PDF 转图片时的 DPI
- **必须**: 否
- **默认值**: 150
- **类型**: `int`
- **示例**：`.\CLI.py --path path\to\your\pdf --pdf-ocr-mode split --dpi 72`

### `--merge` (`-M`)
- **作用**: 在渲染后自动合并渲染结果，因为 PDF OCR 的渲染模式本质上就是把 PDF 拆成图片，然后单独渲染每张图片，渲染出来就是很多个 PDF
- **必须**: 否
- **默认值**: False
- **类型**: `store_true`
- **示例**: `.\CLI.py --path path\to\your\pdf --pdf-ocr-mode render --merge`