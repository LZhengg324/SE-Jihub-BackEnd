# coding: utf-8
import json

import myApp.sparkAI.SparkApi as SparkApi
import time

from djangoProject.settings import response_json


# 初始上下文内容，当前可传system、user、assistant 等角色
# text = [
#     {"role": "system", "content": "你现在扮演一位资深程序员"}  # 设置对话背景或者模型角色
#     # {"role": "user", "content": "你是谁"},  # 用户的历史问题
#     # {"role": "assistant", "content": "....."} , # AI的历史回答结果
#     # # ....... 省略的历史对话
#     # {"role": "user", "content": "你会做什么"}  # 最新的一条问题，如无需上下文，可只传最新一条问题
# ]


def getText(text, role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while getlength(text) > 8000:
        del text[0]
    return text


def UnitTest(request):
    kwargs: dict = json.loads(request.body)
    code = kwargs.get('code')
    text = [
        {"role": "system", "content": "你现在扮演一位资深程序员"},
    ]
    Input = "请针对以下代码生成单元测试代码:" + code
    question = checklen(getText(text, "user", Input))
    SparkApi.answer = ""
    SparkApi.main(1, question)

    return response_json(
        errcode=0,
        data={
            'content': SparkApi.answer
        }
    )


def CodeReview(request):
    kwargs: dict = json.loads(request.body)
    code = kwargs.get('code')
    text = [
        {"role": "system", "content": "你现在扮演一位资深程序员"},
    ]
    Input = "请针对以下代码进行代码分析:" + code
    question = checklen(getText(text, "user", Input))
    SparkApi.answer = ""
    SparkApi.main(1, question)

    return response_json(
        errcode=0,
        data={
            'content': SparkApi.answer
        }
    )


if __name__ == '__main__':
    code = input()
    text = [
        {"role": "system", "content": "你现在扮演一位资深程序员"},
    ]
    Input = "请针对以下代码进行代码分析:" + code
    question = checklen(getText(text, "user", Input))
    SparkApi.answer = ""
    SparkApi.main(1, question)

    print(SparkApi.answer)
