from scripts import local, scriptsLogger
from scripts import Renderer
from scripts import TempCleaner
from time import sleep
import os
import json

config_path = os.path.join("Configs", "Config.json")
try:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
except FileNotFoundError:
    print("配置文件未找到 / Configuration file not found")
    print("程序将在3秒后退出 / Exit in 3 seconds")
    sleep(3)
    exit(1)

OCRHandler_logger = scriptsLogger.getChild("OCRHandler")


class OCRHandler:
    def __init__(self):
        self.safetensors_model = None
        self.safetensors_tokenizer = None
        pass


    def ocr(self,
            image_path:str = None,
            mode:str = None,
            model:object = None,
            tokenizer:object = None):
        """
        OCR 和格式化 OCR
        如果不提供模型或tokenizer，则使用类自己的
        OCR and formatted OCR
        If no model or tokenizer provided, then model and tokenizer in the class itself will be used

        Args:
            image_path: 输入图像路径 / Input image path
            mode: OCR 模式 / OCR mode
            model: 模型 / Model
            tokenizer: Tokenizer

        Returns:
            一个元组，第一个是结果（str），第二个是错误码（成功则为0）
            A tuple, the first element is the result (string), the second one is the error code (will be 0 if succeeded)
        """
        # 检查图片和模型有效性
        model = self.safetensors_model if model is None else model
        tokenizer = self.safetensors_tokenizer if tokenizer is None else tokenizer
        if image_path is None or model is None or tokenizer is None:
            OCRHandler_logger.error(local['OCRHandler']['error']['no_model_img'])
            return local['OCRHandler']['error']['no_model_img'], 19
        OCRHandler_logger.debug(local['OCRHandler']['debug']['params'].format(params=str(locals())))

        try:
            if mode == "ocr":
                res = model.chat(tokenizer, image_path, ocr_type='ocr')
                return res, 0
            elif mode == "format":
                res = model.chat(tokenizer, image_path, ocr_type='format')
                return res, 0
            else:
                OCRHandler_logger.error(local['OCRHandler']['error']['invalid_mode'].format(mode=mode))
                res = local['OCRHandler']['error']['invalid_mode'].format(mode=mode)
                return res, 20
        except Exception as e:
            OCRHandler_logger.error(local['OCRHandler']['error']['ocr_fail'].format(error=str(e)))
            return local['OCRHandler']['error']['ocr_fail'].format(error=str(e)), 16


    def render_old(self,
                   image_path:str = None,
                   pdf_conv_conf:bool = False,
                   temp_clean:bool = True,
                   model:object = None,
                   tokenizer:object = None) -> tuple[str,int]:
        """
        渲染模式（旧版）
        渲染一张图片，可保存为PDF，使用selenium
        如果未提供模型，则默认使用类的模型
        Render mode (old)
        Render one image, able to save as PDF, using selenium

        Args:
            image_path: 输入图像路径 / Input image path
            pdf_conv_conf: 是否保存为 PDF / Whether to save as PDF
            temp_clean: 是否清理临时文件 / Whether to clean temp files
            model: 模型（safetensors） / Model (safetensors)
            tokenizer: Tokenizer (safetensors)

        Returns:
            一个元组，第一项是结果，第二项是错误码
            如果成功，则第二项为 0
            A tuple, the first one is the result, the second one is the error code
            If succeeded, the second one will be 0
        """
        # 检查模型和图片是否有效
        model = self.safetensors_model if model is None else model
        tokenizer = self.safetensors_tokenizer if tokenizer is None else tokenizer
        if model is None or tokenizer is None or image_path is None:
            OCRHandler_logger.error(local['OCRHandler']['error']['no_model_img_render_old'])
            return local['OCRHandler']['error']['no_model_img_render_old'], 19

        OCRHandler_logger.debug(local['OCRHandler']['debug']['params_render_old'].format(params=str(locals())))

        image_basename = os.path.basename(image_path)
        try:
            OCRHandler_logger.debug(local['OCRHandler']['debug']['got_img_name'].format(img_name=image_basename))
            render_status = Renderer.render(model=model,
                                            tokenizer=tokenizer,
                                            img_path=image_path,
                                            conv_to_pdf=pdf_conv_conf,
                                            wait=config["pdf_render_wait"],
                                            time=config["pdf_render_wait_time"])
            if render_status == 0:
                OCRHandler_logger.info(local['OCRHandler']['info']['render_completed'])
                if temp_clean and pdf_conv_conf:
                    OCRHandler_logger.info(local['OCRHandler']['info']['temp_cleaning'])
                    TempCleaner.cleaner(["result"],
                                        [f"{os.path.splitext(image_basename)[0]}-gb2312.html",
                                         f"{os.path.splitext(image_basename)[0]}-utf8.html",
                                         f"{os.path.splitext(image_basename)[0]}-utf8-local.html"])
                if temp_clean and not pdf_conv_conf:
                    OCRHandler_logger.info(local['OCRHandler']['info']['temp_cleaning'])
                    TempCleaner.cleaner(["result"], [f"{os.path.splitext(image_basename)[0]}-gb2312.html"])
                else:
                    OCRHandler_logger.info(local['OCRHandler']['info']['temp_cleaning_skipped'])
                res = local["OCRHandler"]["info"]["render_completed"].format(img_file=image_basename)
                return res, 0
            else:
                OCRHandler_logger.error(local['OCRHandler']['error']['render_fail'].format(img=image_basename, code=render_status))
                res = local["OCRHandler"]["error"]["render_fail"].format(img=image_basename, code=render_status)
                return res, 17
        except Exception as e:
            OCRHandler_logger.error(local['OCRHandler']['error']['render_fail_unexpected'].format(img=image_basename, error=str(e)))
            return local["OCRHandler"]["error"]["render_fail_unexpected"].format(img=image_basename, error=str(e)), 16

    def ocr_fg(self,
               image_path:str = None,
               fg_box_x1:int = 0,
               fg_box_y1:int = 0,
               fg_box_x2:int = 0,
               fg_box_y2:int = 0,
               mode:str = None,
               fg_color:str = "red",
               model:object = None,
               tokenizer:object = None) -> tuple[str, int]:
        """
        指定区域的 OCR 识别
        如果不提供 model 和 tokenizer，则默认使用类自己的
        OCR recognition for specified area
        If no model or tokenizer provided, by default, model and tokenizer in class itself will be used

        Args:
            image_path: 输入图像路径 / Input image path
            fg_box_x1: 指定区域 x 坐标 1 / The first x coordinate of the specified area
            fg_box_y1: 指定区域 y 坐标 1 / The first y coordinate of the specified area
            fg_box_x2: 指定区域 x 坐标 2 / The second x coordinate of the specified area
            fg_box_y2: 指定区域 y 坐标 2 / The second y coordinate of the specified area
            mode: OCR 模式 / OCR mode
            fg_color: 指定颜色 / Specified color
            model: 模型 （safetensors） / model (safetensors)
            tokenizer: Tokenizer (safetensors)
        Returns:
            一个元组， 第一项是结果（str），第二个是错误码，成功则为 0
            A tuple, the first element is the result (string), the second one is error code, will be 0 if succeeded
        """
        # 检查模型和图片是否有效
        model = self.safetensors_model if model is None else model
        tokenizer = self.safetensors_tokenizer if tokenizer is None else tokenizer
        if model is None or tokenizer is None or image_path is None:
            OCRHandler_logger.error(local['OCRHandler']['error']['no_model_img_fg'])
            return local['OCRHandler']['error']['no_model_img_fg'], 19

        OCRHandler_logger.debug(local['OCRHandler']['debug']['params_fg'].format(params=str(locals())))

        if mode == "fine-grained-ocr":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            OCRHandler_logger.debug(local['OCRHandler']['debug']['current_ocr_box'].format(box=box))
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_box=box)
            return res, 0
        elif mode == "fine-grained-format":
            # 构建 OCR 框 / Building OCR box
            box = f"[{fg_box_x1}, {fg_box_y1}, {fg_box_x2}, {fg_box_y2}]"
            OCRHandler_logger.debug(local['OCRHandler']['debug']['current_ocr_box'].format(box=box))
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_box=box)
            return res, 0
        elif mode == "fine-grained-color-ocr":
            OCRHandler_logger.debug(local['OCRHandler']['debug']['current_ocr_color'].format(color=fg_color))
            res = model.chat(tokenizer, image_path, ocr_type='ocr', ocr_color=fg_color)
            return res, 0
        elif mode == "fine-grained-color-format":
            OCRHandler_logger.debug(local['OCRHandler']['debug']['current_ocr_color'].format(color=fg_color))
            res = model.chat(tokenizer, image_path, ocr_type='format', ocr_color=fg_color)
            return res, 0
        else:
            OCRHandler_logger.error(local['OCRHandler']['error']['invalid_mode_fg'].format(mode=mode))
            res = local["OCRHandler"]["error"]["invalid_mode_fg"].format(mode=mode)
            return res, 18

    def ocr_crop(self,
                 image_path:str = None,
                 mode:str = None,
                 model:object = None,
                 tokenizer:object = None) -> tuple[str, int]:
        """
        multi-crop OCR，更适合复杂文档
        如果不提供模型和 tokenizer，则默认使用类自身的
        multi-crop OCR, suitable for complex document
        If no model or tokenizer were provided, then by default, model and tokenizer in the class itself will be used

        Args:
            image_path: 输入图片路径 / Input image path
            mode: multi-crop OCR 模式 / multi-crop OCR mode
            model: 模型（safetensors） / Model (safetensors)
            tokenizer: Tokenizer (safetensors)

        Returns:
            一个元组，第一个元素是结果（str），第二个是错误码，成功则为 0
            A tuple, the first element is the result (string), the second one is the error code, will be 0 if succeeded
        """
        # 检查图片是否上传
        # 检查模型是否已加载
        model = self.safetensors_model if model is None else model
        tokenizer = self.safetensors_tokenizer if tokenizer is None else tokenizer
        if model is None or tokenizer is None or image_path is None:
            OCRHandler_logger.error(local["OCRHandler"]["error"]["no_model_crop"])
            res = local["OCRHandler"]["error"]["no_model_crop"]
            return res, 19

        OCRHandler_logger.debug(local['OCRHandler']['debug']['params_crop'].format(params=str(locals())))

        try:
            if mode == "multi-crop-ocr":
                res = model.chat_crop(tokenizer, image_path, ocr_type='ocr')
                return res, 0
            elif mode == "multi-crop-format":
                res = model.chat_crop(tokenizer, image_path, ocr_type='format')
                return res, 0
            else:
                OCRHandler_logger.error(local["OCRHandler"]["error"]["invalid_mode_crop"].format(mode=mode))
                res = local["OCRHandler"]["error"]["invalid_mode_crop"].format(mode=mode)
                return res, 18
        except Exception as e:
            OCRHandler_logger.error(local['OCRHandler']['error']['crop_ocr_fail'].format(error=str(e)))
            return local["OCRHandler"]["error"]["crop_ocr_fail"].format(error=str(e)), 16