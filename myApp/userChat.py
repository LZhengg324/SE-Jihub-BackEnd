from myApp.models import *
from djangoProject.settings import response_json
import json
from myApp.image import delete_img, get_img_url

SUCCESS = 0
ILLEGAL = 1


def get_room_content(request):
    kwargs: dict = json.loads(request.body)

    roomId = int(kwargs.get('roomId'))
    user = User.objects.get(id=int(kwargs.get('currentUserId')))

    messages = []
    for message in Message.objects.filter(group_id=roomId, receive_user=user):
        content = message.content
        if message.type == 'B':
            content = get_img_url(message.content)

        messages.append({'content': content,
                         'senderName': message.send_user.name,
                         'senderId': message.send_user.id,
                         'time': message.time,
                         'type': message.type})

    return response_json(
        errcode=SUCCESS,
        data={
            'messages': messages
        }
    )


def get_user_public_rooms(request):
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get('projectId'))
    userId = int(kwargs.get('currentUserId'))

    discussions = []
    for association in UserGroup.objects.filter(user=userId):
        group = Group.objects.get(id=association.group.id)
        if group.type == 'PUB' and group.project_id_id == projectId:

            users = []
            for asso in UserGroup.objects.filter(group=group):
                users.append({'userId': asso.user.id,
                              'userName': asso.user.name,
                              'userRole': asso.role})
            for user in users:
                if user.userRole == 'B':
                    owner_index = users.index(user)
                    users[0], users[owner_index] = users[owner_index], users[0]
                    break

            discussions.append({
                'roomId': group.id,
                'roomName': group.name,
                'outline': group.outline,
                'users': users
            })

    return response_json(
        errcode=SUCCESS,
        data={
            'discussions': discussions
        }
    )


def get_user_private_rooms(request):
    kwargs: dict = json.loads(request.body)

    projectId = int(kwargs.get('projectId'))
    userId = int(request.session['currentUserId'])

    project = Project.objects.get(id=projectId)
    user = User.objects.get(id=userId)

    privates = []
    for association in UserGroup.objects.filter(user=user):
        group = Group.objects.get(id=association.group.id, project_id=project)
        if group.type == 'PRI':
            pri_assos = UserGroup.objects.filter(group=group)
            targetUserId = 0
            targetUserName = ""
            for asso in pri_assos:
                if asso.user.id == userId:
                    continue
                else:
                    targetUserId = asso.user.id
                    targetUserName = asso.user.name
            privates.append({
                'roomId': group.id,
                'targetUserId': targetUserId,
                'targetUserName': targetUserName
            })

    return response_json(
        errcode=SUCCESS,
        data={
            'privates': privates
        }
    )


def create_public_room(request):
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get('projectId'))
    currentUser = User.objects.get(id=kwargs.get('currentUserId'))
    group = Group(
        name=kwargs.get('roomName'),
        outline=kwargs.get('outline'),
        project_id=project,
        type='PUB'
    )
    group.save()

    association = UserGroup(
        user=currentUser,
        group=group,
        role='B'
    )
    association.save()

    for user_info in kwargs.get('users'):
        if user_info == currentUser.id:
            continue
        user = User.objects.get(id=user_info)
        association = UserGroup(
            user=user,
            group=group,
            role='A'
        )
        association.save()

    return response_json(
        errcode=SUCCESS,
        data={
            'roomId': group.id,
        }
    )


def create_private_room(request):
    kwargs: dict = json.loads(request.body)
    project = Project.objects.get(id=kwargs.get('projectId'))
    currentUser = User.objects.get(id=kwargs.get('currentUserId'))
    targetUser = User.objects.get(id=kwargs.get('targetUserId'))

    all_pri_groups = Group.objects.filter(type='PRI', project_id=project)
    for pri_group in all_pri_groups:
        if UserGroup.objects.filter(user=currentUser, group=pri_group).exists() and UserGroup.objects.filter(
                user=targetUser, group=pri_group).exists():
            return response_json(
                errcode=SUCCESS,
                data={
                    'roomId': pri_group.id,
                }
            )

    group = Group(
        name="NONE",
        outline="NONE",
        project_id=project,
        type='PRI'
    )
    group.save()

    association = UserGroup(
        user=currentUser,
        group=group,
        role='A'
    )
    association.save()

    association = UserGroup(
        user=targetUser,
        group=group,
        role='A'
    )
    association.save()

    return response_json(
        errcode=SUCCESS,
        data={
            'roomId': group.id,
        }
    )


def add_user_to_room(request):
    kwargs: dict = json.loads(request.body)

    user = User.objects.get(id=int(kwargs.get('userId')))
    group = Group.objects.get(id=int(kwargs.get('roomId')))

    if group.type == 'PRI':
        return response_json(
            errcode=ILLEGAL,
            message='PRIVATE ROOM CAN NOT INVITE PEOPLE!'
        )

    association = UserGroup.objects.filter(user=user, group=group)
    if not len(association) == 0:
        return response_json(
            errcode=SUCCESS,
        )
    association = UserGroup(
        user=user,
        group=group,
        role='A'
    )
    association.save()
    return response_json(
        errcode=SUCCESS
    )


def delete_user_from_room(request):
    kwargs: dict = json.loads(request.body)
    currentUser = User.objects.get(id=int(kwargs.get('currentUserId')))
    targetUser = User.objects.get(id=int(kwargs.get('targetUserId')))
    room = Group.objects.get(id=int(kwargs.get('roomId')))
    association = UserGroup.objects.get(user=currentUser, group=room)

    if association.role == 'B':
        association = UserGroup.objects.get(user=targetUser, group=room)
        association.delete()
        return response_json(
            errcode=SUCCESS
        )

    else:
        return response_json(
            errcode=ILLEGAL,
            message="YOU ARE NOT THE OWNER!"
        )


def delete_user_from_groups(user_id: int, project_id: int):
    user = User.objects.get(id=int(user_id))
    project = Project.objects.get(id=int(project_id))

    groups = Group.objects.filter(project_id=project)
    for group in groups:
        association = UserGroup.objects.filter(user=user, group=group)
        if not len(association) == 0:
            association.first().delete()


def delete_room(request):
    kwargs: dict = json.loads(request.body)
    currentUser = User.objects.get(id=int(kwargs.get('currentUserId')))
    room = Group.objects.get(id=int(kwargs.get('roomId')))
    association = UserGroup.objects.get(user=currentUser, group=room)
    if room.type == 'PRI':
        return response_json(
            errcode=ILLEGAL,
            message="CAN'T DELETE PRIVATE ROOM!"
        )
    if association.role == 'B':
        messages = Message.objects.filter(group=room)
        for message in messages:
            if message.type == 'B':
                delete_img(message.content)
        messages.delete()

        association = UserGroup.objects.filter(group=room)
        association.delete()

        room.delete()
        return response_json(errcode=SUCCESS)
    else:
        return response_json(
            errcode=ILLEGAL,
            message="YOU ARE NOT THE OWNER!"
        )


def exit_room(request):
    kwargs: dict = json.loads(request.body)
    currentUser = User.objects.get(id=int(kwargs.get('currentUserId')))
    room = Group.objects.get(id=int(kwargs.get('roomId')))
    association = UserGroup.objects.get(user=currentUser, group=room)
    if room.type == 'PRI':
        return response_json(
            errcode=ILLEGAL,
            message="CAN'T EXIT PRIVATE ROOM!"
        )
    if association.role == 'A':
        association.delete()
        return response_json(errcode=SUCCESS)
    else:
        return response_json(
            errcode=ILLEGAL,
            message="YOU ARE THE OWNER!"
        )
