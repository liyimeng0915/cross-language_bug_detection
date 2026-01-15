import datetime
import re
import os
import time
import myutils as myutils

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='jython.log',
                    filemode='w')
'''
import org.python.core.Py;
import org.python.core.PyException;
import org.python.core.PyFile;
import org.python.core.PySystemState;
import org.python.util.JLineConsole;
import org.python.util.InteractiveConsole;
import org.python.util.InteractiveInterpreter;




'''


class JythonFinder():
    def __init__(self,project_path):
        self.project_path = project_path

        self.res_java = []
        self.res_python = []

        self.java_call_python_files_test = []
        # 间接一层
        self.pattern_res1 = []
        # 间接二层
        self.pattern_res2 = []

        self.pkgs = []

    def re_match(self, pattern, text, pattern_list=None):

        if re.search(pattern, text) and pattern_list is not None:
            # pattern_temp = re.compile(r'^\s*([a-zA-Z_]\w*)\s*=')
            pattern_temp = re.compile(r'\s*([a-zA-Z_]\w*)\s*=')
            match = pattern_temp.search(text)
            if match:
                pat = fr'\b{re.escape(match.group(1))}\b'
                pattern_list.append(pat)
            return True
        elif re.search(pattern, text):
            return True
        return False

    def extract_pkg_name(self, string):
        pattern = r'org\.python\.\w+\.(\w+)'
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        else:
            return None

    def find_java(self):
        logging.debug(f"{self.project_path} run find_java.")
        for path_root, dirs, files in os.walk(self.project_path):

            # logging.debug(f'= 1 = {path_root}')
            # print(f'= 1 = {path_root}')
            for file in files:
                # print(file)
                if file.endswith('.java'):
                    file_path = os.path.join(path_root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()
                        # 一个文件对应一个列表，使用前清除
                        self.pattern_res1.clear()
                        self.pattern_res2.clear()
                        self.pkgs.clear()

                        for i, line in enumerate(lines):
                            line = line.strip()
                            # 跳过注释
                            if myutils.java_line_starts_with_annotation(line):
                                continue

                            pkg_name = self.extract_pkg_name(line)

                            if pkg_name is not None:
                                # print(f'pkg_name = {pkg_name}--- line = {line}')
                                self.pkgs.append(pkg_name)

                            for pkg in self.pkgs:
                                pat = rf'\b{pkg}\b'
                                if self.re_match(pat, line, self.pattern_res1):
                                    self.res_java.append((file_path, i + 1, line))
                            # 列表去重1
                            self.pattern_res1 = list(set(self.pattern_res1))
                            if len(self.pattern_res1) != 0:
                                for pat in self.pattern_res1:
                                    if self.re_match(pat, line, self.pattern_res2):
                                        self.res_java.append((file_path, i + 1, line))

                            # 列表去重2
                            self.pattern_res2 = list(set(self.pattern_res2))
                            if len(self.pattern_res2) != 0:
                                for pat in self.pattern_res2:
                                    if self.re_match(pat, line):
                                        self.res_java.append((file_path, i + 1, line))


                            # if re.search(r"\borg.python\b",line):
                            #     self.java_call_python_files_test.append(self.project_path)
                            #     logging.info(self.project_path+ '-------' + line + '---'+file_path)

if __name__ == '__main__':
    pass


