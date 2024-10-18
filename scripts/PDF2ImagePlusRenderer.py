import fitz
import os
import glob
import scripts.Renderer as Renderer

pdf_path_base = ''


def get_base_name(path):
    return os.path.basename(path)


def remove_extension(base_name):
    return os.path.splitext(base_name)[0]


def split_pdf(pdf_path, img_path, target_dpi):
    """
    将PDF文件拆分为单页PDF文件，并保存为PNG图像文件。

    参数:
    pdf_path -- PDF文件路径
    img_path -- 保存PNG图像文件的目录路径
    target_dpi -- 目标DPI

    返回:
    True -- 成功拆分PDF文件
    False -- 拆分PDF文件失败
    """
    try:
        print(f"[Info-PDF2ImagePlusRenderer.split_pdf] 正在拆分PDF文件：{pdf_path}")
        print(f"[Info-PDF2ImagePlusRenderer.split_pdf] 正在打开：{pdf_path}")
        doc = fitz.open(pdf_path)

        pdf_path_base = get_base_name(path=pdf_path)
        pdf_path_base = remove_extension(pdf_path_base)

        for page_number in range(len(doc)):
            zoom = target_dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            # 将PDF页面转换为图像
            print(f"[Info-PDF2ImagePlusRenderer.split_pdf] 正在处理第 {page_number} 页")
            page = doc[page_number]
            pix = page.get_pixmap(matrix=matrix)

            # 保存图像
            output_path = os.path.join(f"{img_path}", f"{pdf_path_base}_{page_number}.png")
            pix.save(output_path)
            print(f"[Info-PDF2ImagePlusRenderer.split_pdf] 已保存 {output_path}")

        doc.close()
        return True
    except Exception as e:
        print(f"[Error-PDF2ImagePlusRenderer.split_pdf] 拆分PDF文件失败: {e}")
        return False


def get_sorted_png_files(directory, prefix):
    """
    获取指定目录下，符合前缀和整数后缀的PNG文件列表，并按整数大小排序。

    参数:
    directory -- 要搜索的目录路径
    prefix -- 文件名前缀

    返回:
    sorted_files -- 按整数大小排序的文件列表
    """
    try:
        # 构建匹配模式
        pattern = os.path.join(directory, f"{prefix}_*.png")

        # 获取所有匹配的文件
        print(f"[Info-PDF2ImagePlusRenderer.get_sorted_png_files] 正在获取 PNG 文件列表")
        files = glob.glob(pattern)

        # 定义一个函数，用于从文件名中提取整数部分
        print(f"[Info-PDF2ImagePlusRenderer.get_sorted_png_files] 正在排序 PNG 图片列表")
        def extract_integer(filename):
            # 假设文件名格式正确，去掉扩展名 .png 和前缀
            number_part = os.path.basename(filename).replace(f"{prefix}_", "").replace(".png", "")
            return int(number_part)

        # 按整数大小排序文件列表
        sorted_files = sorted(files, key=extract_integer)
        return sorted_files
    except Exception as e:
        print(f"[Error-PDF2ImagePlusRenderer.get_sorted_png_files] 获取 PNG 文件列表失败: {e}")


def pdf_renderer(model, tokenizer, pdf_path, target_dpi, pdf_convert, wait, time):
    """
    将PDF文件转换为图片，并调用渲染器进行渲染。

    参数:
    model -- 模型
    tokenizer -- 分词器
    pdf_path -- PDF文件路径
    target_dpi -- 目标DPI
    pdf_convert -- 是否转换为PDF
    wait -- 等待时间
    time -- 时间

    返回:
    True -- 成功渲染
    False -- 渲染失败
    """
    # 创建目录
    if not os.path.exists("pdf"):
        os.makedirs("pdf")
    if not os.path.exists("imgs"):
        os.makedirs("imgs")

    try:
        # 将 pdf 文件转换为图片
        print(f"[Info-PDF2ImagePlusRenderer.pdf_renderer] 正在将PDF文件转换为图片：{pdf_path}")
        split_pdf(pdf_path=pdf_path, img_path="imgs", target_dpi=target_dpi)
        # pdf 文件名
        pdf_name = get_base_name(path=pdf_path)
        pdf_name = remove_extension(pdf_name)
        # 获取图片列表
        print(f"[Info-PDF2ImagePlusRenderer.pdf_renderer] 正在获取图片列表")
        img_list = get_sorted_png_files(directory="imgs", prefix=pdf_name)
        if len(img_list) == 0:
            print(f"[Error-PDF2ImagePlusRenderer.pdf_renderer] 未找到图片文件")
            return False
        else:
            pass
        # 调用渲染器
        for img in img_list:
            print(f"[Info-PDF2ImagePlusRenderer.pdf_renderer] 正在渲染图片：{img}")
            success = Renderer.render(model=model, tokenizer=tokenizer, image_path=img, wait=wait, time=time,
                                      convert_to_pdf=pdf_convert)
            if not success:
                return False
        return True
    except Exception as e:
        print(f"[Error-PDF2ImagePlusRenderer.pdf_renderer] 渲染失败: {e}")
        return False
