from github import Github
import git
import re
import os
import getopt
import sys
import shutil

def find_mr(target_branch,PolarionId,repo):
    title_patt = re.compile(f"polarion\s*\[\s*{PolarionId}\s*\]")
    merge_request_list = repo.get_pulls(state='open')
    merge_commit_sha_list = []
    for merge_request in merge_request_list:
        if title_patt.findall(merge_request.title) is not [] and target_branch == merge_request.base.ref:
            for request_commit in merge_request.get_commits():
                merge_commit_sha_list.append(request_commit.sha)
    return merge_commit_sha_list



def CollectCode_and_PushCommits(merge_commit_sha_list,target_branch):
    target_path = "./jenkins_test"
    if os.path.exists(target_path):
        os.remove(target_path)
    cmd = f"git clone git@github.com:yaaaaaaaaing/jenkins_test.git -b {target_branch}"
    os.system(cmd)
    local_repo = git.Repo(target_path)
    for commit_sha in merge_commit_sha_list:
        local_repo.git.cherry_pick(commit_sha)

def RunProject_and_UpdateStatus(merge_commit_sha_list,repo):
    python = '.\jenkins_test\virtual_py\Scripts\python.exe'
    cmd = "cd.\jenkins_test && python python_code.py"
    cwd = os.getcwd()
    if os.system(cmd) == 0:
        run_result = 0
    else:
        run_result = 1
    
    if run_result == 0:
        for merge_commit_sha in merge_commit_sha_list:
            repo.get_commit(merge_commit_sha).create_status(
            state="success",  # 状态: "error", "failure", "pending", or "success"
            context="pp_ci"  # 状态检测名称
            )
    else:
        for merge_commit_sha in merge_commit_sha_list:
            repo.get_commit(merge_commit_sha).create_status(
            state="failure",  # 状态: "error", "failure", "pending", or "success"
            context="pp_ci"  # 状态检测名称
            )




if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:t:l:", ["polarionid=","target_branch=","log_path"])
    except getopt.GetoptError:
        print("error!")
        exit(1)  
    PolarionId = '1234'
    target_branch = 'develop'
    for opt, value in opts:
        if opt in ('-p', '--polarionid'):
            PolarionId = value
        elif opt in ('-t', '--target_branch'):
            target_branch = value
        else:
            pass

    access_token = os.environ["GITHUB_TOKEN"]
    g = Github(login_or_token = access_token)
    user = g.get_user("yaaaaaaaaing")
    repo = user.get_repo("jenkins_test")

    merge_commit_sha_list = find_mr(target_branch,PolarionId,repo)
    CollectCode_and_PushCommits(merge_commit_sha_list,target_branch)
    RunProject_and_UpdateStatus(merge_commit_sha_list,repo)

print("1")

