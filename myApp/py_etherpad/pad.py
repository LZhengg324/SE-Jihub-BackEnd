import base64
import json
import time

from djangoProject.settings import response_json
from myApp.models import *
import py_etherpad
import random
from django.db.models import signals
from django.dispatch import receiver
from urllib.parse import quote

apiKey = "bcc011026cfdfad733eb9f7993b6f5c3317a80bc643603bd53bd378215a5944e"
baseUrl = "http://122.9.40.159:9001/"
apiUrl = baseUrl + "api"
ep_client = py_etherpad.EtherpadLiteClient(apiKey=apiKey, baseUrl=apiUrl)


def createPad(request):
    kwargs: dict = json.loads(request.body)
    projectId = int(kwargs.get('projectId'))
    name = str(kwargs.get('name'))
    userId = str(kwargs.get('userId'))
    info = ""
    if 'info' in kwargs:
        info = str(kwargs.get('info'))

    token = str(random.randint(0, 100)) + str(time.time()).replace('.', '')[3:] + str(random.randint(0, 100))

    project = Project.objects.get(id=projectId)
    try:
        ep_client.createPad(padID=token)
    except:
        return response_json(
            errcode=1,
            message="Failed!Please Try Again."
        )
    pad = Pad.objects.create(name=name, token=token, project=project, info=info)

    UserPad.objects.create(user=User.objects.get(id=userId), pad=pad, color=genColor(), role='A')

    return response_json(
        errcode=0,
        data={
            'token': pad.token,
            'name': pad.name,
            'info': pad.info
        }
    )


def deletePad(request):
    kwargs: dict = json.loads(request.body)
    token = str(kwargs.get('token'))
    userId = str(kwargs.get('userId'))
    pads = Pad.objects.filter(token=token)
    if pads.exists():
        if UserPad.objects.filter(user=userId, pad=pads.first()).exists():
            session = UserPad.objects.filter(user=userId, pad=pads.first()).first()
            if session.role == 'A':
                pad = pads.first()
                pad.delete()
                return response_json(errcode=0)
            else:
                return response_json(
                    errcode=1,
                    message="No Permission, Only Creator can Delete the Pad!"
                )
        else:
            return response_json(
                errcode=1,
                message="No Permission, Only Creator can Delete the Pad!"
            )
    return response_json(
        errcode=0
    )


def enterPad(request):
    kwargs: dict = json.loads(request.body)
    token = str(kwargs.get('token'))
    userId = int(kwargs.get('userId'))
    pad = Pad.objects.get(token=token)
    user = User.objects.get(id=userId)

    sessions = UserPad.objects.filter(pad=pad, user=user)
    color = genColor()
    if sessions.exists():
        session = sessions.first()
        color = session.color
    else:
        UserPad.objects.create(pad=pad, user=user, color=color, role='B')
    padUrl = baseUrl + "p/" + token + "?" + "userName=" + user.name + "&userColor=" + color
    return response_json(
        errcode=0,
        data={
            'padUrl': padUrl
        }
    )


def getPads(request):
    kwargs: dict = json.loads(request.body)
    projectId = int(kwargs.get('projectId'))
    pads = Pad.objects.filter(project=projectId)
    rets = []
    for pad in pads:
        rets.append({
            'name': pad.name,
            'token': pad.token,
            'info': pad.info,
            'creatorId': UserPad.objects.filter(pad=pad).first().user.id,
            'creatorName': UserPad.objects.filter(pad=pad).first().user.name
        })
    return response_json(
        errcode=0,
        data={
            'pads': rets
        }
    )


def favorPad(request):
    kwargs: dict = json.loads(request.body)
    userId = int(kwargs.get('userId'))
    token = str(kwargs.get('token'))
    users = User.objects.filter(id=userId)
    if users.exists():
        user = users.first()
    else:
        return response_json(
            errcode=1,
            message="User not exist!"
        )
    pads = Pad.objects.filter(token=token)
    if pads.exists():
        pad = pads.first()
    else:
        return response_json(
            errcode=2,
            message="Pad not exist!"
        )

    if UserFavorPad.objects.filter(user=user, pad=pad).exists():
        return response_json(
            errcode=3,
            message="You have favored the pad!"
        )
    else:
        UserFavorPad.objects.create(user=user, pad=pad)
    return response_json(errcode=0)


def unFavorPad(request):
    kwargs: dict = json.loads(request.body)
    userId = int(kwargs.get('userId'))
    token = str(kwargs.get('token'))
    users = User.objects.filter(id=userId)
    if users.exists():
        user = users.first()
    else:
        return response_json(
            errcode=1,
            message="User not exist!"
        )
    pads = Pad.objects.filter(token=token)
    if pads.exists():
        pad = pads.first()
    else:
        return response_json(
            errcode=2,
            message="Pad not exist!"
        )

    if not UserFavorPad.objects.filter(user=user, pad=pad).exists():
        return response_json(
            errcode=3,
            message="You haven't favored the pad!"
        )
    else:
        UserFavorPad.objects.filter(user=user, pad=pad).first().delete()
    return response_json(errcode=0)


def getFavorPads(request):
    kwargs: dict = json.loads(request.body)
    userId = int(kwargs.get('userId'))
    projectId = int(kwargs.get('projectId'))
    favors = UserFavorPad.objects.filter(user=userId)
    pads = []
    for favor in favors:
        pad = favor.pad
        if pad.project.id == projectId:
            pads.append({
                'name': pad.name,
                'token': pad.token,
                'info': pad.info,
                'creatorId': UserPad.objects.filter(pad=pad).first().user.id,
                'creatorName': UserPad.objects.filter(pad=pad).first().user.name
            })
    return response_json(
        errcode=0,
        data={
            'pads': pads
        }
    )


def genColor():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "%23" + color


@receiver(signals.post_delete, sender=Pad)
def post_delete_pad(sender, instance, **kwargs):
    pad = instance
    token = pad.token
    ep_client.deletePad(token)

# if __name__ == '__main__':
#     import subprocess
#
#     # 定义cURL命令
#     curl_command = "curl --request POST --url 'http://localhost:9001/oidc/token' --header 'content-type: application/x-www-form-urlencoded' --data grant_type=client_credentials --data client_id=client_credentials --data client_secret=client_credentials"
#
#     # 执行cURL命令并获取输出
#     output = subprocess.check_output(curl_command, shell=True)
#
#     # 将输出转换为字符串
#     output = output.decode('utf-8')
#
#     # 打印输出
#     print(output)
