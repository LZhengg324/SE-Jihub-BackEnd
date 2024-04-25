import struct

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR
import json
import os
import shutil
import sys
from myApp.userdevelop import genResponseStateInfo, genUnexpectedlyErrorInfo
import random
from hashlib import sha256

# TODO : add check manager function
def isAdmin(userId):
  try:
    status = User.objects.get(id=userId).status
    if status != User.ADMIN:
      return False
    return True
  except Exception as e:
    return False

def genRandStr(randLength=6):
  randStr = ''
  baseStr = 'ABCDEFGHIGKLMNOPORSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length = len(baseStr) - 1
  for i in range(randLength):
    randStr += baseStr[random.randint(0, length)]
  return randStr

class ShowUsers(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get users ok")
    users = []
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    allUsers = User.objects.all()
    for user in allUsers:
      if user.status == user.ADMIN:
        continue
      users.append({"id": user.id, "name" : user.name, "email" : user.email, 
                    "registerTime" : user.create_time, "status" : user.status})
      
    response["users"] = users
    return JsonResponse(response)
  
class ShowAdmins(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get users ok")
    users = []
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    allUsers = User.objects.all()
    for user in allUsers:
      if user.status != user.ADMIN:
        continue
      users.append({"id": user.id, "name" : user.name, "email" : user.email, 
                    "registerTime" : user.create_time, "status" : user.status})
      
    response["users"] = users
    return JsonResponse(response)

class ChangeUserStatus(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "change status ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    userId = kwargs.get('userId')
    changeToStatus = kwargs.get('changeToStatus')
    user = User.objects.get(id=userId)
    userName = user.name
    if user.status == changeToStatus:
      return JsonResponse(genResponseStateInfo(response, 2, "no need change"))
    user.status = changeToStatus
    user.save()
    response["name"] = userName
    return JsonResponse(response)

class ResetUserPassword(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "reset password ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    userId = kwargs.get('userId')
    user = User.objects.get(id=userId)
    userName = user.name
    resetPassWord = genRandStr()
    user.password = sha256(resetPassWord.encode('utf-8')).hexdigest()
    user.save()
    response["name"] = userName
    response["resetPassword"] = resetPassWord
    return JsonResponse(response)

class ShowAllProjects(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get projects ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    projects = []
    allProjects = Project.objects.all()
    for project in allProjects:
      leader = User.objects.get(id=project.manager_id.id)
      projects.append({"name" : project.name, "projectId" : project.id,
                       "leader" : leader.name, "leaderId" : leader.id,
                      "email" : leader.email, "createTime" : project.create_time,
                      "progress" : project.progress, "status" : project.status, 
                      "access" : project.access})
    response["projects"] = projects
    return JsonResponse(response)

class ChangeProjectStatus(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "change status ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    projectId = kwargs.get('projectId')
    changeToStatus = kwargs.get('changeToStatus')
    project = Project.objects.get(id=projectId)
    projectName = project.name
    if project.status == changeToStatus:
      return JsonResponse(genResponseStateInfo(response, 2, "no need change"))
    project.status = changeToStatus
    project.save()
    response["name"] = projectName
    return JsonResponse(response)
  
class ChangeProjectAccess(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "change status ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    projectId = kwargs.get('projectId')
    changeToAccess = kwargs.get('changeToAccess')
    project = Project.objects.get(id=projectId)
    projectName = project.name
    if project.access == changeToAccess:
      return JsonResponse(genResponseStateInfo(response, 2, "no need change"))
    project.access = changeToAccess
    project.save()
    response["name"] = projectName
    return JsonResponse(response)

class ShowUsersLogin(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get login messages ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    loginMessages = []
    allUsers = User.objects.all()
    for user in allUsers:
      loginMessages.append({"name" : user.name, 
                            "email" : user.email, 
                            "loginTime" : user.last_login_time,
                            "IP" : user.last_login_ip,
                          })
      
    response["loginMessages"] = loginMessages
    return JsonResponse(response)

class GetUserNum(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get users num ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    response["userSum"] = User.objects.count()
    return JsonResponse(response)

class GetProjectNum(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get projects num ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    response["projectSum"] = Project.objects.count()
    return JsonResponse(response)
  
class GetProjectScale(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get numbers of different scale projects ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    tiny = 0
    small = 0
    medium = 0
    big = 0
    large = 0
    projects = Project.objects.all()
    for project in projects:
      usersNum = int(UserProject.objects.filter(project_id=project.id).count())
      if usersNum < 4:
        tiny = tiny + 1
      elif usersNum < 8:
        small = small + 1
      elif usersNum < 16:
        medium = medium + 1
      elif usersNum < 31:
        big = big + 1
      else:
        large = large + 1
    response["tinyNum"] = tiny
    response["smallNum"] = small
    response["mediumNum"] = medium
    response["bigNum"] = big
    response["largeNum"] = large
    return JsonResponse(response)
  
class  GetProjectUsers(View):
    def post(self, request):
      DBG("---- in " + sys._getframe().f_code.co_name + " ----")
      response = {'message': "404 not success", "errcode": -1}
      try:
        kwargs: dict = json.loads(request.body)
      except Exception:
        return JsonResponse(response)
      response = {}
      genResponseStateInfo(response, 0, "get users of this project ok")
      projectId = kwargs.get('projectId',-1)
      managerId = kwargs.get('managerId')
      if not isAdmin(managerId):
        return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
      userList = UserProject.objects.filter(project_id_id=projectId)    
      users = []
      for user in userList:
        users.append({
            "peopleId": user.user_id.id,
            "peopleName": user.user_id.name,
            "peopleEmail": user.user_id.email,
            "peopleActive": 1,
            "peopleStatus": user.user_id.status,
        })

      response["users"] = users
      return JsonResponse(response)

class ShowAssistants(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get users ok")
    users = []
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    allUsers = User.objects.all()
    for user in allUsers:
      if user.status != user.ASSISTANT:
        continue
      users.append({
                    "name" : user.name, 
                    "email" : user.email, 
                    "id": user.id, 
                  })
      
    response["users"] = users
    return JsonResponse(response)

class GetProjectAssistants(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "get assistants of project ok")
    
    projectId = kwargs.get('projectId')
    # managerId = kwargs.get('managerId')
    # if not isAdmin(managerId):
      # return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    
    userProjects = UserProject.objects.all()
    allUsers = User.objects.all()
    assistants = []
    for userProject in userProjects:
      # if userProject.role != "ADMIN":
        # continue
      if userProject.project_id != projectId:
        continue

      for assistant in allUsers:
        if assistant.id == userProject.user_id :
          if assistant.status != "ASSISTANT":
            continue
          assistants.append({
                          "name": assistant.name,
                          "email":  assistant.email,
                          "id": assistant.id,
                        })
    response["assistants"] = assistants
    return JsonResponse(response)

class ChangeUserUploadAccess(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "change user upload access ok")
    managerId = kwargs.get('managerId')
    userId = kwargs.get('userId')
    changeToStatus = kwargs.get('status')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    # projectId = kwargs.get('projectId')
    # changeToAccess = kwargs.get('changeToAccess')
    user = User.objects.get(id=userId)
    userName = user.name
    if user.status == changeToStatus:
      return JsonResponse(genResponseStateInfo(response, 2, "no need change"))
    user.status = changeToStatus
    user.save()
    response["username"] = userName
    return JsonResponse(response)
  
class SetAssistantAccess(View):
  def post(self, request):
    DBG("---- in " + sys._getframe().f_code.co_name + " ----")
    response = {'message': "404 not success", "errcode": -1}
    try:
      kwargs: dict = json.loads(request.body)
    except Exception:
      return JsonResponse(response)
    response = {}
    genResponseStateInfo(response, 0, "change status ok")
    managerId = kwargs.get('managerId')
    if not isAdmin(managerId):
      return JsonResponse(genResponseStateInfo(response, 1, "Insufficient authority"))
    assistantsId = kwargs.get('assistantsId')
    projectId = kwargs.get('projectId')
    # project = Project.objects.get(id=projectId)
    # projectName = project.name
    allUserProjects = UserProject.objects.all()
    for userProject in allUserProjects:
      if userProject.user_id == assistantsId:
        if userProject.role == "ADMIN":
          if userProject.project_id == projectId:
            return JsonResponse(genResponseStateInfo(response, 2, "no need change"))

    newUserProject = UserProject(user_id=assistantsId,
                                 project_id = projectId,
                                 role = "ADMIN")
    newUserProject.save()
    
    response["assistant"] = assistantsId
    response["project"] = projectId
    return JsonResponse(response)
  


