"""
PDF 信息提取模块
用于从 PDF 文件中提取文本和图片信息，支持多种提取模式
"""

# ==================== 导入语句 ====================

# 标准库导入
import os
import time

# 第三方库导入
import cv2
import fitz
import numpy as np
import easyocr
import opencc

# ==================== PDF 图片处理函数 ====================


def savePDFasImage(uploaded_file_name, page, page_img_save_dir):
    """
    将 PDF 页面保存为图片

    功能说明：
    1. 生成两种分辨率的图片（1x 和 6x）
    2. 使用 fitz 库进行 PDF 渲染
    3. 保存图片到指定目录

    @param uploaded_file_name: 上传的文件名
    @param page: PDF 页面对象
    @param page_img_save_dir: 图片保存目录
    @return: (原始分辨率图片路径, 高分辨率图片路径)
    """
    file_name = uploaded_file_name[:-4]

    # 生成高分辨率图片 (6x)
    zoom_x = 6.0
    zoom_y = 6.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    page_image_6x = "%s/%s-page-%i-%s.png" % (
        page_img_save_dir, file_name, page.number, '6x')
    pix.save(page_image_6x)

    # 生成原始分辨率图片 (1x)
    zoom_x = 1.0
    zoom_y = 1.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    page_image = "%s/%s-page-%i-%s.png" % (
        page_img_save_dir, file_name, page.number, '1x')
    pix.save(page_image)

    return page_image, page_image_6x


def deletePDFImage(page_image, page_image_6x):
    """
    删除 PDF 生成的图片文件

    @param page_image: 原始分辨率图片路径
    @param page_image_6x: 高分辨率图片路径
    """
    try:
        os.remove(page_image)
        print(f"文件 {page_image} 已成功删除。")
        os.remove(page_image_6x)
        print(f"文件 {page_image_6x} 已成功删除。")
    except FileNotFoundError:
        print(f"文件不存在。")
    except Exception as e:
        print(f"删除文件时发生错误：{e}")

# ==================== 图片检测函数 ====================


