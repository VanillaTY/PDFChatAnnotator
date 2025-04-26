"""
JSON 文件处理模块
用于处理 PDF 文本和图片数据的 JSON 存储
"""

# ==================== 导入语句 ====================

# Django 相关导入
from django.conf import settings

# 标准库导入
import os
import json

# ==================== 全局变量 ====================

# JSON 文件路径
extractedPDFPath = ''

# 已处理的页面列表
existing_pages = []

# ==================== 函数定义 ====================


def set_json_init(file_name):
    """
    初始化 JSON 文件并获取已处理的页面列表

    功能说明：
    1. 设置 JSON 文件路径
    2. 读取已存在的 JSON 文件内容
    3. 提取已处理的页面列表
    4. 准备文件以进行后续写入

    @param file_name: PDF 文件名
    @return: 已处理的页面列表
    """
    global extractedPDFPath
    global existing_pages

    # 设置 JSON 文件路径
    extractedPDFBasePath = os.path.join(os.path.join(
        settings.STATICFILES_DIRS[0], "app"), "extracted_text")
    json_filename = file_name[:-4] + '.json'
    print(json_filename)
    extractedPDFPath = os.path.join(extractedPDFBasePath, json_filename)

    try:
        # 读取已存在的 JSON 文件
        with open(extractedPDFPath, "r+") as file:
            # 获取已处理的页面列表
            existing_data = json.load(file)
            existing_pages = [item["page"] for item in existing_data]
            print(existing_pages)

            # 将文件指针移回文件开头
            file.seek(0)
            content = file.read()
            new_content = content[:-1]

        # 准备文件以进行后续写入
        with open(extractedPDFPath, "w") as file:
            file.write(new_content)
            file.write(",")

    except FileNotFoundError:
        # 如果文件不存在，创建新文件
        with open(extractedPDFPath, "w") as file:
            file.write("[")
            existing_pages = [-1]

    return existing_pages


def save_text_and_related_img_to_json(file_name, current_page_number, textList, relatedImgList):
    """
    将文本和相关的图片列表保存到 JSON 文件

    功能说明：
    1. 构建数据字典
    2. 将数据追加到 JSON 文件

    @param file_name: PDF 文件名
    @param current_page_number: 当前页码
    @param textList: 文本列表
    @param relatedImgList: 相关的图片列表
    """
    # 构建数据字典
    data = {
        "file_name": file_name,
        "page": current_page_number,
        "textList": textList,
        "thisTextImgList": relatedImgList,
    }

    # 将数据追加到 JSON 文件
    with open(extractedPDFPath, "a") as json_file:
        json.dump(data, json_file, ensure_ascii=False)
        json_file.write(",")


def set_json_ending():
    """
    完成 JSON 文件的写入

    功能说明：
    1. 读取文件内容
    2. 删除最后一个逗号
    3. 添加结束方括号
    """
    # 读取文件内容
    with open(extractedPDFPath, "r") as json_file:
        content = json_file.read()

    # 删除最后一个字符（逗号）
    if content:
        content = content[:-1]

    # 添加结束方括号并写入文件
    with open(extractedPDFPath, "w") as json_file:
        json_file.write(content + "]")
