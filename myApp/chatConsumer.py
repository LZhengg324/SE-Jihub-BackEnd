import json
import datetime
from myApp.image import base64_to_img_name, get_img_url

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from myApp.models import Group, User, Message, UserGroup, Project


def resetUnReadNums(uid, gid):
    messages = Message.objects.filter(receive_user=uid, group_id=gid, status='UC')
    for message in messages:
        message.status = 'C'
        message.save()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.projectId = int(self.scope['url_route']['kwargs']['projectId'])
        self.project = Project.objects.get(id=self.projectId)
        self.projectName = 'project_%s' % self.projectId

        # get userId from websocket request url
        self.userId = int(self.scope['url_route']['kwargs']['userId'])
        self.groupId = 0

        # join room group
        async_to_sync(self.channel_layer.group_add)(
            self.projectName, self.channel_name
        )

        # accept the connect request
        self.accept()

    def disconnect(self, code):
        # disconnect the websocket connection
        async_to_sync(self.channel_layer.group_discard)(
            self.projectName, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        assert text_data is not None
        # read the message from webcokect scope['text']['message']
        ws_json_data = json.loads(text_data)
        type = int(ws_json_data['type'])

        if type == 1:
            roomId = int(ws_json_data['roomId'])
            self.groupId = roomId
            resetUnReadNums(self.userId, self.groupId)
            self.send(text_data=json.dumps({
                'type': 2
            }))

        elif type == 2:
            message_content = str(ws_json_data['mes'])
            message_type = str(ws_json_data['mes_type'])

            send_user = User.objects.get(id=self.userId)
            send_time = datetime.datetime.now()
            # generate the message for all users in this room,
            # and flag these messages' unchecking status.
            cnt = 0
            for association in UserGroup.objects.filter(group_id=self.groupId):
                check_status = 'UC'
                if association.user.id == self.userId:
                    check_status = 'C'

                if message_type == 'B' and cnt == 0:
                    img_name = base64_to_img_name(message_content)
                    message_content = img_name
                    cnt += 1

                Message.objects.create(
                    type=message_type,
                    status=check_status,
                    content=message_content,
                    time=send_time,
                    group_id=Group.objects.get(id=self.groupId),
                    send_user=send_user,
                    receive_user=association.user
                )


            group = Group.objects.get(id=self.groupId)
            group.time = send_time
            group.save()
            # send the message to others in this room.
            if message_type == 'B':
                message_content = get_img_url(message_content)
            async_to_sync(self.channel_layer.group_send)(
                self.projectName, {
                    'type': 'chat_message',
                    'send_user_name': send_user.name,
                    'send_user_id': send_user.id,
                    'message': message_content,
                    'send_time': send_time,
                    'message_type': message_type,
                    'group_id': self.groupId
                }
            )

        elif type == 3:
            async_to_sync(self.channel_layer.group_send)(
                self.projectName, {
                    'type': 'remind_all'
                }
            )
        else:
            print('error')

    def chat_message(self, event):

        # set the message status to 'checked'
        for message in Message.objects.filter(receive_user=self.userId, group_id=self.groupId, status='UC'):
            message.status = 'C'
            message.save()

        # send message to client
        if self.groupId == event['group_id']:
            self.send(text_data=json.dumps({
                'type': 1,
                'senderId': event['send_user_id'],
                'senderName': event['send_user_name'],
                'mes': event['message'],
                'mes_type': event['message_type'],
                'time': str(event['send_time'])
            }))

        if self.groupId != event['group_id']:
            self.send(text_data=json.dumps({
                'type': 2
            }))

    def remind_all(self):
        if not UserGroup.objects.filter(user=self.userId, group=self.groupId).exists():
            self.groupId = 0
        self.send(text_data=json.dumps({
            'type': 2
        }))
