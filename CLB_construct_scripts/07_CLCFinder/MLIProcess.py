import csv
import MLI as MLI
import re
import subprocess
import os
import my_config


def git_checkout(repo_path, commit_sha):

    git_command = ["git", "checkout", commit_sha]

    try:
        result = subprocess.run(git_command, cwd=repo_path, text=True, capture_output=True, check=True,encoding='utf-8')

        print("git checkout命令 - stderr:", result.stderr)

    except subprocess.CalledProcessError as e:
        print("-异常,git命令- Error occurred during git checkout:")
        print(e.stderr)
        print("-异常,git命令- Return code:", e.returncode)


def git_diff(repo_path, commit_sha1, commit_sha2):
    git_command = ["git", "diff", commit_sha1, commit_sha2]

    try:
        result = subprocess.run(git_command, cwd=repo_path, text=True, capture_output=True, check=True,encoding='utf-8')
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"- 错误 -：Error occurred during git diff: {e.stderr} (Return code: {e.returncode})"



def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='', encoding="utf-8",errors='ignore') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # 读取表头
        for row in csvreader:
            data_list.append(row)
    return data_list


def list_files_in_directory(directory_path):

    entries = os.listdir(directory_path)
    files = [file for file in entries if os.path.isfile(os.path.join(directory_path, file))]

    return files

def extract_names(filename):
    name_without_extension = filename[:-4]
    a, b = name_without_extension.split('_', 1)

    return a, b


def MLI_res_save_to_csv(data, file_name):
    if len(data) == 0:
        print(f"-提示：- {file_name} 结果大小为 0 ")
        return
    else:
        print(f"------{file_name} 大小：{len(data)}")
    header = ['file_path', 'start_line', 'code']

    with open(file_name, 'w', newline='', encoding="utf-8",errors='ignore') as csvfile:
        csvwriter = csv.writer(csvfile)
        # 写入表头
        csvwriter.writerow(header)
        # 写入数据
        csvwriter.writerows(data)


def read_csv_and_map(file_path):
    url_languages_map = {}

    with open(file_path, mode='r', encoding='ISO-8859-1',errors='ignore') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            url = row['URL']
            languages = row['Languages']  # 假设语言是以逗号分隔的字符串
            url_languages_map[url] = languages

    return url_languages_map


def check_languages(input_str):
    # 定义需要检查的编程语言及其正则表达式模式
    languages = {
        "C": r"\bC\(\d+(\.\d+)?%\)",
        "C++": r"\bC\+\+\(\d+(\.\d+)?%\)",
        "Java": r"\bJava\(\d+(\.\d+)?%\)",
        "Python": r"\bPython\(\d+(\.\d+)?%\)"
    }

    language_presence = {lang: False for lang in languages}

    for lang, pattern in languages.items():
        if re.search(pattern, input_str):
            language_presence[lang] = True

    return language_presence


def get_languages_by_repo_name(owner,repo_name):
    file_path = my_config.repo_all_csv

    url_languages_dict = read_csv_and_map(file_path)

    url = f'https://github.com/{owner}/{repo_name}'

    if url in url_languages_dict:
        languages = url_languages_dict[url]
        res = check_languages(languages)
    else:
        res = {'C': True, 'C++': True, 'Java': True, 'Python': True}

    return res


def MLI_execute(repo_path,owner,repo_name,commit_sha,flags):
    MLI_res_dir = my_config.MLI_res_dir

    languages_dict = get_languages_by_repo_name(owner,repo_name)

    res_jna = []
    res_jni = []

    res_cffi = []
    res_ctypes = []
    res_boostpy = []
    res_pythonc = []
    res_pybind11 = []
    res_swig = []

    res_java_python = []

    csv_dir = f"{MLI_res_dir}{owner}/{repo_name}/{commit_sha}/"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    if (languages_dict['C'] or languages_dict['C++']) and languages_dict['Java']:
        if flags['jna']:
            res_jna = MLI.process_java_c_jna(repo_path)
            MLI_res_save_to_csv(res_jna, csv_dir + "jna.csv")
        if flags['jni']:
            res_jni = MLI.process_java_c_jni(repo_path)
            MLI_res_save_to_csv(res_jni, csv_dir + "jni.csv")

    if (languages_dict['C'] or languages_dict['C++']) and languages_dict['Python']:
        if flags['cffi']:
            res_cffi = MLI.process_python_c_cffi(repo_path)
            MLI_res_save_to_csv(res_cffi, csv_dir + "cffi.csv")
        if flags['ctypes']:
            res_ctypes = MLI.process_python_c_ctypes(repo_path)
            MLI_res_save_to_csv(res_ctypes, csv_dir + "ctypes.csv")
        if flags['boostpy']:
            res_boostpy = MLI.process_python_c_boostpy(repo_path)
            MLI_res_save_to_csv(res_boostpy, csv_dir + "boostpy.csv")
        if flags['pythonc']:
            res_pythonc = MLI.process_python_c_pythonc(repo_path)
            MLI_res_save_to_csv(res_pythonc, csv_dir + "pythonc.csv")
        if flags['pybind11']:
            res_pybind11 = MLI.process_python_c_pybind11(repo_path)
            MLI_res_save_to_csv(res_pybind11, csv_dir + "pybind11.csv")

        if flags['swig']:
            res_swig = MLI.process_python_c_swig(repo_path)
            MLI_res_save_to_csv(res_swig, csv_dir + "swig.csv")

    if languages_dict['Java'] and languages_dict['Python'] and flags['java_python']:
        res_java_python = MLI.process_java_python(repo_path)
        MLI_res_save_to_csv(res_java_python, csv_dir + "java_python.csv")

    return res_jna,res_jni,res_cffi,res_ctypes,res_boostpy,res_pythonc,res_pybind11,res_swig,res_java_python


if __name__ == '__main__':
    pass