def detectImgFromPDFPage(uploaded_file_name, page, page_image_origin, page_image, img_save_dir, threhold=5000):
    """
    从 PDF 页面中检测并提取图片

    功能说明：
    1. 使用 OpenCV 进行图片检测
    2. 应用边缘检测和轮廓分析
    3. 提取并保存检测到的图片

    @param uploaded_file_name: 上传的文件名
    @param page: PDF 页面对象
    @param page_image_origin: 原始分辨率图片路径
    @param page_image: 高分辨率图片路径
    @param img_save_dir: 图片保存目录
    @param threhold: 轮廓面积阈值
    @return: (提取的图片名称列表, 图片坐标列表)
    """
    file_name = uploaded_file_name[:-4]
    zoom_x = 6
    zoom_y = 6

    # 读取图片
    zoomed_image = cv2.imread(page_image)
    image = cv2.imread(page_image_origin)

    # 图像预处理
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=20, threshold2=100)
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)

    # 轮廓检测
    contours, hierarchy = cv2.findContours(
        dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤轮廓
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threhold:
            print(area)
            filtered_contours.append(contour)

    # 提取图片区域
    split_res = image.copy()
    extracted_images = []
    extracted_images_names = []
    extracted_images_coordinates = []

    for idx, contour in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(contour)
        extracted_images.append(
            zoomed_image[y * zoom_y:(y + h) * zoom_y, x * zoom_x:(x + w) * zoom_x])
        extracted_images_coordinates.append(
            [y * zoom_y, (y + h) * zoom_y, x * zoom_x, (x + w) * zoom_x])

        # 绘制检测框
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int64(box)
        split_res = cv2.drawContours(split_res, [box], 0, (0, 0, 255), 2)

    # 保存提取的图片
    for idx, extracted_image in enumerate(extracted_images):
        real_idx = len(extracted_images) - 1 - idx
        cv2.imwrite("%s/%s-page-%i-%i.png" % (img_save_dir,
                    file_name, page.number, real_idx), extracted_image)
        extracted_images_names.append(
            "%s-page-%i-%i.png" % (file_name, page.number, real_idx))

    extracted_images_names.reverse()
    extracted_images_coordinates.reverse()
    return extracted_images_names, extracted_images_coordinates

# ==================== 文本提取函数 ====================


def detectyTextFromPDFPage(page_image, lang):
    """
    从 PDF 页面中提取文本（通用模式）

    功能说明：
    1. 使用 EasyOCR 进行文本识别
    2. 支持繁体中文转换
    3. 合并段落文本

    @param page_image: 图片路径
    @param lang: 语言设置
    @return: 提取的文本内容
    """
    reader = easyocr.Reader(lang)
    result = reader.readtext(page_image, paragraph=True, rotation_info=[90, 180, 270],
                             contrast_ths=0.3, adjust_contrast=0.5, slope_ths=0.2,
                             height_ths=2.0, width_ths=2.0, x_ths=2.0, y_ths=1.0)

    # 繁体中文转换
    if lang[0] == 'ch_tra':
        print('ch_tra')
        converter = opencc.OpenCC('t2s.json')

    filtered_results = []
    for (coordinate, text) in result:
        print("convert before: ", text)
        if lang[0] == 'ch_tra':
            text = converter.convert(text)
            print("convert after: ", text)
        filtered_results.append(text)

    # 合并文本
    final_result = ""
    for i in filtered_results:
        final_result += i

    print(final_result + '\n')
    return final_result


def detectyTextFromPDFPage_Type1(page_image):
    """
    从 PDF 页面中提取文本（模式1）

    功能说明：
    1. 使用简体和英文识别
    2. 不保留坐标信息
    3. 直接合并所有文本

    @param page_image: 图片路径
    @return: 提取的文本内容
    """
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext(page_image, detail=0, paragraph=True, rotation_info=[90, 180, 270],
                             contrast_ths=0.3, adjust_contrast=0.5, slope_ths=0.2,
                             height_ths=2.0, width_ths=2.0, x_ths=2.0, y_ths=1.0)

    final_result = ""
    for i in result:
        final_result += i
    print(final_result)
    return final_result


def detectyTextFromPDFPage_Type2(page_image):
    """
    从 PDF 页面中提取文本（模式2）

    功能说明：
    1. 使用简体和英文识别
    2. 保留坐标信息
    3. 根据面积过滤文本区域

    @param page_image: 图片路径
    @return: 过滤后的文本列表（包含坐标）
    """
    reader = easyocr.Reader(['ch_sim', 'en'])
    results = reader.readtext(page_image, paragraph=True, rotation_info=[90, 180, 270],
                              min_size=1000, contrast_ths=0.3, adjust_contrast=0.5,
                              slope_ths=0.5, height_ths=1.0, width_ths=1.0,
                              x_ths=20.0, y_ths=0.3)

    filtered_results = []
    for (coordinate, text) in results:
        area = (coordinate[2][0] - coordinate[0][0]) * \
            (coordinate[2][1] - coordinate[0][1])
        if area >= 40000.0:
            filtered_results.append((coordinate, text))

    return filtered_results


def detectyTextFromPDFPage_Type4(page_image):
    """
    从 PDF 页面中提取文本（模式4）

    功能说明：
    1. 使用简体和英文识别
    2. 根据垂直位置过滤文本
    3. 过滤过短的文本

    @param page_image: 图片路径
    @return: 提取的文本内容
    """
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext(page_image, paragraph=True, rotation_info=[90, 180, 270],
                             contrast_ths=0.3, adjust_contrast=0.5, slope_ths=0.2,
                             height_ths=2.0, width_ths=2.0, x_ths=2.0, y_ths=1.0)

    filtered_results = []
    for (coordinate, text) in result:
        if coordinate[3][1] >= 700:
            filtered_results.append(text)

    final_result = ""
    for i in filtered_results:
        final_result += i

    if len(final_result) < 50:
        final_result = ""

    print(final_result + '\n')
    return final_result

# ==================== 主函数 ====================


def info_extract_function(name):
    """
    信息提取主函数

    功能说明：
    1. 打开 PDF 文件
    2. 处理指定页面范围
    3. 提取图片和文本信息

    @param name: 文件名
    """
    file_path = 'camera_ready_paper.pdf'
    doc = fitz.open(file_path)

    for page in doc.pages(11, 13, 1):
        page_image, page_image_6x = savePDFasImage(page, 'pdf_image')
        detectImgFromPDFPage(page, page_image, page_image_6x, 'loadedImgs')
        detectyTextFromPDFPage_Type1(page_image_6x)


if __name__ == '__main__':
    # 计时开始
    start_time = time.time()
    info_extract_function('PyCharm')
    # 计时结束
    end_time = time.time()
    # 计算执行时间
    execution_time = end_time - start_time
    print("代码执行时间：", execution_time, "秒")
