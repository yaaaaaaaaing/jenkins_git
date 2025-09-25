from github import Github
import git
import re
import os
import getopt
import sys
from datetime import datetime, timezone
import requests

def get_latest_commit_sha(repo,target_branch):
    return repo.get_branch(target_branch).commit.sha

def add_tag(repo,latest_commit_sha,tag_version):
    tag_exist = False
    tags = repo.get_tags()
    for tag in tags:
        if tag.name == tag_version:
            tag_exist = True
    if not tag_exist:
        repo.create_git_ref(ref=f"refs/tags/{tag_version}",sha=latest_commit_sha)

def creat_release(repo,repo_path,tag_version,access_token):
    
    token = access_token
    tag_name = tag_version      # 已经存在的 tag
    release_name = "Release" + tag_version
    release_body = f"This is the release for version {tag_version}"

    url = f"https://api.github.com/repos/{repo_path}/releases"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "tag_name": tag_name,
        "name": release_name,
        "body": release_body,
        "draft": False,
        "prerelease": False
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 201:
        print(f"Failed to create release: {response.status_code}")
        print(response.json())
        return
    else:
        upload_url = response.json()["upload_url"].split("{")[0]  # 去掉 {?name,label}
        file_path = "this is a file from repo JENKINS_GIT"
        file_name = "this is a file from repo JENKINS_GIT"

        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/zip"
        }

        with open(file_path, "rb") as f:
            upload_response = requests.post(
                f"{upload_url}?name={file_name}",
                headers=headers,
                data=f
            )

    print(1)

if __name__ == "__main__":
    access_token = os.environ["GITHUB_TOKEN"]
    g = Github(login_or_token = access_token)
    repo_name = "jenkins_test"
    user_name = "yaaaaaaaaing"
    target_branch = 'develop'
    tag_version = 'v1.2.0'

    user = g.get_user(user_name)
    repo = user.get_repo(repo_name)
    latest_commit_sha = get_latest_commit_sha(repo,target_branch)
    add_tag(repo,latest_commit_sha,tag_version)
    creat_release(repo,f'{user_name}/{repo_name}',tag_version,access_token)