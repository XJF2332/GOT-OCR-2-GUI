import numpy as np
import onnxruntime as ort
from torchvision.transforms import InterpolationMode

import ctypes
import torch
import torchvision.transforms as transforms
import PIL.Image as Image
from pathlib import Path

class GOTImageEvalProcessor:
    def __init__(self, image_size=384, mean=None, std=None):
        if mean is None:
            mean = (0.48145466, 0.4578275, 0.40821073)
        if std is None:
            std = (0.26862954, 0.26130258, 0.27577711)

        self.normalize = transforms.Normalize(mean, std)

        self.transform = transforms.Compose(
            [
                transforms.Resize(
                    (image_size, image_size), interpolation=InterpolationMode.BICUBIC
                ),
                transforms.ToTensor(),
                self.normalize,
            ]
        )

    def __call__(self, item) -> torch.Tensor:
        # print(item.mode)
        # import numpy as np
        # print(np.array(item).dtype)
        return self.transform(item)

cwd= Path(__file__).parent

# 加载DLL
dll_path = f"{ cwd / 'libocr.dll'}"
libocr = ctypes.CDLL(dll_path)

# 定义GOT_TYPE
GOT_TYPE = ctypes.c_int
GOT_OCR_TYPE = 1
GOT_FORMAT_TYPE = 2
GOT_CROP_OCR_TYPE = 3
GOT_CROP_FORMAT_TYPE = 4


# 定义结构体
class ocr_result(ctypes.Structure):
    _fields_ = [
        ("result", ctypes.c_char_p),
        ("error", ctypes.c_char_p)
    ]


# 定义函数原型
libocr.ocr_init.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
libocr.ocr_init.restype = ctypes.c_void_p

libocr.ocr_free.argtypes = [ctypes.c_void_p]
libocr.ocr_free.restype = ctypes.c_int

libocr.ocr_run.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int, GOT_TYPE]
libocr.ocr_run.restype = ctypes.POINTER(ocr_result)

libocr.ocr_cleanup_ctx.argtypes = [ctypes.c_void_p]
libocr.ocr_cleanup_ctx.restype = ctypes.c_int

libocr.ocr_free_result.argtypes = [ctypes.POINTER(ocr_result)]
libocr.ocr_free_result.restype = ctypes.c_int


# 封装函数
def ocr_init(argc, argv):
    argv_array = (ctypes.c_char_p * argc)()
    argv_array[:] = [arg.encode('utf-8') for arg in argv]
    return libocr.ocr_init(argc, argv_array)


def ocr_free(ctx):
    return libocr.ocr_free(ctx)


def ocr_run(ctx, image_embeds, got_type):
    # 确保 image_embeds 是一个 numpy 数组
    if not isinstance(image_embeds, np.ndarray):
        raise TypeError("image_embeds must be a np.ndarray")

    # 确保数组是连续的（C 风格）且数据类型为 float32
    image_embeds = np.ascontiguousarray(image_embeds, dtype=np.float32)

    # 获取数组的指针
    image_embeds_ptr = image_embeds.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    # 调用 C 函数
    return libocr.ocr_run(ctx, image_embeds_ptr, image_embeds.shape[0], got_type)


def ocr_cleanup_ctx(ctx):
    return libocr.ocr_cleanup_ctx(ctx)


def ocr_free_result(result):
    return libocr.ocr_free_result(result)


def main(encoder_path, decoder_path, image_path, providers):
    img = Image.open(image_path).convert('RGB')
    session = ort.InferenceSession(encoder_path, providers=providers)
    decoder = ocr_init(7, [
        "got",
        "-m",
        decoder_path,
        "-ngl",
        "100",
        "--log-verbosity",
        "-1",
    ])
    img_arr: np.ndarray = GOTImageEvalProcessor(1024)(img).detach().numpy()
    img_embeds: np.ndarray = session.run(None, {
        "input": img_arr.reshape(1, 3, 1024, 1024)
    })[0].reshape(256, 1024)
    result = ocr_run(decoder, img_embeds, GOT_CROP_FORMAT_TYPE)
    try:
        if result:
            print("Error:", result.contents.error.decode('utf-8') if result.contents.error is not None else None)
    finally:
        # 清理上下文
        ocr_cleanup_ctx(decoder)
        ocr_free(decoder)
    return result.contents.result.decode('utf-8') if result.contents.result is not None else None


if __name__ == '__main__':
    encoder_path = str(cwd / r"C:\AI\GOT-OCR-2-GUI\gguf\Encoder.onnx")
    decoder_path = str(cwd / r"C:\AI\GOT-OCR-2-GUI\gguf\decoders\Decoder-Q8_0.gguf")
    img_path = r"C:\AI\GOT-OCR-2-GUI\imgs\1_1.png"
    res = main(encoder_path=encoder_path, decoder_path=decoder_path, image_path=img_path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    print(res)
