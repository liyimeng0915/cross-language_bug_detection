import subprocess
import re

def get_line_numbers_c_cpp(filename,lang_type):

    cmd = "ctags -x --"+lang_type+"-kinds=f " + filename

    output = subprocess.getoutput(cmd,encoding='utf-8')
    lines = output.splitlines()
    line_nums = []
    for line in lines:
        line = line.split(" ")
        char = list(filter(None, line))
        line_num = char[2]
        line_nums.append(int(line_num))
    # 列表排序
    line_nums.sort()
    return line_nums


def process_file_c_cpp(filename, line_num):
    code = ""
    cnt_braket = 0
    found_start = False
    found_end = False

    with open(filename, "r",encoding="utf-8",errors='ignore') as f:
        for i, line in enumerate(f):
            if(i >= (line_num - 1)):
                code += line

                if (not line.startswith("//")) and line.count("{") > 0:
                    found_start = True
                    cnt_braket += line.count("{")

                if (not line.startswith("//")) and line.count("}") > 0:
                    cnt_braket -= line.count("}")

                if cnt_braket == 0 and found_start == True:
                    found_end = True
                    return code, i+1
            
def get_line_numbers_java(filename):
    cmd = "ctags -x --java-kinds=m " + filename

    output = subprocess.getoutput(cmd,encoding='utf-8')
    lines = output.splitlines()
    line_nums = []
    for line in lines:
        line = line.split(" ")
        char = list(filter(None, line))
        line_num = char[2]
        line_nums.append(int(line_num))

    line_nums.sort()
    return line_nums


def get_function_code_java(java_file, start_line):
    with open(java_file, 'r',encoding='utf-8',errors='ignore') as file:
        lines = file.readlines()

    if lines[start_line-1].strip().endswith(";"):
        return lines[start_line-1],start_line

    end_line = -1
    function_code = []
    brace_count = 0
    in_function = False
    in_multiline_comment = False

    for i, line in enumerate(lines[start_line - 1:], start=start_line):
        # Handle multiline comments
        if in_multiline_comment:
            function_code.append(line)
            if '*/' in line:
                in_multiline_comment = False
            continue

        # Check if the current line starts a multiline comment
        if '/*' in line and '*/' not in line:
            in_multiline_comment = True
            function_code.append(line)
            continue

        # Remove single-line comments and multiline comments from the line
        clean_line = re.sub(r'//.*', '', line)
        clean_line = re.sub(r'/\*.*?\*/', '', clean_line)

        if not in_function:
            function_code.append(line)
            if '{' in clean_line:
                in_function = True
                brace_count += clean_line.count('{')
                brace_count -= clean_line.count('}')
                if brace_count == 0:
                    end_line = i
                    break
        else:
            function_code.append(line)
            brace_count += clean_line.count('{')
            brace_count -= clean_line.count('}')
            if brace_count == 0:
                end_line = i
                break

    function_code_str = ''.join(function_code)
    return function_code_str, end_line

def get_line_numbers_python(filename):

    cmd = "ctags -x --python-kinds=f " + filename

    output = subprocess.getoutput(cmd,encoding='utf-8',errors='ignore')
    lines = output.splitlines()
    line_nums = []
    for line in lines:
        line = line.split(" ")
        char = list(filter(None, line))
        line_num = char[2]
        line_nums.append(int(line_num))

    line_nums.sort()
    return line_nums

# 去除末尾空行
def remove_trailing_blank_lines(code: str) -> str:
    lines = code.rstrip().split('\n')
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)

def get_function_code_python(file_path, start_line):
    with open(file_path, 'r',encoding="utf-8",errors='ignore') as file:
        lines = file.readlines()

    function_code = []
    in_function = False
    base_indent = None

    for i, line in enumerate(lines, start=1):
        if i < start_line:
            continue

        stripped_line = line.strip()
        if not stripped_line:
            function_code.append(line)
            continue

        current_indent = len(line) - len(stripped_line)

        if in_function:
            if current_indent <= base_indent and stripped_line:
                break
            function_code.append(line)
        else:
            if i == start_line:
                base_indent = current_indent
                function_code.append(line)
                in_function = True

    func_code1 = ''.join(function_code)
    func_code = remove_trailing_blank_lines(func_code1)
    func_code_len = len(func_code.splitlines())
    end_line = start_line + func_code_len - 1

    return ''.join(func_code), end_line

def get_function_main(filename):


    function_start_end_line_pairs = []

    if filename.endswith('.c'):
        start_lines = get_line_numbers_c_cpp(filename,'c')
        for start_line in start_lines:
            code,end_line = process_file_c_cpp(filename, start_line)
            function_start_end_line_pairs.append((start_line, end_line, code))

    elif filename.endswith('.cpp'):
        start_lines = get_line_numbers_c_cpp(filename, 'c++')
        for start_line in start_lines:
            code, end_line = process_file_c_cpp(filename,start_line)
            function_start_end_line_pairs.append((start_line, end_line, code))

    elif filename.endswith('.java'):
        start_lines = get_line_numbers_java(filename)
        for start_line in start_lines:
            code,end_line = get_function_code_java(filename, start_line)
            function_start_end_line_pairs.append((start_line, end_line, code))


    elif filename.endswith('.py'):
        start_lines = get_line_numbers_python(filename)
        for start_line in start_lines:
            code,end_line = get_function_code_python(filename, start_line)
            function_start_end_line_pairs.append((start_line, end_line, code))
    else:
        print(f'{filename} 文件格式不正确！')
        return None

    return function_start_end_line_pairs
