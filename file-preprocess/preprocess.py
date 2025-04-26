import fitz
import os
import json
import cv2
import numpy as np
import easyocr
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# ==================== 配置文件参数 ====================
# PDF文件存储目录
# 请确保此目录存在，并且包含要处理的PDF文件
# 如果是windows系统，请使用反斜杠（\）
pdf_store_dir = "./pdfFiles/my_paper"

# 要处理的PDF文件名
# 请将此处改为你要处理的PDF文件名
# 注意：文件名需要包含.pdf后缀
uploaded_file_name = "（勿外传）6.2024-山东馆藏文物精品大系·青铜器卷·秦汉篇.pdf"

# PDF文件完整路径
# 此路径由pdf_store_dir和uploaded_file_name自动组合生成
uploaded_file_path = os.path.join(pdf_store_dir, uploaded_file_name)

# 起始页码（从1开始计数）
# 例如：如果要从第12页开始处理，则设置为12
pageNum = 12

# 结束页码（从1开始计数）
# 例如：如果要处理到第246页，则设置为246
# 注意：结束页码必须大于等于起始页码
endPageNum = 246

# 是否使用简体中文（True: 简体中文, False: 繁体中文）
# True: 使用简体中文进行OCR识别
# False: 使用繁体中文进行OCR识别
isChSim = True

# OCR语言设置
# 根据isChSim的值自动设置OCR识别的语言
# ['ch_sim', 'en']: 简体中文和英文
# ['ch_tra', 'en']: 繁体中文和英文
lang = ['ch_sim', 'en'] if isChSim else ['ch_tra', 'en']
# ==================== 配置文件参数结束 ====================

extractedPDFPath = ''
existing_pages = []


def catalog_many_to_one(savedPageNum, savedText, text, thisPageImgList, newPageImgList, current_page_number, startPageNum, endPageNum):
    """
    处理文本和图片的关联关系，将多页内容整合到一起
    参数:
        savedPageNum: 已保存的页码
        savedText: 已保存的文本
        text: 当前页面的文本
        thisPageImgList: 当前页面的图片列表
        newPageImgList: 新页面的图片列表
        current_page_number: 当前页码
        startPageNum: 起始页码
        endPageNum: 结束页码
    返回:
        更新后的各种状态和内容
    """
    returnText = ''
    returnLastText = ''
    returnImgList = []
    returnLastImgList = []
    returnSavedPageNum = -1
    returnLastSavedPageNum = -1
    ifSaved = False
    ifLastPage = False

    # 如果当前页面没有文本内容
    if text == '':
        # 继续将新图片添加到当前图片列表中
        for img in newPageImgList:
            thisPageImgList.append(img)
    else:
        # 如果检测到新的文本内容
        if current_page_number != (startPageNum + 1):
            # 如果不是第一页，保存之前的内容并更新暂存项
            ifSaved = True
            returnText = savedText
            savedText = text
            returnSavedPageNum = savedPageNum
            savedPageNum = current_page_number
            returnImgList = thisPageImgList
            thisPageImgList = newPageImgList
        else:
            # 如果是第一页，直接更新暂存项
            savedText = text
            savedPageNum = current_page_number
            thisPageImgList = newPageImgList

    # 处理最后一页的情况
    if current_page_number == endPageNum and text == '':
        # 如果是最后一页且没有新内容，提交所有已保存的内容
        ifSaved = True
        returnText = savedText
        returnSavedPageNum = savedPageNum
        savedText = ''
        returnImgList = thisPageImgList
        thisPageImgList = []
    if current_page_number == endPageNum and text != '':
        # 如果是最后一页且有新内容，提交当前内容
        ifLastPage = True
        returnLastText = text
        returnLastImgList = newPageImgList
        returnLastSavedPageNum = current_page_number

    return savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList, ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum


def save_text_and_related_img_to_json(file_name, current_page_number, textList, relatedImgList):
    """
    将文本和相关的图片保存到JSON文件中
    参数:
        file_name: 文件名
        current_page_number: 当前页码
        textList: 文本列表
        relatedImgList: 相关图片列表
    """
    data = {
        "file_name": file_name,
        "page": current_page_number,
        "textList": textList,
        "thisTextImgList": relatedImgList,
    }
    with open(extractedPDFPath, "a") as json_file:
        json.dump(data, json_file, ensure_ascii=False)
        json_file.write(",")


def set_json_ending():
    """
    设置JSON文件的结束格式，删除最后一个逗号并添加右方括号
    """
    with open(extractedPDFPath, "r") as json_file:
        content = json_file.read()

    if content:
        content = content[:-1]

    with open(extractedPDFPath, "w") as json_file:
        json_file.write(content + "]")


