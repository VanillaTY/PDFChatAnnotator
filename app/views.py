"""
PDF Chat Annotator 视图模块
处理 PDF 聊天标注器的所有视图函数
"""

# ==================== 导入语句 ====================

# Django 相关导入
from django.http import HttpResponse, QueryDict
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# 第三方库导入
import fitz
import os
import re
import json
from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache

# 本地模块导入
from app import models
from utils import info_extract, prompt, multimodel_binding, save_text_json
from utils.excel_storage import ExcelStorage

# ==================== 全局变量 ====================

# 目录配置
base_dir = settings.BASE_DIR
pdf_store_dir = os.path.join(base_dir, 'pdfFiles')

# 图像处理路径
source_folder = os.path.join(os.path.join(
    settings.STATICFILES_DIRS[0], "app"), "loadedImgs/")
destination_folder = os.path.join(os.path.join(
    settings.STATICFILES_DIRS[0], "app"), "dataset/")

# Initialize Excel storage if not using MySQL
if not settings.USE_MYSQL:
    excel_storage = ExcelStorage()

# ==================== 工具函数 ====================


def extract_dicts(string):
    """
    从包含多个字典模式的字符串中提取字典
    @param string: 包含字典模式的输入字符串
    @return: 提取的字典列表
    """
    pattern = re.compile(r'\{(.+?)\}')  # 匹配大括号{}内的内容
    matches = pattern.findall(string)  # 查找所有匹配项
    dictionaries = []  # 存储解析后的字典

    for match in matches:
        dict_str = "{" + match + "}"  # 匹配到的字符串转换成字典格式
        dictionary = eval(dict_str)  # eval函数将字符串转换成字典
        dictionaries.append(dictionary)

    return dictionaries


def is_string(obj):
    """
    检查对象是否为字符串或将其转换为字符串
    @param obj: 要检查的对象
    @return: 如果是字符串返回True，否则返回字符串表示
    """
    if isinstance(obj, str):
        return True
    else:
        return str(obj)


def copy_specific_png_image(source_folder, image_filename, destination_folder):
    """
    将特定的PNG图片从源文件夹复制到目标文件夹
    @param source_folder: 源目录路径
    @param image_filename: 图片文件名
    @param destination_folder: 目标目录路径
    """
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 构建源图片文件的完整路径
    source_path = os.path.join(source_folder, image_filename)

    # 构建目标图片文件的完整路径
    destination_path = os.path.join(destination_folder, image_filename)

    # 打开源图片文件和目标图片文件，并复制数据
    with open(source_path, 'rb') as source_file:
        with open(destination_path, 'wb') as destination_file:
            destination_file.write(source_file.read())

# ==================== 视图函数 ====================


def index(request):
    """
    主索引视图函数
    @param request: HTTP请求对象
    @return: 渲染的索引模板
    """
    template = loader.get_template('app/index.html')
    info = 'This is information. '
    context = {
        'info': info,
    }
    return render(request, 'app/index.html', context)


@csrf_exempt
def submitCard(request):
    """
    处理卡片提交，包含标签和图片
    @param request: 包含标签列表和图片列表的HTTP请求对象
    @return: 包含状态的JSON响应
    """
    try:
        query_dict = json.loads(request.POST.get('labelLists'))
        img_lists = request.POST.getlist('ImgLists[]')

        for img in img_lists:
            labelNames = {}
            attributes = {}
            attributes['imgName'] = img

            image_filename = img
            try:
                copy_specific_png_image(
                    source_folder, image_filename, destination_folder)
            except Exception as e:
                print(f"Error copying image: {str(e)}")
                return HttpResponse(json.dumps({"status": False, "error": "Failed to copy image"}))

            for index, key in enumerate(query_dict.keys(), start=1):
                value = query_dict[key]
                labelNames['labelName' + str(index)] = key
                attributes['label' + str(index)] = value

            # 保存到数据库或Excel
            try:
                if settings.USE_MYSQL:
                    models.LabelLists.objects.create(**attributes)
                    models.LabelName.objects.create(**labelNames)
                else:
                    excel_storage.save_label_list(**attributes)
                    excel_storage.save_label_name(**labelNames)
            except Exception as e:
                print(f"Error saving data: {str(e)}")
                return HttpResponse(json.dumps({"status": False, "error": "Failed to save data"}))

        return HttpResponse(json.dumps({"status": True}))
    except Exception as e:
        print(f"General error in submitCard: {str(e)}")
        return HttpResponse(json.dumps({"status": False, "error": "An unexpected error occurred"}))


