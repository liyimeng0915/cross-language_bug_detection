
import os
import re
import subprocess
from collections import OrderedDict


import pandas as pd
from urllib.parse import urlparse
import multiprocessing


def get_all_subfolders(folder_path):
    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subfolders.append(os.path.abspath(item_path))
    return subfolders


def get_all_grandchild_folders(folder_path):
    grandchild_folders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subfolders = get_all_subfolders(item_path)
            grandchild_folders.extend(subfolders)
    return grandchild_folders



def check_and_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"路径 {path} 创建成功")
    else:
        print(f"路径 {path} 已存在，无需创建！")


def tuple_to_string(tuple_data):
    '''
     元组转字符串
    :param tuple_data: 元组数据
    :return:  字符串
    '''
    string_data = ''
    for item in tuple_data:
        string_data += str(item) + ' '
    return string_data.strip()


def list_deduplicated(lst):
    '''
    列表去重
    :param lst: 列表
    :return: 去重之后的列表
    '''
    return list(OrderedDict.fromkeys(lst))


def python_line_is_comment(line):

    stripped_line = line.strip()
    return stripped_line.startswith('#')


def java_line_starts_with_annotation(line):

    if line.startswith('//') or line.startswith('/**') or line.startswith('*') or line.startswith('/***'):
        return True
    else:
        return False

def string2re(str):


    return fr'\b{str}\b'


def execute_cmd(command):

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                print(output.decode().strip())
        return process.poll()
    except Exception as e:
        print("An error occurred:", str(e))

def git_clone_project(github_url, folder):

    cmd = f'git clone {github_url} {folder}'
    execute_cmd(cmd)


def read_csv_column(file_path, column_name):

    try:
        df = pd.read_csv(file_path)
        column_data = df[column_name]
        return column_data
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
    except pd.errors.ParserError:
        print("Error: Failed to parse the CSV file.")
    except KeyError:
        print("Error: Column '{}' not found in the CSV file.".format(column_name))
    except Exception as e:
        print("An error occurred:", str(e))


def get_repository_name(url):

    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return path_parts
        else:
            print("Error: Invalid GitHub URL.")
    except Exception as e:
        print("An error occurred:", str(e))


def clone_csv_url_test():
    # csv文件
    java_cpp_csv_path = 'data/repo_csv/05twoLangs/repo_Java_C++.csv'
    # 本地文件夹
    java_cpp_repo_path = 'D:/mypythondata/repo/repo_java_cpp0'
    # 根据csv文件读取github url
    column_data = read_csv_column(java_cpp_csv_path, 'Repository URL')
    for i in range(0, 460):
        url = column_data[i]
        repo_folder = os.path.join(java_cpp_repo_path,get_repository_name(url)[0],get_repository_name(url)[1])
        git_clone_project(url, repo_folder)
        print('='*100)


def clone_github_repo(csv_file, target_folder, num_repo_right, num_repo_left = 0):
    if not os.path.exists(csv_file):
        print(f'{csv_file} 文件不存在！')
        return
    else:
        print(f'{csv_file} 文件存在，继续运行...')

    if not os.path.exists(target_folder):
        print(f'{target_folder} 路径不存在！')
        os.mkdir(target_folder)
        print(f'{target_folder} 路径创建成功！继续运行...')
    else:
        print(f'{target_folder} 文件存在，继续运行...')

    github_urls = read_csv_column(csv_file, 'Repository URL')

    if num_repo_right > len(github_urls):
        num_repo_right = len(github_urls)

    for i in range(num_repo_left, num_repo_right):
        url = github_urls[i]
        target_folder = os.path.join(target_folder,get_repository_name(url)[0],get_repository_name(url)[1])
        git_clone_project(url,target_folder)
        print(f' {i}/{num_repo_right-num_repo_left}克隆完成！总共第{num_repo_right + 1}个！')


#####################################################################################
def split_path(path):

    directories = []

    path2 = path.replace('\\', '/')
    parts = path2.split('/')

    for i in range(1, len(parts) + 1):
        directories.append('/'.join(parts[:i]))

    return directories
def make_print_to_file(path='./'):
    # path， it is a path for save your log about fuction print
    import os
    import sys
    import datetime
    if not os.path.exists(path):
        os.makedirs(path)

    class Logger(object):
        def __init__(self, filename="Default.log", path="./"):
            self.terminal = sys.stdout
            self.log = open(os.path.join(path, filename), "a", encoding='utf8', )

        def write(self, message):
            process_name = multiprocessing.current_process().name
            self.terminal.write(process_name+": "+message)
            self.log.write(process_name+": "+message)

        def flush(self):
            pass

    fileName = datetime.datetime.now().strftime('day' + '%Y_%m_%d')
    sys.stdout = Logger(fileName + '.log', path=path)
 
    print("*************************************Current time is:", datetime.datetime.now().strftime('%Y-%m-%d-%H:%M'),
          "**************************************")


if __name__ == '__main__':
    pass
    # file_path = "a/b/c/d"
    #
    # # 获取"c"和"d"的名称
    # parts = file_path.split("/")
    # c_name = parts[-2]
    # d_name = parts[-1]
    #
    # # 打印结果
    # print("c的名称:", c_name)
    # print("d的名称:", d_name)

