"""
多模态数据绑定模块
用于处理文本和图片之间的关联关系，支持多种绑定模式
"""

# ==================== 一对一绑定函数 ====================


def catalog_one_to_one(text, thisPageImgList):
    """
    一对一绑定模式：每个文本对应一个图片列表

    功能说明：
    1. 保持文本和图片列表的一一对应关系
    2. 返回新的图片列表（当前为空实现）

    @param text: 当前页面的文本内容
    @param thisPageImgList: 当前页面的图片列表
    @return: (文本, 原图片列表, 新图片列表)
    """
    newThisPageImgList = []
    return text, thisPageImgList, newThisPageImgList

# ==================== 坐标匹配绑定函数 ====================


def pairImagetoText(extracted_text_list, img_list, img_coordinates_list):
    """
    基于坐标的图片-文本匹配

    功能说明：
    1. 根据文本和图片的坐标信息进行匹配
    2. 将图片关联到对应的文本上
    3. 支持一个文本对应多个图片的情况

    @param extracted_text_list: 提取的文本列表，包含坐标信息
    @param img_list: 图片列表
    @param img_coordinates_list: 图片坐标列表
    @return: (文本列表, 图片列表)
    """
    textList = []
    imgList = []

    # 遍历每个文本及其坐标
    for (text_coordinate, text) in extracted_text_list:
        thisTextImgList = []
        ifTextListAppend = False

        # 遍历每个图片及其坐标
        for img, img_coordinate in zip(img_list, img_coordinates_list):
            # 检查文本和图片的垂直位置关系
            # 如果文本在图片下方50像素范围内，则认为它们相关
            if (text_coordinate[0][1] - int(img_coordinate[1])) <= 50 and (text_coordinate[0][1] - int(img_coordinate[1])) >= 0:
                if not ifTextListAppend:  # 新的文本
                    textList.append(text)
                    ifTextListAppend = True
                thisTextImgList.append(img)

        if ifTextListAppend:
            imgList.append(thisTextImgList)

    return textList, imgList

# ==================== 多对一绑定函数 ====================


def catalog_many_to_one(savedPageNum, savedText, text, thisPageImgList, newPageImgList, current_page_number, startPageNum, endPageNum):
    """
    多对一绑定模式：多个页面内容对应一个数据点

    功能说明：
    1. 处理跨页面的内容关联
    2. 支持内容暂存和提交
    3. 处理最后一页的特殊情况

    @param savedPageNum: 已保存的页面编号
    @param savedText: 已保存的文本内容
    @param text: 当前页面的文本内容
    @param thisPageImgList: 当前页面的图片列表
    @param newPageImgList: 新页面的图片列表
    @param current_page_number: 当前页面编号
    @param startPageNum: 起始页面编号
    @param endPageNum: 结束页面编号
    @return: (保存的页面编号, 保存的文本, 当前页面图片列表, 是否已保存, 
             返回的保存页面编号, 返回的文本, 返回的图片列表, 是否是最后一页,
             最后一页的文本, 最后一页的图片列表, 最后一页的保存编号)
    """
    # 初始化返回值
    returnText = ''
    returnLastText = ''
    returnImgList = []
    returnLastImgList = []
    returnSavedPageNum = -1
    returnLastSavedPageNum = -1
    ifSaved = False
    ifLastPage = False

    # 处理当前页面内容
    if text == '':
        # 如果当前页面没有文本，将新图片添加到现有图片列表中
        for img in newPageImgList:
            thisPageImgList.append(img)
    else:
        # 如果当前页面有文本 (如果检测到新的内容，则把之前的尽数提交并且更新暂存项)
        if current_page_number != (startPageNum + 1):
            # 非第一页：提交之前的内容，更新暂存项
            ifSaved = True
            returnText = savedText
            savedText = text
            returnSavedPageNum = savedPageNum
            savedPageNum = current_page_number
            returnImgList = thisPageImgList
            thisPageImgList = newPageImgList
        else:
            # 第一页：直接更新暂存项
            savedText = text
            savedPageNum = current_page_number
            thisPageImgList = newPageImgList

    # 处理最后一页的特殊情况
    if current_page_number == endPageNum:
        if text == '':
            # 最后一页且没有新内容：提交所有暂存内容
            ifSaved = True
            returnText = savedText
            returnSavedPageNum = savedPageNum
            savedText = ''
            returnImgList = thisPageImgList
            thisPageImgList = []
        else:
            # 最后一页且有新内容：标记为最后一页内容
            ifLastPage = True
            returnLastText = text
            returnLastImgList = newPageImgList
            returnLastSavedPageNum = current_page_number

    return (savedPageNum, savedText, thisPageImgList, ifSaved,
            returnSavedPageNum, returnText, returnImgList, ifLastPage,
            returnLastText, returnLastImgList, returnLastSavedPageNum)
