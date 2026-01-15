

import pandas as pd
import csv
import re
import os
import sys
import datetime
import myutils


def make_print_to_file(path='./'):

    if not os.path.exists(path):
        os.makedirs(path)

    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            self.terminal = sys.stdout
            self.log = open(os.path.join(path, filename), "a", encoding='utf8', )

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

    fileName = datetime.datetime.now().strftime('day' + '%Y_%m_%d')
    sys.stdout = Logger(fileName + '.log', path=path)
    print("*************************************Current time is:", datetime.datetime.now().strftime('%Y-%m-%d-%H:%M'),
          "**************************************")

def remove_duplicates(input_csv_path, output_csv_path, column_name):
    df = pd.read_csv(input_csv_path)

    df_unique = df.drop_duplicates(subset=[column_name])

    df_unique.to_csv(output_csv_path, index=False)

    print(f"去重后的数据已保存到: {output_csv_path}")

# 1
def deduplicated():
    directory = "final_res\\"
    csv_file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                # 构建文件的完整路径
                file_path = os.path.join(root, file)
                csv_file_list.append(file_path)

    for i, csv_file_path in enumerate(csv_file_list):
        csv_file_path = csv_file_path.replace('\\',
                                              '\\\\') 
        file_name = os.path.basename(csv_file_path)

        dir_name = os.path.dirname(csv_file_path)
        output_dir_name = dir_name.replace('final_res',
                                           'final_res_deduplicated')
        output_csv_file_path = output_dir_name + '\\\\' + file_name 

        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name)

        column_name = 'func_code'

        remove_duplicates(csv_file_path, output_csv_file_path, column_name)
# 2
def merge_all_csv():
    folder_path = 'final_res_deduplicated\\'
    output_csv_path = 'final_res_deduplicated_all\\merge_all.csv'  

    dir_name = os.path.dirname(output_csv_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    dfs = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"读取文件: {file_path}")

                df = pd.read_csv(file_path)

                dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df.to_csv(output_csv_path, index=False)
    print(f"所有CSV文件已合并并保存到: {output_csv_path}")


