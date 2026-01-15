
import re
import subprocess
import os
import FunctionGetter as FG
import git_utils

def merge_patch_file(filename,patch,res_file_path):


    res_file_dir = os.path.dirname(res_file_path)
    if not os.path.exists(res_file_dir):
        os.makedirs(res_file_dir)
    if not os.path.exists(filename):
        return
    with open(filename, 'r', encoding="utf-8",errors='ignore') as file:
        file_content = file.readlines()

    file_content2 = []

    patch_lines = patch.strip().split('\n')

    pattern = r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@'

    new_start = []
    new_count = []

    for line in patch_lines:
        match = re.match(pattern, line)
        if line.startswith('@@'):
            if match:
                new_start.append(int(match.group(3)))
                new_count.append(int(match.group(4)))
        else:
            continue

    idx = 0
    i = 0
    while i < len(file_content):
        if idx < len(new_start) and i == new_start[idx] - 1:
            flag = False
            cnt = 0
            for j in range(len(patch_lines)):
                if patch_lines[j].startswith('@@'):
                    if flag:
                        break
                    else:
                        flag = True
                        continue
                else:
                    file_content2.append(patch_lines[j] + '\n')
                cnt = j + 1

            for _ in range(cnt):
                patch_lines.pop(0)

            i += new_count[idx] - 1
            idx += 1
        else:
            file_content2.append(file_content[i])
        i += 1

    with open(res_file_path, 'w', encoding="utf-8",errors='ignore') as file:
        for line in file_content2:
            file.write(line)


def get_file_diff(path, commit_sha1, commit_sha2, file_path):
    original_cwd = os.getcwd()

    try:
        os.chdir(path)

        result = subprocess.run(
            ['git', 'diff', commit_sha1, commit_sha2, '--', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    finally:
        os.chdir(original_cwd)


def get_modified_files(path, commit_sha1, commit_sha2):
    original_cwd = os.getcwd()

    try:
        os.chdir(path)

        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=M', commit_sha1, commit_sha2],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            return [line for line in result.stdout.splitlines() if line]
        else:
            return f"Error: {result.stderr}"
    finally:
        os.chdir(original_cwd)


def process_diff(diff_content):

    if not isinstance(diff_content, str) or len(diff_content)<=0:
        return ''
    lines = diff_content.splitlines()

    first_diff_index = next((i for i, line in enumerate(lines) if line.startswith('@@')), None)

    if first_diff_index is not None:
        return '\n'.join(lines[first_diff_index:])
    else:
        return ''


def merge_file_diff(repo_path, res_repo_path, commit_sha_parent, commit_sha):
    modified_files = get_modified_files(repo_path, commit_sha_parent, commit_sha)
    git_utils.git_checkout(repo_path, commit_sha)
    for modified_file in modified_files:
        file_diff = get_file_diff(repo_path, commit_sha_parent, commit_sha, modified_file)

        file_diff = process_diff(file_diff)
        merge_patch_file(repo_path + modified_file, file_diff, res_repo_path + modified_file)


def get_line_num(file_name):
    plus_lines = []
    minus_lines = []

    with open(file_name, 'r',encoding="utf-8",errors='ignore') as file:
        for i, line in enumerate(file, start=1):
            stripped_line = line.lstrip()  # 去除行前的空白字符
            if stripped_line.startswith('-') and not line.startswith(' '):
                minus_lines.append(i)
            elif stripped_line.startswith('+') and not line.startswith(' '):
                plus_lines.append(i)

    return plus_lines, minus_lines


def replace_symbols_and_save(input_file_path, output_file_path):
    with open(input_file_path, 'r',encoding="utf-8",errors='ignore') as infile, open(output_file_path, 'w',encoding="utf-8",errors='ignore') as outfile:
        for line in infile:
            if line.startswith('+') or line.startswith('-'):
                outfile.write(' ' + line[1:])
            else:
                outfile.write(line)




if __name__ == '__main__':
    # 参数1 当前commit sha
    commit_sha = '5b51ca0b921a3f1748c430afc40216870be506e3'
    # 参数2 当前commit 的parent sha
    commit_sha_parent = '377352d956df82311dc1fb203218d181d6aada47'

    # 参数3 仓库名称
    reponame = 'react-native'

    # 参数4 所有仓库存放的目录
    repo_base_dir = '/mnt/mypythondata/test/repo/'

    # 参数5 当前仓库的路径
    repo_path = repo_base_dir + reponame + '/'

    # 合并文件的结果保存路径
    # 参数6 处理结果存放的目录
    repo_res_base_dir = '/mnt/mypythondata/test/repo_res/'

    res_repo_path = repo_res_base_dir + 'merged_files/' + reponame +'/' + commit_sha
    # res_repo_path = f'/mnt/mypythondata/test/repo_res/merged_files/{reponame}/{commit_sha}/'

    # 将合并文件去掉 + - 符号的文件保存路径
    res_repo_path_without_plus_minus_files = f'{repo_res_base_dir}/without_plus_minus_files/{reponame}/{commit_sha}/'
    # res_repo_path_without_plus_minus_files = f'/mnt/mypythondata/test/repo_res/without_plus_minus_files/{reponame}/{commit_sha}/'

    # 获取修改的文件相对路径
    modified_files = get_modified_files(repo_path, commit_sha_parent, commit_sha)

    # 合并文件
    merge_file_diff(repo_path, res_repo_path, commit_sha_parent, commit_sha)

    # []
    res_list = []
    for modified_file in modified_files:
        # 获取+ - 所在行号
        plus_lines, minus_lines = get_line_num(res_repo_path + modified_file)

        # 创建文件夹
        if not os.path.exists(os.path.dirname(res_repo_path_without_plus_minus_files + modified_file)):
            os.makedirs(os.path.dirname(res_repo_path_without_plus_minus_files+modified_file))

        # 去掉 + - 
        replace_symbols_and_save(res_repo_path + modified_file, res_repo_path_without_plus_minus_files + modified_file)

        file_name = res_repo_path_without_plus_minus_files + modified_file
        if file_name.endswith('java') or file_name.endswith('cpp') or file_name.endswith('c') or file_name.endswith('py'):
            res = FG.get_function_main(file_name)
        else:
            print(file_name)
            print('非java、c、cpp、python文件，跳过处理')
            continue

        for r in res:
            print(r[0])
            print(r[1])
            print(r[2])

