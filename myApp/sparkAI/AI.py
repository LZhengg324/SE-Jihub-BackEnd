# coding: utf-8
import json
import subprocess
import re
from urllib import request

import requests

import myApp.sparkAI.SparkApi as SparkApi
import time

from djangoProject.settings import response_json
from myApp.models import Repo

appid = "8c7f700a"  # 填写控制台中获取的 APPID 信息
api_secret = "OGQwMjI2MmRjNTY0ZjcxZWZlMGRlNmM5"  # 填写控制台中获取的 APISecret 信息
api_key = "2a4394a0d3316a4271dac8eb0c65ab04"  # 填写控制台中获取的 APIKey 信息
domain = "generalv3.5"
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

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
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)

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
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)

    return response_json(
        errcode=0,
        data={
            'content': SparkApi.answer
        }
    )

def PrDescriptionGen(request):
    kwargs: dict = json.loads(request.body)
    # branch = kwargs.get('branch')
    # repo_id = kwargs.get('repo_id')
    # repo = Repo.objects.get(id=repo_id)
    #
    # response={}
    # commit_detail = {}
    #
    # cmd = ("gh api repos/{}/commits?sha={} --jq '.[0].sha'".format(repo.remote_path, branch))
    # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # if result.returncode == 0:
    #     commit_sha = result.stdout.replace("\n", "")
    #     if result.returncode == 0:
    #         result = subprocess.run(f"gh api repos/{repo.remote_path}/commits/{commit_sha}", capture_output=True,
    #                                 shell=True, text=True)
    #         commit_detail = json.loads(result.stdout)
    #     else:
    #         response['errcode'] = 2
    #         response['errmsg'] = "get newest commit detail failed"
    # else:
    #     response['errcode'] = 1
    #     response['errmsg'] = "get newest commit sha failed"
    #
    #
    # files_changed = commit_detail['files']
    # diff = ""
    # for file in files_changed:
    #     if 'patch' in file:
    #         diff += file['filename'] + file['patch'] + "\n"
    diff = kwargs.get('diff')
    text = [
        {"role": "system", "content": "你现在扮演一位资深程序员"},
    ]
    Input = "请针对以下代码的改动部分用中文生成改动概述:\n" + diff
    question = checklen(getText(text, "user", Input))
    SparkApi.answer = ""
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)

    return response_json(
        errcode=0,
        data={
            'content': SparkApi.answer
        }
    )

def LabelGenerate(request):
    kwargs: dict  = json.loads(request.body)
    description = kwargs.get('description')
    text = [
        {"role": "system", "content": "你现在扮演一位秘书"}
    ]
    Input = "以下是任务的描述，从中提取关键字生成标签，直接输出并用中文逗号隔开，若无法提取标签则只输出null\n" + description
    # 这里有一些标签：1 ，2 ，3 ，4
    # 接下来给你一段任务描述，从上面的标签中选5个最合适的，输出标签用英文逗号隔开
    question = checklen(getText(text, "user", Input))
    SparkApi.answer = ""
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)

    tags = SparkApi.answer.split("，")
    pattern = re.compile(r'^标签：')
    tags_without_prefix = [pattern.sub('', tag) for tag in tags]
    tags_without_prefix = [tag.replace(" ", "") for tag in tags_without_prefix]
    tags_without_prefix = [tag.replace("null", "") for tag in tags_without_prefix]

    return response_json(
        errcode=0,
        data={
            'content': tags_without_prefix
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
    SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)

    print(SparkApi.answer)
