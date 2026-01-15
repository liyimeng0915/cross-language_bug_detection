import DiffProcess as DP
import MLIProcess as MP
import FunctionGetter as FG
import os
import csv
import my_config
import threading
from myutils import make_print_to_file
import multiprocessing
import MLIProcess


def extract_code_segment(file_path, start_line, end_line):
    with open(file_path, 'r', encoding="utf-8",errors='ignore') as file:
        lines = file.readlines()

    result = []
    line_counter = 1
    for line in lines:
        if start_line <= line_counter <= end_line:
            result.append(line)

        if line.startswith('-'):
            continue
        line_counter = line_counter+1

    return ''.join(result)


def merge_lists(*lists):
    merged_list = []
    for lst in lists:
        if lst:
            merged_list.extend(lst)
    return merged_list


def list_intersection(list1, list2):
    return [item for item in list1 if item in list2]


def get_function_before(text):
    lines = text.splitlines()
    processed_lines = []
    for line in lines:
        if not line.startswith('+'):
            if line.startswith('-'):
                line = ' ' + line[1:]
            processed_lines.append(line)

    return '\n'.join(processed_lines)


def get_function_after(text):

    lines = text.splitlines()


    processed_lines = []
    for line in lines:
        if not line.startswith('-'):
            # 替换行首的'-'为' '
            if line.startswith('+'):
                line = ' ' + line[1:]
            processed_lines.append(line)

    # 将处理后的行合并成一个多行字符串
    return '\n'.join(processed_lines)


def write_tuples_to_csv(data, filename):

    headers = ['file_path', 'commit_sha','commit_parent_sha','mli_line_num', 'mli_line_code', 'func_start_line', 'func_end_line', 'func_code', 'func_code_merged', 'func_before', 'func_after']

    # 打开文件并写入数据
    with open(filename, mode='w', newline='',encoding="utf-8") as file:
        writer = csv.writer(file)
        # 写入表头
        writer.writerow(headers)
        # 写入数据行
        writer.writerows(data)


def get_subpath_from_fifth_slash(path):

    slash_count = 0
    for i, char in enumerate(path):
        if char == '/':
            slash_count += 1
            if slash_count == 5:
                return path[i+1:]  
    return "" 


def check_lines(text):

    lines = text.split('\n')
    found = False
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            print(line)
            found = True
    return found


