import csv
import requests
import time
import os
import datetime
import pandas as pd
from myutils import send_email
def get_all_commits(owner, repo, token):
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {'Authorization': f'token {token}'}
    commits = []
    i = 0
    try:
        while commits_url:
            response = requests.get(commits_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                commits.extend(data)

                if 'next' in response.links:
                    commits_url = response.links['next']['url']
                    i = i + 1
                else:
                    commits_url = None
            else:
                # 输出错误信息并等待一段时间后重试
                print(f"Failed to fetch commits. Status code: {response.status_code}")
                if response.status_code ==403:
                    time.sleep(600)
                time.sleep(60)
    except requests.exceptions.RequestException as e:
        time.sleep(300)

    return commits


def write_commits_to_csv(commits, output_file):
    fieldnames = ['SHA', 'Author', 'Date', 'Message', 'Parent_SHA', 'Parent_SHA_num']

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for commit in commits:
            if len(commit['parents']) != 0:
                parent_sha = commit['parents'][0]['sha']
            else:
                parent_sha = None
            commit_data = {
                'SHA': commit['sha'],
                'Author': commit['commit']['author']['name'],
                'Date': commit['commit']['author']['date'],
                'Message': commit['commit']['message'],
                'Parent_SHA': parent_sha,
                'Parent_SHA_num': len(commit['parents'])
            }

            writer.writerow(commit_data)

def read_csv_to_list(file_path, column_name, num_rows):

    try:
        df = pd.read_csv(file_path, usecols=[column_name], nrows=num_rows)
        data_list = df[column_name].tolist()
        return data_list
    except FileNotFoundError:
        return []
    except KeyError:
        return []


from urllib.parse import urlparse


def get_repo_owner_and_name(github_url):
    try:
        parsed_url = urlparse(github_url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            owner = path_parts[0]
            name = path_parts[1]
            return owner, name
        else:
            raise ValueError("Invalid GitHub URL format")
    except Exception as e:
        return None, None


if __name__ == '__main__':
    file_path = 'withlabels_repo_all_languages_filtered.csv'
    column_name = 'URL'
    num_rows = 2416
    urls = read_csv_to_list(file_path, column_name, num_rows)

    token = ''
    for i, url in enumerate(urls):
        owner, name = get_repo_owner_and_name(url)

        res_file_name = 'commits/' + owner + '_' + name + '.csv'

        if os.path.exists(res_file_name):
            print(f'{res_file_name} 已存在，跳过！')
            continue

        all_commits = get_all_commits(owner, name, token)

        write_commits_to_csv(all_commits, res_file_name)

        if i % 10 == 0:
            time.sleep(3)
        elif i % 100 == 0:
            time.sleep(30)
