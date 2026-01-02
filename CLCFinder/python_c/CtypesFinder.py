import re
import os
import myutils

class CtypesFinder():
    def __init__(self, project_path):
        self.project_path = project_path

        self.res_python = []

        self.pattern_list1 = []
        self.pattern_list2 = []
        self.pkg_names = []

        self.test_list = []

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

    def extract_import_pkg1(self, string):
        pattern = rf"import\s+ctypes\s+as\s+(\w+)"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        else:
            return None

    def extract_import_pkg2(self,string):
        pattern = rf"from\s+ctypes\s+import\s+(\w+)"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        else:
            return None

    def find_ctypes(self):
        # pattern1  from ctypes import  import ctypes
        pattern1 = r'\b(from\s+ctypes\s+import\s+|import\s+ctypes\b)'
        # pattern2 cdll.LoadLibrary("libm.dylib")
        pattern2 = r'\.LoadLibrary\b'
        # pattern3 ctypes.c_xxx
        pattern3 = r'\bctypes\.'  # ctypes.xxx
        # pattern5,6  lib = ctypes.CDLL(xxx) 
        pattern4 = r'\bctypes\.CDLL\('
        pattern5 = r'\bctypes\.cdll\('

        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    # print('main    -   '+file)
                    file_path = os.path.join(root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()

                        self.pattern_list1.clear()
                        self.pattern_list2.clear()
                        self.pkg_names.clear()

                        for i, line in enumerate(lines):
                            line = line.strip()
                            if myutils.python_line_is_comment(line):
                                continue
                            # print(file_path+'     - ' + str(i))
                            pkg1 = self.extract_import_pkg1(line)
                            if pkg1 is not None:
                                self.pkg_names.append(pkg1)

                            pkg2 = self.extract_import_pkg2(line)
                            if pkg2 is not None:
                                self.pkg_names.append(pkg2)

                            if len(self.pkg_names) != 0:
                                for pkg_name in self.pkg_names:
                                    pattern_pkg = fr'\b{pkg_name}\b'
                                    if self.re_match(pattern_pkg, line, self.pattern_list1):
                                        self.res_python.append((file_path, i + 1, line))

                            if self.re_match(pattern1, line):
                                self.res_python.append((file_path, i + 1, line))

                            if self.re_match(pattern2, line, self.pattern_list1):
                                self.res_python.append((file_path, i + 1, line))

                            if self.re_match(pattern3, line, self.pattern_list1):
                                self.res_python.append((file_path, i + 1, line))

                            if self.re_match(pattern4, line, self.pattern_list1):
                                self.res_python.append((file_path, i + 1, line))

                            if self.re_match(pattern5, line, self.pattern_list1):
                                self.res_python.append((file_path, i + 1, line))

                            if len(self.pattern_list1) != 0:
                                for pat in self.pattern_list1:
                                    if self.re_match(pat, line, self.pattern_list2):
                                        self.res_python.append((file_path, i + 1, line))

                            if len(self.pattern_list2) != 0:
                                for pat in self.pattern_list2:
                                    if self.re_match(pat, line):
                                        self.res_python.append((file_path, i + 1, line))

    def find_test(self):
        for root, _, files in os.walk(self.project_path):
            for file in files:
                # print('test    -   ' + file)
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()

                        self.pattern_list1.clear()
                        self.pattern_list2.clear()
                        self.pkg_names.clear()

                        for i, line in enumerate(lines):
                            line = line.strip()
                            if myutils.python_line_is_comment(line):
                                continue
                            if re.search(r'\bctypes\b',line):
                                self.test_list.append((file_path, i + 1, line))

        self.test_list = myutils.list_deduplicated(self.test_list)

    def find_main(self):
        self.find_ctypes()
        self.res_python = myutils.list_deduplicated(self.res_python)


if __name__ == '__main__':
    pass
    # p_path = []
    # for p in p_path:
    #     ct = CtypesFinder(p)
    #     ct.find_main()
    #     ct.find_test()
    #     if len(ct.res_python) == 0:
    #         print(p)

    #     print('================= res_python ========================================================')
    #     print(f'    1  ct.res_python的长度为{len(ct.res_python)}')
    #     print(f'    1  ct.test_list的长度为{len(ct.test_list)}')
    #     for r in ct.test_list:
    #         print(r)
    #     print('=================  ct.res_python  ===============================================')
    #     print(f'    2  ct.res_python的长度为{len(ct.res_python)}')
    #     print(f'    2  ct.test_list的长度为{len(ct.test_list)}')
    #     for r in ct.res_python:
    #         print(r)