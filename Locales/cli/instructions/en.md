# CLI Application for GOT-OCR-2

## Error Code Reference Table

| Error Code | Error Message                              |
|------------|--------------------------------------------|
| 1          | Configuration file not found               |
| 2          | Language file not found                    |
| 3          | Unsupported input path: directory          |
| 4          | File not found at the specified input path |
| 5          | Unsupported input file type                |

## Parameter Explanation

### Image OCR Mode

**Specification**: `--image-ocr-mode` or `-IM`  
**Type**: String  
**Options**:

| Parameter                     | Explanation                                                    |
|-------------------------------|----------------------------------------------------------------|
| `ocr`                         | Basic OCR without formatting                                   |
| `format`                      | OCR with formatting                                            |
| `fine-grained-ocr`            | OCR without formatting using coordinate-based region selection |
| `fine-grained-format`         | OCR with formatting using coordinate-based region selection    |
| `fine-grained-color-ocr`      | OCR without formatting using color-based region selection      |
| `fine-grained-color-format`   | OCR with formatting using color-based region selection         |
| `multi-crop-ocr`              | OCR without formatting, better suited for complex content      |
| `multi-crop-format`           | OCR with formatting, better suited for complex content         |
| `render`                      | Render OCR results into HTML and PDF                           |

### PDF Mode

**Specification**: `--pdf-ocr-mode` or `-PM`  
**Type**: String  
**Options**:

| Parameter       | Explanation                                                                       |
|-----------------|-----------------------------------------------------------------------------------|
| `split`         | Split PDF into images; this option and `merge` do not perform OCR                 |
| `merge`         | Merge separate PDFs into one; you must select PDF files matching `<string>_0.pdf` |
| `render`        | Perform OCR on PDF and render into HTML and PDF; generates many temporary files   |

### Other Parameters

### `--detailed-help` (`-DH`)
- **Purpose**: Display this help document
- **Required**: No
- **Default**: False
- **Type**: `store_true`
- **Example**: `.\CLI.py --detailed-help`

### `--path` (`-P`)
- **Purpose**: Specify the path to the input file, which can be an image or PDF
- **Required**: Yes
- **Default**: None
- **Type**: `str`
- **Example**: `.\CLI.py --path path\to\your\image\or\pdf`

### `--fg-box-x1` (`-X1`), `--fg-box-y1` (`-Y1`), `--fg-box-x2` (`-X2`), `--fg-box-y2` (`-Y2`)
- **Purpose**: Specify the X1/Y1/X2/Y2 coordinates for the box used in `fine-grained` mode
- **Required**: No
- **Default**: 0
- **Type**: `int`
- **Example**: `.\CLI.py --fg-box-x1 0 --fg-box-y1 0 --fg-box-x2 100 --fg-box-y2 100 --path path\to\your\image`

### `--fg-color` (`-C`)
- **Purpose**: Specify the color for the box used in `fine-grained-color` mode; you need to draw the box first
- **Required**: No
- **Default**: `red`
- **Options**: `red`, `green`, `blue`
- **Type**: `str`
- **Example**: `.\CLI.py --fg-color red --path path\to\your\image`

### `--no-pdf` (`-NP`)
- **Purpose**: Do not save the result as a PDF; only effective in `render` mode
- **Required**: No
- **Default**: False
- **Type**: `store_false`
- **Example**: `.\CLI.py --path path\to\your\image --image-ocr-mode render --no-pdf`

### `--clean-temp` (`-CT`)
- **Purpose**: Whether to clean up temporary files after execution; only effective in `render` mode
- **Required**: No
- **Default**: False
- **Type**: `store_true`
- **Example**: `.\CLI.py --path path\to\your\image --image-ocr-mode render --clean-temp`

### `--dpi` (`-D`)
- **Purpose**: Specify the DPI when converting PDF to images
- **Required**: No
- **Default**: 150
- **Type**: `int`
- **Example**: `.\CLI.py --path path\to\your\pdf --pdf-ocr-mode split --dpi 72`

### `--merge` (`-M`)
- **Purpose**: Automatically merge rendered results after rendering; PDF OCR render mode essentially splits the PDF into images and renders each image separately, resulting in multiple PDFs
- **Required**: No
- **Default**: False
- **Type**: `store_true`
- **Example**: `.\CLI.py --path path\to\your\pdf --pdf-ocr-mode render --merge`