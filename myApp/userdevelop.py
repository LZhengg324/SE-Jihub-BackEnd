import struct

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.views import View
from myApp.models import *
from djangoProject.settings import DBG, USER_REPOS_DIR, BASE_DIR
import json
import os
import shutil
import sys
import subprocess
import json5
import pytz

repo_semaphore = {}


def getSemaphore(repoId):
    repoId = str(repoId)
    if not repo_semaphore.__contains__(repoId):
        repo_semaphore[repoId] = True
        return
    while repo_semaphore[repoId] == True:
        continue
    repo_semaphore[repoId] = True
    return


def releaseSemaphore(repoId):
    repo_semaphore[repoId] = False
    return


MERET = 0


def getCounter():
    global MERET
    MERET = MERET + 1
    return MERET - 1


def isProjectExists(projectId):
    try:
        project = Project.objects.get(id=projectId)
        return project
    except Exception as e:
        return None


def isUserInProject(userId, projectId):
    try:
        userProject = UserProject.objects.get(user_id=userId, project_id=projectId)
        return userProject
    except Exception as e:
        return None


def genUnexpectedlyErrorInfo(response, e):
    response["errcode"] = -1
    response['message'] = "unexpectedly error : " + str(e)
    return response


def genResponseStateInfo(response, errcode, message):
    response["errcode"] = errcode
    response['message'] = message
    return response


class GetProjectName(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get project name ok")
        response["data"] = {}
        response["data"]["name"] = ""
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        response["data"]["name"] = project.name
        return JsonResponse(response)


class GetBindRepos(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get bind repos ok")
        response["data"] = []
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        descLogName = str(getCounter()) + "_getRepoDesc.log"
        try:
            userProjectRepos = UserProjectRepo.objects.filter(project_id=projectId)
            for userProjectRepo in userProjectRepos:
                repoId = userProjectRepo.repo_id.id
                repo = Repo.objects.get(id=repoId)

                os.system(
                    "gh repo view \"" + repo.remote_path + "\" | grep description > \"" + os.path.join(USER_REPOS_DIR,
                                                                                                       descLogName) + "\"")
                desc = open(os.path.join(USER_REPOS_DIR, descLogName), "r").readlines()[0]
                desc = desc.split(":", 2)[1].strip()
                os.system("rm -f " + "\"" + os.path.join(USER_REPOS_DIR, descLogName) + "\"")
                if desc.isspace():
                    desc = None
                response["data"].append({"repoId": repoId,
                                         "repoRemotePath": repo.remote_path,
                                         "name": repo.name,
                                         "repoIntroduction": desc})
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)


class UserBindRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "bind ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoRemotePath = kwargs.get('repoRemotePath')
        DBG("userId=" + userId + " projectId=" + projectId + " repoRemotePath=" + repoRemotePath)
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))
        # check if repo exists
        try:
            localHasRepo = False
            s = Repo.objects.filter(remote_path=repoRemotePath)
            if len(s) != 0:
                localHasRepo = True
                repoId = s[0].id
                userProjectRepo = UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId)
                if len(userProjectRepo) != 0:
                    return JsonResponse(genResponseStateInfo(response, 4, "duplicate repo"))
            # clone & repo
            repoName = repoRemotePath.split("/")[-1]
            localPath = os.path.join(USER_REPOS_DIR, repoName)
            DBG("repoName=" + repoName, " localPath=" + localPath)
            if localHasRepo == False:
                # if dir not exists, then clone
                if not os.path.exists(localPath):
                    print("---------------")
                    print("gh repo clone " + repoRemotePath + " " + "\"" + localPath + "\"")
                    r = os.system("gh repo clone " + repoRemotePath + " " + "\"" + localPath + "\"")
                    if r != 0:
                        return JsonResponse(genResponseStateInfo(response, 5, "clone repo fail"))
            # insert Repo
            repo = None
            s = Repo.objects.filter(remote_path=repoRemotePath)
            if len(s) != 0:
                repo = s[0]
            else:
                repoEntry = Repo(name=repoName, local_path=localPath, remote_path=repoRemotePath)
                repoEntry.save()
                # insert UserProjectRepo
                repo = Repo.objects.get(name=repoName, local_path=localPath, remote_path=repoRemotePath)
            user = User.objects.get(id=userId)
            project = Project.objects.get(id=projectId)
            userProjectRepoEntry = UserProjectRepo(user_id=user, project_id=project, repo_id=repo)
            userProjectRepoEntry.save()
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)


class UserUnbindRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "unbind ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(user_id=userId, project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project that bind by this user"))

        try:
            userProjectRepo = UserProjectRepo.objects.get(user_id=userId, project_id=projectId, repo_id=repoId)
            userProjectRepo.delete()
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))

        return JsonResponse(response)


class GetRepoBranches(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get branches ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = []
        try:
            log = str(getCounter()) + "_getRepoBranches.log"
            commitLog = str(getCounter()) + "_commitInfo.log"
            remotePath = Repo.objects.get(id=repoId).remote_path
            os.system("gh api -H \"Accept: application/vnd.github+json\" -H \
                \"X-GitHub-Api-Version: 2022-11-28\" /repos/" + remotePath + "/branches > " + "\"" + os.path.join(
                USER_REPOS_DIR, log) + "\"")
            ghInfo = json.load(open(os.path.join(USER_REPOS_DIR, log), encoding="utf-8"))
            for it in ghInfo:
                sha = it["commit"]["sha"]
                cmd = "gh api /repos/" + remotePath + "/commits/" + sha + " > " + "\"" + os.path.join(USER_REPOS_DIR,
                                                                                                      commitLog) + "\""
                os.system(cmd)
                commitInfo = json.load(open(os.path.join(USER_REPOS_DIR, commitLog), encoding="utf-8"))
                data.append({"branchName": it["name"],
                             "lastCommit": {
                                 "sha": sha,
                                 "authorName": commitInfo["commit"]["author"]["name"],
                                 "authorEmail": commitInfo["commit"]["author"]["email"],
                                 "commitDate": commitInfo["commit"]["author"]["date"],
                                 "commitMessage": commitInfo["commit"]["message"]
                             }
                             })
            response["data"] = data
            # os.system("rm -f " + os.path.join(USER_REPOS_DIR, log))
            # os.system("rm -f " + os.path.join(USER_REPOS_DIR, commitLog))
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


class GetCommitHistory(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get commit history ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branchName = kwargs.get('branchName')
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = []
        try:
            log = str(getCounter()) + "_getCommitHistory.log"
            localPath = "\"" + Repo.objects.get(id=repoId).local_path + "\""
            getSemaphore(repoId)
            os.system("cd " + localPath + " && git checkout " + branchName + " && git pull")
            cmd = "cd " + localPath + " && bash " + "\"" + os.path.join(BASE_DIR,
                                                                        "myApp/get_commits.sh") + "\"" + " > " + "\"" + os.path.join(
                USER_REPOS_DIR, log) + "\""
            os.system(cmd)
            releaseSemaphore(repoId)
            try:
                ghInfo = json5.load(open(os.path.join(USER_REPOS_DIR, log), encoding="utf-8"))
            except Exception as e:
                DBG("in GetCommitHistory has excp : " + str(e))
            response["data"] = ghInfo
            os.system("rm -f " + "\"" + os.path.join(USER_REPOS_DIR, log) + "\"")
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


class GetIssueList(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get issue list ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = []
        try:
            log = "getIssueList.log"
            remotePath = Repo.objects.get(id=repoId).remote_path
            os.system("gh api -H \"Accept: application/vnd.github+json\" -H \
                \"X-GitHub-Api-Version: 2022-11-28\" /repos/" + remotePath + "/issues?state=all > " + "\"" + os.path.join(
                USER_REPOS_DIR, log) + "\"")
            ghInfo = json.load(open(os.path.join(USER_REPOS_DIR, log), encoding="utf-8"))
            for it in ghInfo:
                data.append({"issueId": it["number"],
                             "issuer": it["user"]["login"],
                             "issueTitle": it["title"],
                             "issueTime": it["updated_at"],
                             "isOpen": it["state"] == "open",
                             "ghLink": it["html_url"]})
            response["data"] = data
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


class GetPrList(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get pr list ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = []
        try:
            log = "getPrList.log"
            remotePath = Repo.objects.get(id=repoId).remote_path
            os.system("gh api  /repos/" + remotePath + "/pulls?state=all > " + "\"" + os.path.join(USER_REPOS_DIR,
                                                                                                   log) + "\"")
            ghInfo = json.load(open(os.path.join(USER_REPOS_DIR, log), encoding="utf-8"))
            for it in ghInfo:
                data.append({"prId": it["number"],
                             "prIssuer": it["user"]["login"],
                             "prTitle": it["title"],
                             "prTime": it["updated_at"],
                             "isOpen": it["state"] == "open",
                             "ghLink": it["html_url"],
                             "fromBranchName": it["head"]["ref"],
                             "toBranchName": it["base"]["ref"]})
            response["data"] = data
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


def _getFileTree(dirPath):
    if os.path.isfile(dirPath):
        return {"name": os.path.basename(dirPath)}
    children = []
    fs = os.listdir(dirPath)
    for f in fs:
        if f == ".git":
            continue
        children.append(_getFileTree(os.path.join(dirPath, f)))
    return {"name": os.path.basename(dirPath), "children": children}


class GetFileTree(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get file tree ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branch = str(kwargs.get('branch'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = []
        try:
            localPath = Repo.objects.get(id=repoId).local_path
            getSemaphore(repoId)
            os.system("cd " + "\"" + localPath + "\"" + " && git checkout " + branch + " && git pull")
            r = _getFileTree(localPath)
            for item in r["children"]:
                data.append(item)
            response["data"] = data
            releaseSemaphore(repoId)
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


class GetContent(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "get file tree ok")
        userId = str(kwargs.get('userId'))
        projectId = str(kwargs.get('projectId'))
        repoId = str(kwargs.get('repoId'))
        branch = str(kwargs.get('branch'))
        path = str(kwargs.get('path'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        userProject = isUserInProject(userId, projectId)
        if userProject == None:
            return JsonResponse(genResponseStateInfo(response, 2, "user not in project"))

        if not UserProjectRepo.objects.filter(project_id=projectId, repo_id=repoId).exists():
            return JsonResponse(genResponseStateInfo(response, 3, "no such repo in project"))

        data = ""
        try:
            localPath = Repo.objects.get(id=repoId).local_path
            getSemaphore(repoId)
            os.system("cd " + localPath + " && git checkout " + branch + " && git pull")
            filePath = localPath + path  # os.path.join(localPath, path)
            DBG(filePath)
            data = "警告：这是一个二进制文件，请登录 github 查看"
            try:
                data = open(filePath).read()
            except Exception as e:
                pass
            response["data"] = data
            releaseSemaphore(repoId)
        except Exception as e:
            return genUnexpectedlyErrorInfo(response, e)
        return JsonResponse(response)


# 创建一个Pull Request，并把Pull Request记录到表中，未处理关联，未添加进url，未测试
class CreatePullRequest(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        title = kwargs.get('title')
        description = kwargs.get('description')
        project_id = kwargs.get('project_id')
        if not UserProjectRepo.objects.filter(project_id=project_id).exists():
            return JsonResponse(genResponseStateInfo(response, 1, "Project is not associated with a repo"))

        user_id = kwargs.get('user_id')
        source_branch_name = kwargs.get('source_branch_name')
        repo_id = kwargs.get('repo_id')
        tasks_id = kwargs.get('tasks')

        userProject = UserProject.objects.get(user_id_id=user_id, project_id_id=project_id)
        if userProject.role == UserProject.ILLEGAL :
            return JsonResponse(genResponseStateInfo(response, 4, "user is illegal to create pr in this project"))

        repo = Repo.objects.get(id=repo_id)
        local_path = repo.local_path
        remote_path = repo.remote_path

        try:
            command = (
                'cd \"{}\" && '
                'gh pr create '
                '--title "{}" '
                '--body "{}" '
                '--base main '
                '--head "{}" '
                '--repo "{}"'
                .format(local_path, title, description, source_branch_name, remote_path)
            )
            print(command)
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            print(result)
            if result.returncode == 0:
                ghpr_id = result.stdout.strip().split('/')[-1]
                user = User.objects.get(id=user_id)
                project = Project.objects.get(id=project_id)
                projectLinkPr = ProjectLinkPr.objects.create(ghpr_id=ghpr_id, user_id=user, repo_id=repo,
                                                             project_id=project)
                projectLinkPr.save()
                tasks = []
                for t in tasks_id:
                    task = Task.objects.get(id=t)
                    parent_task = Task.objects.get(id=task.parent_id_id)
                    tasks.append({"id": task.id, "name": task.name, "parent_task": parent_task.name})
                    print(task, task.id)
                    task.status = Task.REVIEWING
                    task.link_pr = projectLinkPr
                    task.save()
                    comment = CommentInPr.objects.create(user=user, projectLinkPr=projectLinkPr,
                                                         content=parent_task.name + " - " + task.name)
                    comment.save()
                content = ('"{}" 在 {} 分支上提交了一个新的 Pull Request'
                           '关联子任务:'.format(user.name, source_branch_name))
                tasks_info = ""
                for task_info in tasks:
                    task_name = task_info["name"]
                    parent_task_name = task_info["parent_task"]
                    tasks_info += f"\n任务名称: {task_name}, 所属冲刺: {parent_task_name}"
                content += tasks_info
                notify_people = User.objects.get(id=project.manager_id_id)
                notify = Notice.objects.create(deadline=datetime.datetime.now(datetime.timezone.utc),
                                               type=Notice.NOTIFICATION,
                                               projectLinkPr_id=projectLinkPr, user_id=notify_people,
                                               seen=False, content=content, project_id=project)
                notify.save()
            else:
                return JsonResponse(genResponseStateInfo(response, 2, "create pr failed"))
        except Exception as e:
            return JsonResponse(genResponseStateInfo(response, 3, str(e)))
        return JsonResponse(genResponseStateInfo(response, 0, "create pr success"))


class createBranch(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        name = kwargs.get('name')
        project_id = kwargs.get('project_id')
        remote_path = str(kwargs.get('remote_path'))
        print("remote_path : " + remote_path)
        user_id = kwargs.get('user_id')
        user = User.objects.get(id=user_id)
        repo = Repo.objects.get(remote_path=remote_path)
        project = Project.objects.get(id=project_id)
        repo_id = repo.id
        if Branch.objects.filter(name=name, project_id=project_id, user_id=user_id, repo_id=repo_id).exists():
            return JsonResponse(genResponseStateInfo(response, 1, "Duplicated Branch"))
        localpath = repo.local_path
        try:
            os.system("cd \"" + localpath + "\" && git checkout main && git pull && git branch "
                      + name + " && git checkout " + name + " && git push -u origin " + name)
        except Exception:
            return JsonResponse(genResponseStateInfo(response, 2, "os.system error"))
        branch = Branch.objects.create(name=name, project_id=project, repo_id=repo, user_id=user)
        branch.save()
        return JsonResponse(genResponseStateInfo(response, 0, "Branch created successfully"))


class GetDiff(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        user_id = kwargs['user_id']
        remote_path = kwargs['remote_path']
        project_id = kwargs['project_id']
        ghpr_id = str(kwargs['ghpr_id'])
        title = ""
        description = ""

        if user_id == None or remote_path == None or project_id == None:
            return JsonResponse(genResponseStateInfo(response, 1, "Null User_id/Remote_path/Project_id"))

        if not isProjectExists(project_id):
            return JsonResponse(genResponseStateInfo(response, 2, "Project does not exist"))

        if not isUserInProject(user_id, project_id):
            return JsonResponse(genResponseStateInfo(response, 3, "user not in project"))

        try:
            repo = Repo.objects.get(remote_path=remote_path)
            projectLinkPr = ProjectLinkPr.objects.get(ghpr_id=ghpr_id, project_id_id=project_id, repo_id_id=repo.id)
            local_path = repo.local_path
            cmd = "cd \"" + local_path + "\" && gh pr diff " + ghpr_id
            print(cmd)
            diff_output = os.popen(cmd).read()
            tasks_info = ""
            tasks = Task.objects.filter(link_pr_id=projectLinkPr.id).order_by('parent_id_id')
            print(tasks.count())
            for task in tasks:
                parentTask = Task.objects.get(id=task.parent_id_id)
                tasks_info += f"冲刺: {parentTask.name}  ---  子任务: {task.name}\n"
            result = subprocess.run(['gh', 'pr', 'view', str(ghpr_id), '--json', 'title,body'], cwd=local_path,
                                    capture_output=True, text=True, encoding="utf-8")
            print(result)
            if result.returncode == 0:
                pr_info = json.loads(result.stdout)
                title = pr_info['title']
                description = pr_info['body']
        except Exception:
            return JsonResponse(genResponseStateInfo(response, 4, "os.popen Error"))

        genResponseStateInfo(response, 0, "gh pr diff success")
        response['diff_output'] = diff_output
        response['title'] = title
        response['description'] = description
        response['tasks_info'] = tasks_info
        response['comment'] = projectLinkPr.comment
        return JsonResponse(response)


class ApprovePullRequest(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        ghpr_id = kwargs['ghpr_id']
        repo_id = kwargs['repo_id']
        comment = kwargs['comment']

        if not Repo.objects.filter(id=repo_id).exists:
            return JsonResponse(genResponseStateInfo(request, 1, "repo not exist"))

        if not ProjectLinkPr.objects.filter(ghpr_id=ghpr_id).exists:
            return JsonResponse(genResponseStateInfo(response, 2, "ghpr_id is invalid"))

        repo = Repo.objects.get(id=repo_id)
        projectLinkPr = ProjectLinkPr.objects.get(ghpr_id=ghpr_id, repo_id=repo)
        project = Project.objects.get(id=projectLinkPr.project_id_id)
        # print("Repo : " + str(repo.id))
        # print("Project : " + str(project.id))
        try:
            local_path = repo.local_path
            command = (
                'cd "{}" && '
                'gh pr merge "{}" --merge'
                .format(local_path, ghpr_id)
            )
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            # print(result)
            if result.returncode == 0:
                tasks_link = Task.objects.filter(link_pr=projectLinkPr)
                for task in tasks_link:
                    task.status = Task.COMPLETED
                    cur_date = datetime.date.today()
                    cur_y, cur_m, cur_d = int(cur_date.year), int(cur_date.month), int(cur_date.day)
                    cur_time = datetime.datetime.now().time()
                    cur_hour, cur_min, cur_sec = int(cur_time.hour), int(cur_time.minute), int(cur_time.second)
                    task.complete_time = datetime.datetime(year=cur_y, month=cur_m, day=cur_d, hour=cur_hour,
                                                           minute=cur_min, second=cur_sec, tzinfo=pytz.utc)
                    task.save()
                projectLinkPr.comment = comment
                projectLinkPr.save()
                user = User.objects.get(id=projectLinkPr.user_id_id)
                content = ('您提交的Pull Request —— #{} 项目负责人已通过'.format(projectLinkPr.ghpr_id))
                notify = Notice.objects.create(deadline=datetime.datetime.now(datetime.timezone.utc),
                                               type=Notice.NOTIFICATION,
                                               projectLinkPr_id=projectLinkPr, user_id=user, seen=False,
                                               content=content, project_id=project)
                notify.save()
            else:
                return JsonResponse(genResponseStateInfo(response, 3, "approve pr failed"))
        except Exception as e:
            return JsonResponse(response, 4, str(e))

        return JsonResponse(genResponseStateInfo(response, 0, "approve pull success"))


class ClosePullRequest(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)

        reponse = {}
        ghpr_id = kwargs['ghpr_id']
        repo_id = kwargs['repo_id']
        comment = kwargs['comment']

        if not Repo.objects.filter(id=repo_id).exists:
            return JsonResponse(genResponseStateInfo(request, 1, "repo not exist"))

        if not ProjectLinkPr.objects.filter(ghpr_id=ghpr_id).exists:
            return JsonResponse(genResponseStateInfo(response, 2, "ghpr_id is invalid"))

        repo = Repo.objects.get(id=repo_id)
        projectLinkPr = ProjectLinkPr.objects.get(ghpr_id=ghpr_id, repo_id=repo)
        project = Project.objects.get(id=projectLinkPr.project_id_id)
        # print("Repo : " + str(repo.id))
        # print("Project : " + str(project.id))
        try:
            local_path = repo.local_path
            # print(local_path)
            command = (
                'cd \"{}\" &&'
                'gh pr close "{}"'
                .format(local_path, ghpr_id)
            )
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            # print(result)
            if result.returncode == 0:
                tasks_link = Task.objects.filter(link_pr=projectLinkPr)
                for task in tasks_link:
                    task.status = Task.INPROGRESS
                    task.link_pr = None
                    task.save()
                projectLinkPr.comment = comment
                projectLinkPr.save()
                user = User.objects.get(id=projectLinkPr.user_id_id)
                content = ('您提交的Pull Request —— #{}已被项目负责人拒绝'.format(projectLinkPr.ghpr_id))
                notify = Notice.objects.create(deadline=datetime.datetime.now(datetime.timezone.utc),
                                               type=Notice.NOTIFICATION,
                                               projectLinkPr_id=projectLinkPr, user_id=user, seen=False,
                                               content=content, project_id=project)
                notify.save()
            else:
                return JsonResponse(genResponseStateInfo(response, 3, "close pr failed"))
        except Exception as e:
            return JsonResponse(genResponseStateInfo(reponse, 4, str(e)))

        return JsonResponse(genResponseStateInfo(reponse, 0, "close pull success"))


class CreateRepo(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        name = kwargs.get('name')
        user_id = kwargs.get('user_id')
        project_id = kwargs.get('project_id')
        remote_path = str(kwargs.get('remote_path'))
        local_path = os.path.join(USER_REPOS_DIR, name)
        # print("local_path : " + local_path)
        # print("remote_path : " + remote_path)
        if user_id == None or remote_path == None or project_id == None:
            return JsonResponse(genResponseStateInfo(response, 1, "Null User_id/Remote_path/Project_id"))

        if not isProjectExists(project_id):
            return JsonResponse(genResponseStateInfo(response, 2, "Project does not exist"))

        if not isUserInProject(user_id, project_id):
            return JsonResponse(genResponseStateInfo(response, 3, "user not in project"))
        try:
            # print("gh repo create " + name + "_" + str(project_id) + " --public")
            os.system("gh repo create " + name + "_" + str(project_id) + " --public")
            # print("---------------")
            original_directory = os.getcwd()

            # 改变当前工作目录到repoTemp
            os.chdir("repoTemp")
            # 在repoTemp目录下创建一个新目录
            os.mkdir(name + "_" + str(project_id))
            os.chdir(name + "_" + str(project_id))
            op = "echo \"# " + name + "\"" + " >> README.md && " \
                 + "git init && git add README.md && " \
                 + "git commit -m \"first commit\" && " + "git branch -M main && " \
                 + "git remote add origin " + remote_path + name + "_" + str(project_id) + ".git && " \
                 + "git push -u origin main"
            # print(op)
            os.system(op)

            # cmd = "gh repo view Jihub2024/" + name + "_" + str(project_id) + " --json sshUrl"
            # ssh = ""
            # result = subprocess.run(cmd, capture_output=True, shell=True, text=True)
            # if result.returncode == 0:
            #     data = json.loads(result.stdout)
            #     ssh = data['sshUrl']
            ssh = "git@github.com:Jihub2024/" + name + "_" + str(project_id)
            response['ssh'] = ssh
        except Exception:
            return JsonResponse(genResponseStateInfo(response, 2, "os.system error"))
        # repo = Repo.objects.create(name=name, local_path=local_path, remote_path=remote_path)
        # repo.save()
        # userProjectRepo = UserProjectRepo.objects.create(user_id=user_id, project_id=project_id, repo_id=repo.id)
        # userProjectRepo.save()
        return JsonResponse(genResponseStateInfo(response, 0, "Repo created successfully"))


# class CreateMainBranch(View):
#   def post(self, request):
#     DBG("---- in " + sys._getframe().f_code.co_name + " ----")
#     response = {'message': "404 not success", "errorcode": -1}
#     try:
#       kwargs:dict = json.loads(request.body)
#     except Exception:
#       return JsonResponse(response)
#     response = {}
#     repo_name = kwargs.get('repo_name')
#     repo = Repo.objects.get(repo_name)
#     remote_path = kwargs.get('remote_path')
#     # remote_path = repo.remote_path
#     local_path = repo.local_path
#     print("local_path : " + local_path)
#     print("remote_path : " + remote_path)
#
#     try:
#       #cd \"" + local_path + "\" &&
#       op = "cd " + local_path + "\necho # " + repo_name + \
#            ">> README.md\n" + "git add README.md\n" + \
#             "git commit -m \"first commit\"0\n" + "git branch -M main\n" + \
#            "git remote add origin " + remote_path + \
#            "\ngit push -u origin main"
#       print(op)
#       os.system(op)
#
#     except Exception:
#       return JsonResponse(genResponseStateInfo(response, 2, "os.system error"))
#     return JsonResponse(genResponseStateInfo(response, 0, "Repo created successfully"))

class GetActivations(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        genResponseStateInfo(response, 0, "sucsessful!")
        response["data"] = {}
        projectId = str(kwargs.get('project_id'))
        project = isProjectExists(projectId)
        if project == None:
            return JsonResponse(genResponseStateInfo(response, 1, "project does not exists"))
        descLogName = str(getCounter()) + "_GetActivations.log"
        try:
            # userProjectRepos = UserProjectRepo.objects.filter(project_id=projectId)
            tasks = Task.objects.filter(project_id=projectId, status='A', project_id__isnull=False)
            for task in tasks:
                id = task.id

                user_id = UserTask.objects.get(task_id=id).user_id.id
                # print(type(user_id))
                if user_id in response["data"]:
                    response["data"][user_id] += task.contribute_level
                else:
                    response["data"][user_id] = task.contribute_level
        except Exception as e:
            return JsonResponse(genUnexpectedlyErrorInfo(response, e))
        if (len(response["data"]) == 0):
            return JsonResponse(genResponseStateInfo(response, 1, "You don't have completed task"))

        return JsonResponse(response)

class checkIsCollaborator(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        repo_id = kwargs['repo_id']
        username = kwargs['username']
        repo = Repo.objects.get(id=repo_id)
        try:
            cmd = ('gh api   -H "Accept: application/vnd.github+json" '
                   ' -H "X-GitHub-Api-Version: 2022-11-28" '
                   '/repos/{}/collaborators/{}'
                   .format(repo.remote_path, username))
            result = subprocess.run(cmd, capture_output=True, shell=True, text=True)
            # print(result)
            if result.returncode == 0:
                genResponseStateInfo(response, 0, "You are a collaborator in the repository")
            else:
                genResponseStateInfo(response, 1, "You aren't a collaborator in the repository")
        except Exception as e:
            genResponseStateInfo(response, 2, "gh api run failed as: " + str(e))

        return JsonResponse(response)

class inviteCollaborator(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        repo_id = kwargs['repo_id']
        username = kwargs['username']
        repo = Repo.objects.get(id=repo_id)
        response = {}
        try:
            cmd = ('gh api   --method PUT   '
                   '-H "Accept: application/vnd.github+json"   '
                   '-H "X-GitHub-Api-Version: 2022-11-28"   '
                   '/repos/{}/collaborators/{} '
                   .format(repo.remote_path, username))
            result = subprocess.run(cmd, capture_output=True, shell=True, text=True)
            # print(result)
            if result.returncode == 0:
                genResponseStateInfo(response, 0, "Invitation sent successfully")
            else:
                genResponseStateInfo(response, 1, "Invitation sent failed")
        except Exception as e:
            genResponseStateInfo(response, 2, "gh api run failed as: " + str(e))

        return JsonResponse(response)

class comment(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        user_id = kwargs['user_id']
        project_id = kwargs['project_id']
        ghpr_id = kwargs['ghpr_id']
        parent_comment = kwargs['parent_comment']
        content = kwargs['content']

        if not ProjectLinkPr.objects.filter(project_id_id=project_id, ghpr_id=ghpr_id).exists():
            return JsonResponse(genResponseStateInfo(response, 1, "no such gh pr in project"))
        projectLinkPr = ProjectLinkPr.objects.get(project_id_id=project_id, ghpr_id=ghpr_id)
        project = Project.objects.get(id=project_id)

        if not CommentInPr.objects.filter(id=parent_comment).exists():
            return JsonResponse(genResponseStateInfo(response, 2, "no such parent comment in project"))
        parentComment = CommentInPr.objects.get(id=parent_comment)

        user = User.objects.get(id=user_id)
        commentInPr = CommentInPr.objects.create(user=user, projectLinkPr=projectLinkPr, content=content,
                                                 parent_comment=parentComment, checkbox=None)
        commentInPr.save()
        notice_message=('{} 项目的 #{} Pull Request 有新的留言'
                        .format(Project.objects.get(id=project_id).name, projectLinkPr.ghpr_id))
        if user_id == Project.objects.get(id=project_id).manager_id_id:
            toUser = User.objects.get(id=projectLinkPr.user_id_id)
            notify = Notice.objects.create(deadline=datetime.datetime.now(datetime.timezone.utc),
                                            type=Notice.NOTIFICATION, projectLinkPr_id=projectLinkPr,
                                           user_id=toUser, project_id=project, content=notice_message)
        else:
            manager = User.objects.get(id=Project.objects.get(id=project_id).manager_id_id)
            notify = Notice.objects.create(deadline=datetime.datetime.now(datetime.timezone.utc),
                                           type=Notice.NOTIFICATION, projectLinkPr_id=projectLinkPr,
                                           user_id=manager, project_id=project, content=notice_message)
        notify.save()
        return JsonResponse(genResponseStateInfo(response, 0, "comment saved"))

class GetCommentsList(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        project_id = kwargs['project_id']
        ghpr_id = kwargs['ghpr_id']

        if not ProjectLinkPr.objects.filter(project_id_id=project_id, ghpr_id=ghpr_id).exists():
            return JsonResponse(genResponseStateInfo(response, 1, "no such gh pr in project"))
        projectLinkPr = ProjectLinkPr.objects.get(project_id_id=project_id, ghpr_id=ghpr_id)

        taskList = CommentInPr.objects.filter(projectLinkPr=projectLinkPr, parent_comment=None).order_by('id')
        data = []
        for task in taskList:
            tmp = {'task_id' : task.id, 'task_name' : task.content, 'solved' : task.checkbox}
            comments = CommentInPr.objects.filter(parent_comment=task).order_by('created_at')
            commentsList = []
            for comment in comments:
                user = User.objects.get(id=comment.user.id)
                sub_tmp = {'comment_id' : comment.id, 'user_id' : user.id, 'user_name' : user.name,
                           'content' : comment.content, 'created_at' : comment.created_at}
                commentsList.append(sub_tmp)
            tmp['comments'] = commentsList
            data.append(tmp)
        response['data'] = data
        return JsonResponse(genResponseStateInfo(response, 0, "get commentList success"))

class MarkTaskSolved(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        comment_id = kwargs['comment_id']
        comment = CommentInPr.objects.get(id=comment_id)
        if comment == None :
            return JsonResponse(genResponseStateInfo(response, 1, "no such task comment"))
        comment.checkbox = True
        comment.save()
        return JsonResponse(genResponseStateInfo(response, 0, "mark task as solved"))

class GetDiff2(View):
    def post(self, request):
        DBG("---- in " + sys._getframe().f_code.co_name + " ----")
        response = {'message': "404 not success", "errorcode": -1}
        try:
            kwargs: dict = json.loads(request.body)
        except Exception:
            return JsonResponse(response)
        response = {}
        user_id = kwargs['user_id']
        remote_path = kwargs['remote_path']
        project_id = kwargs['project_id']
        source_branch = kwargs['source_branch']

        if user_id == None or remote_path == None or project_id == None:
            return JsonResponse(genResponseStateInfo(response, 1, "Null User_id/Remote_path/Project_id"))

        if not isProjectExists(project_id):
            return JsonResponse(genResponseStateInfo(response, 2, "Project does not exist"))

        if not isUserInProject(user_id, project_id):
            return JsonResponse(genResponseStateInfo(response, 3, "user not in project"))

        try:
            local_path = Repo.objects.get(remote_path=remote_path).local_path
            cmd = "cd \"" + local_path + "\" && git diff main " + source_branch
            diff_output = os.popen(cmd).read()
        except Exception:
            return JsonResponse(genResponseStateInfo(response, 4, "os.popen Error"))

        genResponseStateInfo(response, 0, "git diff success")
        response['diff_output'] = diff_output
        return JsonResponse(response)