def crop_padding_with_offset(image, padding=10):
    """
    裁剪图像边缘的填充，并记录偏移量
    参数:
        image: 输入图像
        padding: 填充大小
    返回:
        cropped: 裁剪后的图像
        offset_x, offset_y: x和y方向的偏移量
    """
    h, w = image.shape[:2]
    offset_x, offset_y = padding, padding
    cropped = image[padding:h - padding, padding:w - padding]
    return cropped, offset_x, offset_y


def detectImgFromPDFPage(uploaded_file_name, page, page_image_origin, page_image, img_save_dir, threhold=5000):
    """
    从PDF页面中检测并提取图片
    参数:
        uploaded_file_name: 上传的文件名
        page: PDF页面对象
        page_image_origin: 原始页面图像
        page_image: 处理后的页面图像
        img_save_dir: 图片保存目录
        threhold: 面积阈值，用于过滤小图片
    返回:
        extracted_images_names: 提取的图片文件名列表
        extracted_images_coordinates: 提取的图片坐标列表
    """
    file_name = uploaded_file_name[:-4]
    zoom_x = 6.0  # 水平缩放比例
    zoom_y = 6.0  # 垂直缩放比例

    # 读取图像
    zoomed_image = cv2.imread(page_image)
    image = cv2.imread(page_image_origin)

    # 使用高斯滤波平滑图像以减少噪音
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    blurred, offset_x, offset_y = crop_padding_with_offset(blurred)

    # Canny边缘检测
    edges = cv2.Canny(blurred, threshold1=20, threshold2=100)
    # 对边缘进行膨胀操作，以连接边缘并增强分割
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)

    # 寻找轮廓
    contours, hierarchy = cv2.findContours(
        dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤轮廓，只保留面积大于阈值的轮廓
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threhold:
            print(area)
            filtered_contours.append(contour)

    split_res = image.copy()

    # 提取图片区域
    extracted_images = []
    extracted_images_names = []
    extracted_images_coordinates = []
    for idx, contour in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(contour)

        # 调整坐标，考虑裁剪偏移
        x = x + offset_x
        y = y + offset_y

        # 提取并保存高分辨率图片
        extracted_images.append(zoomed_image[int(
            y * zoom_y):int((y + h) * zoom_y), int(x * zoom_x):int((x + w) * zoom_x)])
        extracted_images_coordinates.append(
            [int(y * zoom_y), int((y + h) * zoom_y), int(x * zoom_x), int((x + w) * zoom_x)])

        # 绘制最小外接矩形
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


def savePDFasImage(uploaded_file_name, page, page_img_save_dir):
    """
    将PDF页面保存为图像文件
    参数:
        uploaded_file_name: 上传的文件名
        page: PDF页面对象
        page_img_save_dir: 图片保存目录
    返回:
        page_image: 原始分辨率图像路径
        page_image_6x: 6倍分辨率图像路径
    """
    file_name = uploaded_file_name[:-4]
    # 生成6倍分辨率的图像
    zoom_x = 6.0
    zoom_y = 6.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    page_image_6x = "%s/%s-page-%i-%s.png" % (
        page_img_save_dir, file_name, page.number, '6x')
    pix.save(page_image_6x)

    # 生成原始分辨率的图像
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
    删除临时生成的PDF图像文件
    参数:
        page_image: 原始分辨率图像路径
        page_image_6x: 6倍分辨率图像路径
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


def detectyTextFromPDFPage(page_image, lang):
    """
    使用OCR从PDF页面图像中识别文本
    参数:
        page_image: 页面图像路径
        lang: 语言列表，如['ch_sim', 'en']
    返回:
        final_result: 识别出的文本内容
    """
    # 初始化OCR阅读器
    reader = easyocr.Reader(lang, gpu=True)
    # 使用OCR识别文本
    result = reader.readtext(page_image, paragraph=True,
                             rotation_info=[90, 180, 270])

    if lang[0] == 'ch_tra':
        print('ch_tra')
        # converter = opencc.OpenCC('t2s.json')

    filtered_results = []
    for (coordinate, text) in result:
        # 过滤 margin:
        # [[113, 393], [173, 393], [173, 1152], [113, 1152]] 鎌邕咄血虱蘚吊普癬8邕咄帶咄
        # [[3005, 4145], [3032, 4145], [3032, 4183], [3005, 4183]] 5
        # [2853, 119], [3066, 119], [3066, 180], [2853, 180]] 食器:鼎
        # print(coordinate, text)

        # 获取文本区域的坐标
        left = coordinate[0][0]
        right = coordinate[1][0]
        top = coordinate[0][1]
        bottom = coordinate[2][1]

        # 计算文本区域的宽度、高度和面积
        width = right - left
        height = bottom - top
        # 计算面积
        area = width * height

        # 过滤边缘文本和过小的文本区域
        if left <= 300 or right <= 300 or left >= 2800 or right >= 2800:
            print("passed text(coordinates): ", left,
                  right, top, bottom, "area: ", area, text)
            pass
        else:
            if (area <= 150000):
                print("passed text(area): ", left, right,
                      top, bottom, "area: ", area, text)
            else:
                print(left, right, top, bottom, "area: ", area, text)
                filtered_results.append(text)

    # 合并所有过滤后的文本
    final_result = ""
    for i in filtered_results:
        final_result += i

    print(final_result + '\n')
    return final_result


def set_json_init(file_name):
    """
    初始化JSON文件，检查已处理的页面
    参数:
        file_name: 文件名
    返回:
        existing_pages: 已处理页面的列表
    """
    global extractedPDFPath
    global existing_pages

    extractedPDFBasePath = os.path.join("app", "extracted_text")
    json_filename = file_name[:-4] + '.json'
    extractedPDFPath = os.path.join(extractedPDFBasePath, json_filename)

    try:
        # 如果JSON文件已存在，读取已处理的页面
        with open(extractedPDFPath, "r+") as file:
            existing_data = json.load(file)
            existing_pages = [item["page"] for item in existing_data]
            file.seek(0)
            content = file.read()
            new_content = content[:-1]

        with open(extractedPDFPath, "w") as file:
            file.write(new_content)
            file.write(",")

    except FileNotFoundError:
        # 如果文件不存在，创建新的JSON文件
        with open(extractedPDFPath, "w") as file:
            file.write("[")
    return existing_pages


def preprocessFile():
    """
    主函数，处理PDF文件的预处理流程
    返回:
        "success": 处理成功
    """
    # 记录开始时间
    start_time = time.time()
    print("start_time: ", start_time)

    # 打开PDF文件
    doc = fitz.open(uploaded_file_path)

    # 初始化变量
    pageImgList = []
    startPageNum = int(pageNum) - 1  # 转换为0-based索引
    endPageNum = int(endPageNum) - 1  # 转换为0-based索引

    thisPageImgList = []
    savedText = ''
    savedPageNum = startPageNum + 1
    current_page_number = startPageNum

    # 设置图片保存路径
    loadedImgsBasePath = os.path.join("app", "loadedImgs")
    pdfImgsBasePath = os.path.join("app", "pdf_image")

    # 初始化JSON文件
    existing_pages = set_json_init(uploaded_file_name)

    # 处理每一页
    for page in doc.pages(startPageNum, endPageNum, 1):
        current_page_number += 1

        if current_page_number not in existing_pages:
            print(f"正在处理第 {current_page_number + 1} 页")  # 显示1-based页码
            # 保存PDF页面为图像
            page_image, page_image_6x = savePDFasImage(
                uploaded_file_name, page, pdfImgsBasePath)
            type = 0
            if type == 0:
                # 识别文本
                text = detectyTextFromPDFPage(page_image_6x, lang)
                # 检测并提取图片
                extracted_images_names, extracted_images_coordinates = detectImgFromPDFPage(uploaded_file_name,
                                                                                            page,
                                                                                            page_image,
                                                                                            page_image_6x,
                                                                                            loadedImgsBasePath)
                # 处理图片列表
                newPageImgList = []
                for extracted_images_name in extracted_images_names:
                    newPageImgList.append(
                        "app/loadedImgs/" + extracted_images_name)

                # 处理文本和图片的关联关系
                savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList, ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum = catalog_many_to_one(
                    savedPageNum, savedText, text, thisPageImgList, newPageImgList, current_page_number, startPageNum, endPageNum)

                # 保存处理结果
                if ifSaved:
                    save_text_and_related_img_to_json(uploaded_file_name, returnSavedPageNum, [
                                                      returnText], returnImgList)
                if ifLastPage:
                    save_text_and_related_img_to_json(uploaded_file_name, returnLastSavedPageNum,
                                                      [returnLastText], returnLastImgList)

            # 删除临时图像文件
            deletePDFImage(page_image, page_image_6x)

    # 完成JSON文件的格式
    set_json_ending()

    # 计算并输出处理时间
    end_time = time.time()
    print("end_time: ", end_time)
    elapsed_time = end_time - start_time
    print(f"总处理时间: {elapsed_time} 秒")
    print(f"处理页面范围: 第 {pageNum} 页到第 {endPageNum} 页")
    print(f"使用语言: {'简体中文' if isChSim else '繁体中文'}")

    return "success"


if __name__ == '__main__':
    result = preprocessFile()
    print(result)
