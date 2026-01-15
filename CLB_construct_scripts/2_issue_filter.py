import os
import re
import pandas as pd
import myconfig


keywords = myconfig.keywords


def read_csv_to_list(filename):
    df = pd.read_csv(filename)
    data_list = df.values.tolist()
    return data_list


def write_list_to_csv(data_list, filename):
    df = pd.DataFrame(data_list)
    df.to_csv(filename, index=False, encoding='utf-8')


def list_files_in_directory(directory_path):
    entries = os.listdir(directory_path)
    files = [file for file in entries if os.path.isfile(os.path.join(directory_path, file))]
    return files


def match_keyword(keyword, text):
    text = str(text)
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    match = pattern.search(text)
    return match is not None


def remove_duplicates(input_list):
    result = []
    for l1 in input_list:
        if l1 not in result:
            result.append(l1)
    return result


def match_issue(filename):
    data_list = read_csv_to_list(filename)

    matched_label_list = []
    matched_title_list = []

    for i,data in enumerate(data_list):
        data_size = len(data_list)

        issue_number = data[0]
        issue_state = data[1]
        issue_title = data[2]
        issue_body = data[3]
        issue_label = data[4]

        if issue_state!= 'closed':
            continue

        for keyword in keywords:
            if match_keyword(keyword, issue_label):
                data.append(f"label matched:{keyword}")
                matched_label_list.append(data)

        for keyword in keywords:
            if match_keyword(keyword, issue_title) or match_keyword(keyword, issue_body):
                data.append(f"title or body matched:{keyword}")
                matched_title_list.append(data)

    return matched_label_list,matched_title_list




def issues_main():
    directory_path = myconfig.issues_directory_path
    res_base_label = myconfig.issues_res_base_label
    res_base_title = myconfig.issues_res_base_title
    res_base_all = myconfig.issues_res_base_all

    file_list = list_files_in_directory(directory_path)
    print(len(file_list))

    for i, file in enumerate(file_list):
        file_path = directory_path + file
        print(f'======== begin ({i}/{len(file_list)}) ==={file_path}==================================')

        label_list, title_list = match_issue(file_path)

        if len(label_list) == 0:

            print(f'{file_path} label_list 为空')
        else:
            label_list = remove_duplicates(label_list)
            write_list_to_csv(label_list, res_base_label + file)

        if len(title_list) == 0:

            print(f'{file_path} title_list 为空')
        else:
            title_list = remove_duplicates(title_list)
            write_list_to_csv(title_list, res_base_title + file)

        if len(label_list) != 0 or len(title_list) != 0:
            res_all = label_list + title_list
            res_all = remove_duplicates(res_all)
            write_list_to_csv(res_all, res_base_all + file)

if __name__ == '__main__':
    issues_main()