def getdata_main(commits_list, start, end):

    process_name = multiprocessing.current_process().name
    commit_dir = my_config.commit_dir
    repo_base_dir = my_config.repo_dir
    repo_res_base_dir = my_config.repo_res_dir

    for i, commit_csv in enumerate(commits_list):

        if os.path.exists(f"final_res_processed\\{i}"):
            continue

        if not (start <= i <= end): continue

        # 根据文件名分离出 owner 和 repo_name
        owner, repo_name = MP.extract_names(commit_csv)
        print(f"序号：{i},名称{owner}/{repo_name}")
        # commit的csv文件绝对路径
        commit_path = commit_dir + commit_csv

        # 将commit的csv文件信息读到列表中
        commit_infos = MP.read_csv_to_list(commit_path)

        # 被处理仓库的绝对路径
        repo_path = repo_base_dir + owner + "/" + repo_name + '/'

        MLI_flags = {'jni': True,  # 1
                     'jna': True,  # 2
                     'cffi': True,  # 3
                     'ctypes': True,  # 4
                     'boostpy': True,  # 5
                     'pybind11': True,  # 6
                     'pythonc': True,  # 7
                     'swig': True,  # 8
                     'java_python': True  # 9
                     }

        for j, commit_info in enumerate(commit_infos):
            if not os.path.exists(f"final_res_processed_commit\\{i}\\{j-1}\\") and j >0:
                os.makedirs(f"final_res_processed_commit\\{i}\\{j-1}\\")
            # 11
            if os.path.exists(f"final_res_processed_commit\\{i}\\{j}\\"):
                continue

            print(f"thread_num:{process_name}  当前第{i+1} - {j}/{len(commit_infos)}个commit，commit_sha:{commit_info[0]}")

            commit_parent_sha = commit_info[4]
            commit_sha = commit_info[0]


            reponame = f'{owner}/{repo_name}'

            res_repo_path = f'{repo_res_base_dir}merged_files/{reponame}/{commit_sha}/'

 
            has_code_file_flag = False
            modified_files = DP.get_modified_files(repo_path, commit_parent_sha, commit_sha)

            for modified_file in modified_files:
                if modified_file.endswith('.java') or modified_file.endswith('.c') or modified_file.endswith(
                        '.cpp') or modified_file.endswith('.py'):
                    has_code_file_flag = True
  
            if not has_code_file_flag:
                continue

            MP.git_checkout(repo_path, commit_sha)

            res_jna, res_jni, res_cffi, res_ctypes, res_boostpy, res_pythonc, res_pybind11, res_swig, res_java_python = MP.MLI_execute(
                repo_path, owner, repo_name, commit_sha,MLI_flags)
            # 1 jni
            if len(res_jna) == 0:#1
                MLI_flags['jni'] = False
            else:
                MLI_flags['jni'] = True
            # 2 jna
            if len(res_jni) == 0:#2
                MLI_flags['jna'] = False
            else:
                MLI_flags['jna'] = True
            # cffi
            if len(res_cffi) == 0:#3
                MLI_flags['cffi'] = False
            else:
                MLI_flags['cffi'] = True

            # 4 ctypes
            if len(res_ctypes) == 0:#4
                MLI_flags['ctypes'] = False
            else:
                MLI_flags['ctypes'] = True

            # 5 boostpy
            if len(res_boostpy) == 0:#5
                MLI_flags['boostpy'] = False
            else:
                MLI_flags['boostpy'] = True

            # 6 pybind11
            if len(res_pybind11) == 0:#6
                MLI_flags['pybind11'] = False
            else:
                MLI_flags['pybind11'] = True
            # 7 pythonc
            if len(res_pythonc) == 0:  # 7
                MLI_flags['pythonc'] = False
            else:
                MLI_flags['pythonc'] = True
            # 8 swig
            if len(res_swig) == 0:#8
                MLI_flags['swig'] = False
            else:
                MLI_flags['swig'] = True
            # 9 java_python
            if len(res_java_python) == 0:#9
                MLI_flags['java_python'] = False
            else:
                MLI_flags['java_python'] = True

            print(f"thread_num:{process_name} 3.1 合并结果。。。")

            MLI_res_all = merge_lists(res_jna, res_jni, res_cffi, res_ctypes, res_boostpy, res_pythonc, res_pybind11,
                                      res_swig, res_java_python)
            if len(MLI_res_all) == 0:
                print(f"{reponame} 多语言结果为空")
                # os.makedirs(f"D:\\mypythondata\\final_res_processed_title\\NO_MLI\\{i}\\{owner}#{repo_name}")
                os.makedirs(f"D:\\mypythondata\\final_res_processed\\NO_MLI\\{i}\\{owner}#{repo_name}")
                break


            MLI_res_func = [] 
            for mli_res in MLI_res_all:
                file_path = mli_res[0]
                mli_line_num = mli_res[1]
                mli_line_code = mli_res[2]

                function_info = FG.get_function_main(file_path)

                for func in function_info:
                    start_line = func[0]
                    end_line = func[1]
                    func_code = func[2]

                    if start_line <= mli_line_num <= end_line:
                        MLI_res_func.append((file_path, mli_line_num, mli_line_code, start_line, end_line, func_code))

            try:
                DP.merge_file_diff(repo_path, res_repo_path, commit_parent_sha, commit_sha)
            except Exception:
                print(Exception)
                continue
            final_function_code_list = [] 
            for mli_func in MLI_res_func:  # (file_path,mli_line_num,mli_line_code,start_line,end_line,func_code)

                file_name2 = res_repo_path + get_subpath_from_fifth_slash(mli_func[0])
                start_line = mli_func[3]
                end_line = mli_func[4]

                # 当这个文件在仓库中不存在时，跳过
                if not os.path.exists(file_name2):
                    continue
                else:
                    print("!!!!6666666666666666666666666666666666666666")

                function_res = extract_code_segment(file_name2, start_line, end_line)

                if not check_lines(function_res):
                    continue
                # 删除+号行，并将行首的- 替换成空格，获得修改前的函数
                func_before = get_function_before(function_res)
                # 删除-号行，并将行首的+ 替换成空格,
                func_after = get_function_after(function_res)

                final_function_code_list.append((mli_func[0],commit_sha, commit_parent_sha,mli_func[1], mli_func[2], mli_func[3], mli_func[4],
                                                 mli_func[5], function_res, func_before, func_after))

            if len(final_function_code_list) != 0:

                final_res_dir = my_config.final_res_dir

                final_res_path = f"{final_res_dir}{owner}/{repo_name}/"

                if not os.path.exists(final_res_path):
                    os.makedirs(final_res_path)

                final_res_csv = final_res_path + f"{commit_sha}.csv"

                write_tuples_to_csv(final_function_code_list, final_res_csv)

                print(f"thread_num:{process_name} :写入数据成功，最终结果大小为：", len(final_function_code_list))

        os.makedirs(f"D:\\mypythondata\\final_res_processed\\{i}")


if __name__ == '__main__':
    """
        思路：
        在仓库最新的状态下，进行多语言扫描，如果没有结果则跳过该仓库
    
    """

    make_print_to_file(path='./log/print_content')
    commit_dir = my_config.commit_dir
    commits_list = MP.list_files_in_directory(commit_dir)
    processes = []

    process1 = multiprocessing.Process(target=getdata_main, args=(commits_list, 0, 100), name='process-1-')

    processes.append(process1)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("All threads have finished.")


