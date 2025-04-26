"""
GPT 提示词处理模块
用于处理与 GPT 模型的交互，包括提示词构建和响应解析
"""

# ==================== 导入语句 ====================

# 标准库导入
import ast
import re

# 第三方库导入
from openai import OpenAI

# ==================== 工具函数 ====================


def extract_dicts(string):
    """
    从字符串中提取字典格式的内容

    功能说明：
    1. 使用正则表达式匹配大括号内的内容
    2. 将匹配到的内容转换为字典
    3. 处理可能的解析错误

    @param string: 包含字典格式的字符串
    @return: 提取的字典列表
    """
    pattern = re.compile(r'\{(.+?)\}')  # 匹配大括号{}内的内容
    matches = pattern.findall(string)  # 查找所有匹配项
    dictionaries = []  # 存储解析后的字典

    for match in matches:
        dict_str = "{" + match + "}"  # 匹配到的字符串转换成字典格式
        try:
            # 使用ast.literal_eval解析字符串成字典
            dictionary = ast.literal_eval(dict_str)
            if isinstance(dictionary, dict):
                dictionaries.append(dictionary)
        except (ValueError, SyntaxError):
            dictionaries.append("{error: error}")
            pass

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

# ==================== GPT 交互函数 ====================


def askGPT(question, text, examplesPropmt):
    """
    向 GPT 模型发送问题并获取回答
    @param question: 用户问题
    @param text: 待处理的文本
    @param examplesPropmt: 示例提示词
    @return: 模型输出和示例文本
    """
    # 构建提示词模板
    prompt_template = """
    请根据提供的文本描述，以Python字典格式回答问题。请确保返回的是有效的Python字典格式。

    示例1：
    文本片段：
    '鬲 商代早期 通高21.4 .口径15.4厘米 1972年出土于陕酉省宝鸡市岐山县京当乡商代铜器窖藏 ,现藏于宝鸡青铜器博物院。 索状耳 ,斜沿外折 ,分裆,袋状足下接实足根 。口沿下饰一周以联珠纹为界隔的云纹 ,袋足饰大三角纹。'
    
    问题：'请提取出名称、时代、出土地。'
    
    回答：
    {{
        '名称': '鬲',
        '时代': '商代早期',
        '出土地': '陕西省宝鸡市'
    }}

    更多示例：
    {examplesPropmt}

    注意：
    1. 返回格式必须是Python字典
    2. 字典键使用中文
    3. 确保返回的是完整的字典结构
    4. 不要包含任何解释性文字
    5. 如果某个信息无法提取，使用空字符串作为值
    6. 不要包含任何代码块标记（如```python）

    现在，请处理以下文本：
    文本片段：
    '{text}'

    问题：'{question}'

    请以Python字典格式回答：
    """

    # 构建完整的提示词
    propmt = prompt_template.format(
        text=text,
        question=question,
        examplesPropmt=examplesPropmt if examplesPropmt else "（无额外示例）"
    )

    # 初始化 OpenAI 客户端
    client = OpenAI(
        # Replace with your own API key
        api_key="",
        base_url="https://api.chatanywhere.tech/v1"
    )

    # 调用 GPT API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
                "content": "你是一个专业的文本信息提取助手，请严格按照要求返回Python字典格式的答案。不要包含任何代码块标记。"},
            {"role": "user", "content": propmt}
        ],
        temperature=0.3,  # 降低随机性，提高准确性
        max_tokens=500
    )

    # 处理响应
    modelOutput = response.choices[0].message.content.strip()
    print("llm modelOutput", modelOutput)

    # 清理响应中的代码块标记
    modelOutput = modelOutput.replace(
        '```python', '').replace('```', '').strip()

    # 确保返回的是有效的Python字典
    try:
        # 尝试将响应解析为字典
        modelOutput = ast.literal_eval(modelOutput)
        print("modelOutput", modelOutput)
        if not isinstance(modelOutput, dict):
            raise ValueError("Response is not a dictionary")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing response as dictionary: {e}")
        # 如果解析失败，返回空字典
        modelOutput = {}

    # 构建示例文本
    exampleText = f"""
    文本片段：
    '{text}'
    
    问题：'{question}'
    """

    return modelOutput, exampleText

# ==================== 测试代码 ====================


if __name__ == '__main__':
    # 测试用例
    text = '爵 商代早期 通高22.4 .口径7.8厘米 1972年出土于陕酉省宝鸡市岐山县京当乡商代铜器窖藏 ,现藏于宝鸡青铜器博物院。 窄长流,尖尾;侈口,束腰,下腹外鼓,平底,三刀形足; 伞状单柱位于流口;腹部一侧有半环形 鏊。上下腹部各饰一周兽面纹5'
    askGPT("请提取出青铜器的名称", text, "")
