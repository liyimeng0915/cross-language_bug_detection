import os
import pandas as pd
import time
import sys
import csv
import re

csv.field_size_limit(100000000)

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # 读取表头
        for row in csvreader:
            data_list.append(row)
    return data_list

def remove_duplicates(input_list):
    result = []
    for l1 in input_list:
        if l1 not in result:
            result.append(l1)
    return result

def write_list_to_csv(data_list, filename):

    headers = ['SHA', 'Author', 'Date', 'Message', 'Parent_SHA','Parent_SHA_num','issue_num']
    df = pd.DataFrame(data_list, columns=headers)

    df.to_csv(filename, index=False, encoding='utf-8')

def list_files_in_directory(directory_path):
    entries = os.listdir(directory_path)
    files = [file for file in entries if os.path.isfile(os.path.join(directory_path, file))]

    return files


def extract_num(text):
    match = re.search(r'#(\d+)', str(text))
    if match:
        return match.group(1)
    else:
        return None


def filter_commits(commits_dir, issue_dir, issue_res_dir):

    commit_files = list_files_in_directory(commits_dir)

    sum = 0
    for i, repo_name in enumerate(commit_files):

        commit_file = commits_dir + repo_name
        issue_file = issue_dir + repo_name

        commit_list = read_csv_to_list(commit_file)

        print(f'len(commit_list)  : {len(commit_list)} {commit_file}')

        if os.path.exists(issue_file):
            issue_list = read_csv_to_list(issue_file)
            print(f'len(issue_list)  :{len(issue_list)}  {issue_file}')

            issue_num_list = []
            for issue in issue_list:
                # type 为 str
                issue_num = issue[0]
                issue_num_list.append(issue_num)

            # 符合要求的保存结果
            commit_res = []
            for commit in commit_list:
                commit_issue_num = commit[6]
                if commit_issue_num in issue_num_list:
                    commit_res.append(commit)

            if len(commit_res)!=0:
                sum = sum + len(commit_res)
                print(f"len(res) : {len(commit_res)}")
                # 将结果写入文件
                write_list_to_csv(commit_res, issue_res_dir + repo_name)

        print('*' * 100 + str(i))
        print(f"sum of res : {sum}")


if __name__ == '__main__':


    commits_dir = 'commits_with_issue_num\\'
    issue_dir = 'issues_title2\\'
    issue_res_dir = "commits_filtered_by_issues_title\\"

    filter_commits(commits_dir,issue_dir,issue_res_dir)