@csrf_exempt
def fileHandle(request):
    """
    处理PDF文件上传和处理
    支持多种处理类型(0, 1, 2, 4)用于不同的文本-图片绑定策略

    处理类型说明：
    type 0: 默认处理方式，结合了 type 1 和 type 4 的特点
        - 可以处理一页文字对应多页图片的情况
        - 也可以处理一页文字对应一页图片的情况

    type 1: 一页文字对应一页图片 (one to one)
        - 一页的文字关联这页的所有图片
        - 适用于每页内容独立的情况
        - 文字和图片在同一页内进行绑定

    type 2: 一页多数据对应 (one to many)
        - 一页有多个数据，图片下面是对应的文字
        - 根据坐标绑定图片和文字
        - 适用于图片和文字有明确位置关系的情况

    type 4: 多页内容对应一个数据 (many to one)
        - 多页内容对应一个数据
        - 如果检测到新的字，则把之前的图片都与之前的字绑定
        - 适用于跨页内容关联的情况

    @param request: 包含PDF文件的HTTP请求对象
    @return: 包含处理状态的JSON响应
    """
    print(request)
    print('start process file')
    uploaded_file = request.FILES.get('file')
    uploaded_file_name = uploaded_file.name
    print(uploaded_file.name)

    # 处理文件存储
    if uploaded_file is not None:
        if not os.path.exists(os.path.join(pdf_store_dir, uploaded_file_name)):
            file_path = default_storage.save(os.path.join(
                pdf_store_dir, uploaded_file_name), uploaded_file)
        else:
            file_path = os.path.join(pdf_store_dir, uploaded_file_name)
    else:
        file_path = os.path.join(pdf_store_dir, 'temp.pdf')

    # 处理PDF文件
    doc = fitz.open(file_path)
    pageImgList = []

    # 获取处理参数
    pageNum = request.POST.get('pageNum')
    lang = request.POST.get('lang').split(',')
    print(lang)
    extractedPageLength = int(request.POST.get('pageLength'))

    # 计算页面范围
    startPageNum = int(pageNum) - 1
    endPageNum = int(pageNum) + extractedPageLength - 1

    # 初始化处理变量
    thisPageImgList = []
    savedText = ''
    savedPageNum = startPageNum + 1
    current_page_number = startPageNum  # 当前页码

    # 设置路径
    loadedImgsBasePath = os.path.join(os.path.join(
        settings.STATICFILES_DIRS[0], "app"), "loadedImgs")
    pdfImgsBasePath = os.path.join(os.path.join(
        settings.STATICFILES_DIRS[0], "app"), "pdf_image")

    # 处理每个页面
    existing_pages = save_text_json.set_json_init(uploaded_file.name)
    print(existing_pages)

    for page in doc.pages(startPageNum, endPageNum, 1):
        current_page_number += 1
        if existing_pages[0] > current_page_number or current_page_number > existing_pages[-1]:
            print(current_page_number)
            page_image, page_image_6x = info_extract.savePDFasImage(
                uploaded_file_name, page, pdfImgsBasePath)
            type = 0  # 处理类型可以根据需要修改

            if type == 1:
                # type 1: one to one 一页的文字关联这页的所有图片
                text = info_extract.detectyTextFromPDFPage_Type1(page_image_6x)
                # 读取并保存这页图片
                extracted_images_names, extracted_images_coordinates = info_extract.detectImgFromPDFPage(
                    uploaded_file_name, page, page_image, page_image_6x, loadedImgsBasePath)

                for extracted_images_name in extracted_images_names:
                    thisPageImgList.append(
                        "app/loadedImgs/" + extracted_images_name)

                # multimodel binding
                text, save_img, thisPageImgList = multimodel_binding.catalog_one_to_one(
                    text, thisPageImgList)
                save_text_json.save_text_and_related_img_to_json(
                    uploaded_file_name, current_page_number, [text], save_img)
                pageImgList.append(save_img)

            elif type == 2:
                # type 2: one to many 一页有多个数据，图片下面是对应的文字，根据坐标绑定图片和文字
                extracted_images_names, extracted_images_coordinates = info_extract.detectImgFromPDFPage(
                    uploaded_file_name, page, page_image, page_image_6x, loadedImgsBasePath, 50000)
                extracted_text = info_extract.detectyTextFromPDFPage_Type2(
                    page_image_6x)

                textList, relatedImgList = multimodel_binding.pairImagetoText(
                    extracted_text, extracted_images_names, extracted_images_coordinates)

                for text, relatedImges in zip(textList, relatedImgList):
                    pageImgList.append(relatedImges)
                    save_text_json.save_text_and_related_img_to_json(
                        uploaded_file_name, current_page_number, [text], relatedImges)

            elif type == 4:
                # type 4: many to one 多页内容对应一个数据，如果检测到新的字，则把之前的图片都与之前的字绑定
                text = info_extract.detectyTextFromPDFPage_Type4(page_image_6x)
                # 读取并保存这页图片
                extracted_images_names, extracted_images_coordinates = info_extract.detectImgFromPDFPage(
                    uploaded_file_name, page, page_image, page_image_6x, loadedImgsBasePath)

                newPageImgList = []
                for extracted_images_name in extracted_images_names:
                    newPageImgList.append(
                        "app/loadedImgs/" + extracted_images_name)

                # multimodel binding
                savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList, ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum = multimodel_binding.catalog_many_to_one(
                    savedPageNum, savedText, text, thisPageImgList, newPageImgList, current_page_number, startPageNum, endPageNum)
                print('--------------------------------------')
                print(savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList,
                      ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum)

                if ifSaved:
                    print(1)
                    save_text_json.save_text_and_related_img_to_json(
                        uploaded_file_name, returnSavedPageNum, [returnText], returnImgList)
                if ifLastPage:
                    print(2)
                    save_text_json.save_text_and_related_img_to_json(
                        uploaded_file_name, returnLastSavedPageNum, [returnLastText], returnLastImgList)
                print('--------------------------------------')

            elif type == 0:
                # type 0: type 1 + type 4 都适用
                # 检测并返回过滤掉的文本
                text = info_extract.detectyTextFromPDFPage(page_image_6x, lang)
                # 读取并保存这页图片
                extracted_images_names, extracted_images_coordinates = info_extract.detectImgFromPDFPage(
                    uploaded_file_name, page, page_image, page_image_6x, loadedImgsBasePath)

                newPageImgList = []
                for extracted_images_name in extracted_images_names:
                    newPageImgList.append(
                        "app/loadedImgs/" + extracted_images_name)

                # multimodel binding
                savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList, ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum = multimodel_binding.catalog_many_to_one(
                    savedPageNum, savedText, text, thisPageImgList, newPageImgList, current_page_number, startPageNum, endPageNum)
                print('--------------------------------------')
                print(savedPageNum, savedText, thisPageImgList, ifSaved, returnSavedPageNum, returnText, returnImgList,
                      ifLastPage, returnLastText, returnLastImgList, returnLastSavedPageNum)

                if ifSaved:
                    print(1)
                    save_text_json.save_text_and_related_img_to_json(
                        uploaded_file_name, returnSavedPageNum, [returnText], returnImgList)
                if ifLastPage:
                    print(2)
                    save_text_json.save_text_and_related_img_to_json(
                        uploaded_file_name, returnLastSavedPageNum, [returnLastText], returnLastImgList)
                print('--------------------------------------')

            # 清理临时文件
            info_extract.deletePDFImage(page_image, page_image_6x)

    save_text_json.set_json_ending()
    res_dic = {"status": True}
    return HttpResponse(json.dumps(res_dic))


