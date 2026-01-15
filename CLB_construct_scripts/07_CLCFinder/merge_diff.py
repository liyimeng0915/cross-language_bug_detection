
import re
import subprocess
import os
import FunctionGetter as FG

def git_checkout(repo_path, commit_sha):
    # 指定要执行的git命令
    git_command = ["git", "checkout", commit_sha]

    try:
        # 切换到指定路径并执行git命令
        result = subprocess.run(git_command, cwd=repo_path, text=True, capture_output=True, check=True,encoding='utf-8')

        # 输出结果
        # print("------git命令:stdout:", result.stdout)
        print("------git命令:stderr:", result.stderr)

    except subprocess.CalledProcessError as e:
        print("-异常,git命令- Error occurred during git checkout:")
        print(e.stderr)
        print("-异常,git命令- Return code:", e.returncode)


def merge_patch_file(filename,patch,res_file_path):
    '''

    :param filename: 文件路径
    :param patch: patch 信息
    :param res_file_path:
    :return:
    '''

    res_file_dir = os.path.dirname(res_file_path)
    if not os.path.exists(res_file_dir):
        os.makedirs(res_file_dir)

    with open(filename, 'r',encoding="utf-8",errors='ignore') as file:
        file_content = file.readlines()

    file_content2 = []

    patch_lines = patch.strip().split('\n')

    pattern = r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@'

    new_start = []
    new_count = []

    # 获取patch中信息
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
        # print("i=" + str(i))
        if idx < len(new_start) and i == new_start[idx] - 1:
            # print('读取patch...')
            flag = False  # 第一次遇到@@ 为false，第二次遇到为true
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
            # print(patch_lines)

            i += new_count[idx] - 1
            # print('####'+file_content[i])
            idx += 1
        else:
            file_content2.append(file_content[i])
        i += 1
    # print('*' * 100)

    with open(res_file_path, 'w') as file:
        for line in file_content2:
            file.write(line)


def get_file_diff(path, commit_sha1, commit_sha2, file_path):
    # 保存当前工作目录
    original_cwd = os.getcwd()

    try:
        # 切换到指定的仓库路径
        os.chdir(path)

        # 执行 git diff 命令
        result = subprocess.run(
            ['git', 'diff', commit_sha1, commit_sha2, '--', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # 检查命令是否成功执行
        if result.returncode == 0:
            # 返回差异信息
            return result.stdout
        else:
            # 返回错误信息
            return f"Error: {result.stderr}"
    finally:
        # 切换回原始工作目录
        os.chdir(original_cwd)


def get_modified_files(path, commit_sha1, commit_sha2):
    # 保存当前工作目录
    original_cwd = os.getcwd()

    try:
        # 切换到指定的仓库路径
        os.chdir(path)

        # 执行 git diff --name-only --diff-filter=M 命令
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=M', commit_sha1, commit_sha2],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # 检查命令是否成功执行
        if result.returncode == 0:
            # 返回被修改的文件名列表（去除空行）
            return [line for line in result.stdout.splitlines() if line]
        else:
            # 返回错误信息
            return f"Error: {result.stderr}"
    finally:
        # 切换回原始工作目录
        os.chdir(original_cwd)


def process_diff(diff_content):
    # 按行拆分 diff 内容
    lines = diff_content.splitlines()

    # 查找第一个以 @@ 开头的行的索引
    first_diff_index = next((i for i, line in enumerate(lines) if line.startswith('@@')), None)

    # 如果找到了，以 @@ 开头的行，则返回从该行开始的内容，否则返回空字符串
    if first_diff_index is not None:
        return '\n'.join(lines[first_diff_index:])
    else:
        return ''


def merge_file_diff(repo_path, res_repo_path, commit_sha_parent, commit_sha):
    '''
    将 file 和 diff 文件结合，将结果存在指定路径
    :param repo_path: 被处理的仓库的路径
    :param res_repo_path: 结果存放的仓库文件夹
    :param commit_sha_parent:
    :param commit_sha:
    :return: 无
    '''
    # 1、 获取该仓库修改的文件路径
    modified_files = get_modified_files(repo_path, commit_sha_parent, commit_sha)
    # 2、 将该仓库切换到指定commit状态
    git_checkout(repo_path, commit_sha)
    # 3、
    for modified_file in modified_files:
        file_diff = get_file_diff(repo_path, commit_sha_parent, commit_sha, modified_file)

        file_diff = process_diff(file_diff)

        merge_patch_file(repo_path + modified_file, file_diff, res_repo_path + modified_file)
        print("*" * 50)


def get_line_num(file_name):
    plus_lines = []
    minus_lines = []

    with open(file_name, 'r') as file:
        for i, line in enumerate(file, start=1):
            stripped_line = line.lstrip()  # 去除行前的空白字符
            if stripped_line.startswith('-') and not line.startswith(' '):
                minus_lines.append(i)
            elif stripped_line.startswith('+') and not line.startswith(' '):
                plus_lines.append(i)

    return plus_lines, minus_lines


def replace_symbols_and_save(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        for line in infile:
            if line.startswith('+') or line.startswith('-'):
                # 用空格替换开头的符号，并写入输出文件
                outfile.write(' ' + line[1:])
            else:
                # 如果行不以 + 或 - 开头，直接写入输出文件
                outfile.write(line)




if __name__ == '__main__':


    # # https://github.com/facebook/react-native/commit/5b51ca0b921a3f1748c430afc40216870be506e3
    commit_sha = '5b51ca0b921a3f1748c430afc40216870be506e3'
    commit_sha_parent = '377352d956df82311dc1fb203218d181d6aada47'

    reponame = 'react-native'

    repo_path = f'E:\\test3\\{reponame}\\'
    res_repo_path = f'E:\\repo_res\\merged_files\\{reponame}\\{commit_sha}\\'

    res_repo_path_without_plus_minus_files = f'E:\\repo_res\\without_plus_minus_files\\{reponame}\\{commit_sha}\\'

    modified_files = get_modified_files(repo_path, commit_sha_parent, commit_sha)

    merge_file_diff(repo_path, res_repo_path, commit_sha_parent, commit_sha)

    for modified_file in modified_files:

        plus_lines, minus_lines = get_line_num(res_repo_path+modified_file)

        if not os.path.exists(os.path.dirname(res_repo_path_without_plus_minus_files+modified_file)):
            os.makedirs(os.path.dirname(res_repo_path_without_plus_minus_files+modified_file))

        replace_symbols_and_save(res_repo_path+modified_file,res_repo_path_without_plus_minus_files+modified_file)

    for modified_file in modified_files:
        file_name = res_repo_path_without_plus_minus_files+modified_file
        res = FG.get_function_main(file_name)
        print(res)
        break





