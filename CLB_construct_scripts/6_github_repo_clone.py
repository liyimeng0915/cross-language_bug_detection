import subprocess
import time
import os
import requests
import shutil


def clone_or_update_repo(owner, repo_name, target_dir):
    repo_url = f"https://github.com/{owner}/{repo_name}.git"
    subprocess.run(["git", "clone", repo_url, target_dir])

def list_files_in_directory(directory_path):

    # 获取目录中的所有条目
    entries = os.listdir(directory_path)

    # 过滤出文件
    files = [file for file in entries if os.path.isfile(os.path.join(directory_path, file))]

    return files



def extract_names(filename):
    name_without_extension = filename[:-4]
    a, b = name_without_extension.split('_', 1)

    return a, b


def check_website(url):

    try:
        response = requests.get(url)

        if response.status_code == 200:
            print(f"{url} 可以正常访问。")
            return True
        else:
            print(f"{url} 无法正常访问。状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"访问 {url} 时出错: {e}")
        return False


if __name__ == '__main__':
    base_dir = "commits_filtered_by_issues_title\\"

    files_list = list_files_in_directory(base_dir)

    for i, file in enumerate(files_list):
        owner, repo_name = extract_names(file)
        print("*"*100)
        print(file, owner, repo_name, i+1)
        target_folder = f"repo\\{owner}\\{repo_name}"

        clone_or_update_repo(owner, repo_name, target_folder)