@csrf_exempt
def receiveMessage(request):
    """
    处理消息接收和处理
    @param request: 包含消息的HTTP请求对象
    @return: 包含处理结果的JSON响应
    """
    askMessage = request.POST.get('message')
    examplesPropmt = request.POST.get('prompt')

    # 设置路径并加载数据
    extractedPDFBasePath = os.path.join(os.path.join(
        settings.STATICFILES_DIRS[0], "app"), "extracted_text")
    json_filename = request.POST.get('filename')[:-4] + '.json'
    extractedPDFPath = os.path.join(extractedPDFBasePath, json_filename)

    # 使用缓存机制
    cache_key = f"pdf_data_{json_filename}"
    data = cache.get(cache_key)
    if data is None:
        with open(extractedPDFPath, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            cache.set(cache_key, data, timeout=3600)  # 缓存1小时

    # 处理页面范围
    pageNum = int(request.POST.get('pageNum'))
    extractedPageLength = int(request.POST.get('pageLength'))
    startPageNum = pageNum
    endPageNum = pageNum + extractedPageLength

    # 使用列表推导式优化数据过滤
    target_pages_data = [
        item for item in data
        if startPageNum <= item.get('page', 0) < endPageNum
    ]
    print("target_pages_data", target_pages_data)
    # 批量处理文本
    texts_to_process = []
    for item in target_pages_data:
        texts_to_process.extend([
            (text, item.get('thisTextImgList'))
            for text in item.get('textList', [])
        ])

    # 批量调用 GPT API
    modelOutputs = []
    exampleTextList = []
    imgList = []

    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for text, img_list in texts_to_process:
            futures.append(
                executor.submit(
                    prompt.askGPT,
                    askMessage,
                    text,
                    examplesPropmt
                )
            )
            imgList.append(img_list)

        for future in futures:
            modelOutput, exampleText = future.result()
            modelOutputs.append(modelOutput)
            exampleTextList.append(exampleText)
    print("modelOutputs", modelOutputs)
    # 准备并返回响应
    res_dic = {
        "status": True,
        "modelOutputs": modelOutputs,
        "exampleTextList": exampleTextList,
        "imgList": imgList,
    }
    return HttpResponse(json.dumps(res_dic))
