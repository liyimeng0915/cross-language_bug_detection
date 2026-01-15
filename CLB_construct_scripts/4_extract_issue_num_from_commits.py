import re
import csv
import pandas as pd
import os
csv.field_size_limit(100000000)

def extract_num(text):
    match = re.search(r'#(\d+)', str(text)) 
    if match:
        return match.group(1) 
    else:
        return None

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader) 
        for row in csvreader:
            data_list.append(row)
    return data_list

def write_list_to_csv(data_list, filename):
    headers = ['SHA', 'Author', 'Date', 'Message', 'Parent_SHA','Parent_SHA_num','issue_num']
    df = pd.DataFrame(data_list, columns=headers)

    df.to_csv(filename, index=False, encoding='utf-8')

def list_files_in_directory(directory_path):
    entries = os.listdir(directory_path)
    files = [file for file in entries if os.path.isfile(os.path.join(directory_path, file))]
    return files


if __name__ == '__main__':

    commit_files = list_files_in_directory("commits\\")
    sum = 0
    for i,commit_file in enumerate(commit_files):
        commits_list = read_csv_to_list("commits\\"+commit_file)
        res_list = []
        for commit_list in commits_list:
            commit_title = commit_list[3]
            num = extract_num(commit_title)
            if num is not None:
                commit_list.append(num)
                res_list.append(commit_list)

        print(f"res_list size : {len(res_list)}")
        sum = sum + len(res_list)
        write_list_to_csv(res_list, "commits_with_issue_num\\"+commit_file)

    print(f"sum : {sum}")

