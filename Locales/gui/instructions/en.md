# Instructions

## **Top**

- Under Construction
- Sometimes I might forget to change back my settings from testing, and the program won't load the model when it starts.
  This is where you can use the functions here.
- You can check the model status in the text box to see if it has been loaded.
- Click the `Load Model` button to load the model.
- Click the `Unload Model` button to unload the model.
- The program will automatically unload any loaded model before loading a new one, this process is executed
  automatically and does not require manual unloading.

## **OCR Tab**

### `OCR` Modes

- OCR: Standard OCR
- Formatted OCR: OCR with formatting

### `Fine-Grained` Modes

- Fine-grained OCR (with coordinate bounding boxes): OCR content within a specific box
- Fine-grained Formatted OCR (with coordinate bounding boxes): OCR and format content within a specific box
- Fine-grained OCR (with color bounding boxes): OCR content within a box of a specific color (I haven't tried this, but it seems like you
  would need to draw a red/green/blue box first and then select the color in the GUI)
- Fine-grained Formatted OCR (with color bounding boxes): OCR and format content within a box of a specific color

### `Multi-Crop` Modes

- Suitable for more complex images

### Render Mode

- Exist files will be overwritten!!!Check the file path before clicking the button!!!
- Render OCR content and save it as an HTML file
- Will be saved as UTF8 encoding and GB2312 encoding files
- ~~You can convert HTML to PDF~~ Deprecated

### Render Mode (New)

Modified the rendering algorithm, and it is different from the official implementation. The new algorithm is based on `pandoc` and `tex`, while the old one is based on `selenium`.

Because the browser, Edge updates, and WebDriver needs to be updated with each update, it is complex and difficult to maintain. So I deprecated it, only the official implementation that saves as HTML is available.

Select "Use New Render Mode" in the Settings tab and choose the format you want to output.

## **Renderer Tab**

- Enter the folder where you want to batch render images.
- The renderer will detect `.jpg` and `.png` files in the folder.
- ~~You can choose whether to convert HTML files to PDF (by default, it will convert).~~ Also deprecated.
- Click the batch render button, and you will find the rendered files in the `result` folder.

## **PDF Tab**

- Under Construction

### `split-to-image` Mode

- Splits the PDF file into images
- The split results are saved in the `imgs` folder, following the naming rule of
  `{PDF Name}_{Page Number (starting from 0)}.png`

### `render` Mode

- The `render` mode first executes the `split-to-image` mode, and then starts rendering each page of the PDF exported
  images
- The batch rendering in the renderer does not distinguish which images are from the PDF and which are not, but the
  `render` mode here can
- ~~When you choose the `render` mode, you will see an additional checkbox, if you check `Save as PDF`, there will be an
  additional `Merge PDF`~~ Also deprecated.
-~~ If you do not check `Merge PDF`, each page will be rendered into a PDF file, with the file name following the naming
  rule of `{PDF Name}_{Page Number (starting from 0)}.pdf`~~  Also deprecated.
- In any case, the rendering results are in the `result` folder

### `merge` Mode

- Upload the first page of the PDF sequence ({PDF Name}_0.pdf)
- Then the program will merge all pages into a single PDF

## **GGUF Tab**

Developing

- Only supported on Windows
- GGUF models and official Safetensors models are independent, you need to load the GGUF model to work. To save memory, it is recommended to unload the Safetensors model first.
- The operation method and the OCR tab are similar, but the mode selecting is not supported here for now.

## **Settings Tab**

- You can set the `fine-grained` mode's box coordinates and box colors here
- Render Mode settings have been deprecated and will not have any effect. To modify, please use Render Mode Settings (New)

## **Instructions Tab**

- You are now looking at the Instructions tab (≧∀≦)ゞ
