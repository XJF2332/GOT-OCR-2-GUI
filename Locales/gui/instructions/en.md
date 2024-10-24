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

- ocr: Standard OCR
- format: OCR with formatting

### `Fine-Grained` Modes

- fine-grained-ocr: OCR content within a specific box
- fine-grained-format: OCR and format content within a specific box
- fine-grained-color-ocr: OCR content within a box of a specific color (I haven't tried this, but it seems like you
  would need to draw a red/green/blue box first and then select the color in the GUI)
- fine-grained-color-format: OCR and format content within a box of a specific color

### `Multi-Crop` Modes

- Suitable for more complex images

### `Render` Modes

- Exist files will be overwritten!!!Check the file path before clicking the button!!!
- Render OCR content and save it as an HTML file
- Will be saved as UTF8 encoding and GB2312 encoding files
- You can convert HTML to PDF

### **How to render**

1. Input image name in the text box, this will become the base name of the output files
2. You will find that three textboxes below changed, which means the name has been applied
3. Click the "Save as PDF" button to save the HTML file as a PDF file

## **Renderer Tab**

- Enter the folder where you want to batch render images.
- The renderer will detect `.jpg` and `.png` files in the folder.
- You can choose whether to convert HTML files to PDF (by default, it will convert).
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
- When you choose the `render` mode, you will see an additional checkbox, if you check `Save as PDF`, there will be an
  additional `Merge PDF`
- If you do not check `Merge PDF`, each page will be rendered into a PDF file, with the file name following the naming
  rule of `{PDF Name}_{Page Number (starting from 0)}.pdf`
- In any case, the rendering results are in the `result` folder

### `merge` Mode

- Upload the first page of the PDF sequence ({PDF Name}_0.pdf)
- Then the program will merge all pages into a single PDF

## **Instructions Tab**

- You are now looking at the Instructions tab (≧∀≦)ゞ

