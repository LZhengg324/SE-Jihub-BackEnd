import json
import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from myApp.models import Group, User, Message, UserGroup

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # get roomid from websocket request url kwargs
        self.room_id = int(self.scope['url_route']['kwargs']['roomId'])
        self.room = Group.objects.get(id = self.room_id)
        self.room_group_name = 'char_room_%s' % self.room_id

        # get userId from websocket request url
        self.user_id = int(self.scope['url_route']['kwargs']['userId'])

        # join room group
        async_to_sync(self.channel_layer.group_add) (
            self.room_group_name, self.channel_name
        )

        # accept the connect request
        self.accept()

    def disconnect(self, code):
        # disconnect the websocket connection
        async_to_sync(self.channel_layer.group_discard) (
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        assert text_data is not None
        # read the message from webcokect scope['text']['message']
        ws_json_data = json.loads(text_data)
<<<<<<< HEAD
        message_content, send_user_id = str(ws_json_data['message']), int(ws_json_data['sender'])

        send_user = User.objects.get(id = send_user_id)
        send_time = datetime.datetime.now()
        # generate the message for all users in this room,
        # and flag these messages' unchecking status.
        for association in UserGroup.objects.filter(group_id = self.room.id):
            check_status = 'UC'
            if association.user.id == send_user_id:
                check_status = 'C'
            message = Message(
                type = 'A',
                status = check_status,
                content = message_content,
                time = send_time,
                group_id = self.room,
                send_user = send_user,
                receive_user = association.user
=======
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
>>>>>>> d7c7adb542bed10bc9e583ab7065578243a00b89
            )
            message.save()

        # send the message to others in this room.
        async_to_sync(self.channel_layer.group_send) (
            self.room_group_name, {
                'type': 'chat_message',
                'send_user_name': send_user.name,
                'send_user_id': send_user.id,
                'message': message_content,
                'send_time': send_time,
            }
        )

    def chat_message(self, event):

        # set the message status to 'checked'
<<<<<<< HEAD
        for message in Message.objects.filter(time = send_time):
            if message.receive_user.id == self.user_id:
                message.status = 'C'
                message.save()
                break
=======
        for message in Message.objects.filter(receive_user=self.userId, group_id=self.groupId, status='UC'):
            message.status = 'C'
            message.save()
>>>>>>> d7c7adb542bed10bc9e583ab7065578243a00b89

        # send message to client
        self.send(text_data=json.dumps({
            'content': event['message'],
            'senderName': event['send_user_name'],
            'senderId': event['send_user_id'],
            'time': str(event['send_time'])
        }))