def read_csv_to_list(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            data.append(row)
    return data

def del_None():
    output_csv_path = 'final_res_deduplicated_all\\merge_all.csv'
    data_list = read_csv_to_list(output_csv_path)

    df = pd.read_csv(output_csv_path, nrows=0)
    header = df.columns.tolist() 

    print(len(data_list))
    res = []
    test1 = []
    test2 = []
    for i,item in enumerate(data_list):
        file_path = item[0]
        commit_sha = item[1]
        commit_parent_sha = item[2]
        mli_line_num = item[3]
        mli_line_code = item[4]
        func_start_line = item[5]
        func_end_line = item[6]
        func_code = item[7]
        func_code_merged = item[8]
        func_before = item[9]
        func_after = item[10]

        if len(func_before) == 0 or func_before is None:
            test1.append(item)
            continue

        if len(func_after) == 0:
            test2.append(item)
            continue

        if func_before == func_after:
            continue

        res.append(item)

    res_file_path = 'final_res_deduplicated_all\\merge_all_without_None.csv'
    df = pd.DataFrame(res, columns=header)
    df.to_csv(res_file_path, index=False, encoding='utf-8')

    test1_file_path = 'final_res_deduplicated_all\\test1.csv'
    df = pd.DataFrame(test1, columns=header)
    df.to_csv(test1_file_path, index=False, encoding='utf-8')


def remove_comments_py(code: str) -> str:
    multi_line_pattern = r'(\w+)\s*=\s*(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')'
    single_line_pattern = r'(\w+)\s*=\s*(\".*?\"|\'.*?\')'

    replacements = {}
    placeholder_index = 0

    def replace_with_placeholder(match):
        nonlocal placeholder_index
        var_name = match.group(1)
        content = match.group(2)
        placeholder = f'__STRING_PLACEHOLDER_{placeholder_index}__'
        replacements[placeholder] = f'{var_name} = {content}'
        placeholder_index += 1
        return placeholder

    def replace_with_placeholder_single(match):
        nonlocal placeholder_index
        var_name = match.group(1)
        content = match.group(2)
        placeholder = f'__STRING_PLACEHOLDER_{placeholder_index}__'
        replacements[placeholder] = f'{var_name} = {content}'
        placeholder_index += 1
        return placeholder

    code = re.sub(multi_line_pattern, replace_with_placeholder, code, flags=re.DOTALL)
    code = re.sub(single_line_pattern, replace_with_placeholder_single, code)
    code = re.sub(r'\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'', '', code, flags=re.DOTALL)
    code = re.sub(r'#.*', '', code)
    code = re.sub(r'\n\s*\n', '\n', code)

    for placeholder, original in replacements.items():
        code = code.replace(placeholder, original)

    return code


def remove_comments_java(code):
    single_line_comment_pattern = r'//.*'
    multi_line_comment_pattern = r'/\*.*?\*/'

    multi_line_comments = re.findall(multi_line_comment_pattern, code, flags=re.DOTALL)
    single_line_comments = re.findall(single_line_comment_pattern, code)

    code = re.sub(multi_line_comment_pattern, '', code, flags=re.DOTALL)
    code = re.sub(single_line_comment_pattern, '', code)

    lines = code.splitlines()
    non_blank_lines = [line for line in lines if line.strip() != '']
    cleaned_code = "\n".join(non_blank_lines)

    removed_comments = "\n".join(multi_line_comments + single_line_comments)

    return cleaned_code


def remove_comments_c(code):
    single_line_comment_pattern = r'//.*'
    multi_line_comment_pattern = r'/\*.*?\*/'

    multi_line_comments = re.findall(multi_line_comment_pattern, code, flags=re.DOTALL)
    single_line_comments = re.findall(single_line_comment_pattern, code)

    code = re.sub(multi_line_comment_pattern, '', code, flags=re.DOTALL)
    code = re.sub(single_line_comment_pattern, '', code)

    lines = code.splitlines()
    non_blank_lines = [line for line in lines if line.strip() != '']
    cleaned_code = "\n".join(non_blank_lines)

    removed_comments = "\n".join(multi_line_comments + single_line_comments)

    return cleaned_code




if __name__ == '__main__':
    # 1
    # deduplicated()
    # 2
    # merge_all_csv()
    # 3
    # del_None()

    make_print_to_file()
    input_csv_path = 'final_res_deduplicated_all\\merge_all_without_None.csv'
    data_list = read_csv_to_list(input_csv_path)

    df = pd.read_csv(input_csv_path, nrows=0)  # 读取表头行
    header = df.columns.tolist()  # 获取表头列名列表

    res = []

    for i, item in enumerate(data_list):

        file_path = item[0]
        commit_sha = item[1]
        commit_parent_sha = item[2]
        mli_line_num = item[3]
        mli_line_code = item[4]
        func_start_line = item[5]
        func_end_line = item[6]
        func_code = item[7]
        func_code_merged = item[8]
        func_before = item[9]
        func_after = item[10]

        if file_path.endswith('.py'):
            func_before_del_comments = remove_comments_py(func_before)
            func_after_del_comments = remove_comments_py(func_after)

        elif file_path.endswith('.java'):
            func_before_del_comments = remove_comments_java(func_before)
            func_after_del_comments= remove_comments_java(func_after)

        else:
            func_before_del_comments = remove_comments_c(func_before)
            func_after_del_comments = remove_comments_c(func_after)

        if len(func_before_del_comments) != 0 and func_before_del_comments != func_after_del_comments:
            res.append((item[0],item[1],item[2],item[3],item[4],item[5],item[6],
                        item[7],item[8],item[9],item[10],
                        func_before_del_comments, func_after_del_comments))
        else:
            print("数据处理！")


    print(len(res))
    headers = ['file_path','commit_sha','commit_parent_sha','mli_line_num',
               'mli_line_code','func_start_line','func_end_line','func_code',
               'func_code_merged','func_before','func_after','func_before_del_comments','func_after_del_comments']

    res_file_path = 'final_res_deduplicated_all\\merge_all_without_None_del_comments.csv'

    myutils.write_data_to_csv(res,headers,res_file_path)











