import re
import os
import myutils

class BoostPyFinder():
    def __init__(self,project_path):
        self.project_path = project_path

        self.res_python = []
        self.res_c_files = []
        self.module_name = []

        # find_module_name
        self.module_pat1 = r'#include\s+<boost/python\.hpp>'
        self.module_pat2 = r'boost/python'
        self.module_pat3 = r'BOOST_PYTHON_MODULE\((\w+)\)'

        self.pkg_names = []

        self.pattern_list1 = []
        self.pattern_list2 = []

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

    #c  module name
    def find_module_name(self):
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp'):
                    file_path = os.path.join(root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()
                        import_flag = False
                        for i, line in enumerate(lines):
                            line = line.strip()

                            if myutils.python_line_is_comment(line):
                                continue

                            if re.search(self.module_pat1, line) or re.search(self.module_pat2, line):
                                import_flag = True

                            match = re.search(self.module_pat3, line)
                            if match:
                                self.res_c_files.append(file_path)
                                name = match.group(1)
                                self.module_name.append(name)

    def extract_import_pkg1(self, module_name, string):
        pattern = rf"import\s+{module_name}\s+as\s+(\w+)"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        else:
            return None

    def extract_import_pkg2(self, module_name,string):
        pattern = rf"from\s+{module_name}\s+import\s+(\w+)"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        else:
            return None

    def find_boost_python(self, module_name):
        pattern_module = fr'\bfrom\s+{module_name}\s+import\s+'
        pattern_module2 = fr'\bimport\s+{module_name}\b'
        pattern_module_name = fr'\b{module_name}\b'

        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()

                        self.pattern_list1.clear()
                        self.pattern_list2.clear()
                        self.pkg_names.clear()
                        # 头文件导入标志
                        import_flag = False

                        for i, line in enumerate(lines):
                            line = line.strip()

                            if myutils.python_line_is_comment(line):
                                continue

                            pkg1 = self.extract_import_pkg1(module_name, line)
                            if pkg1 is not None:
                                self.pkg_names.append(pkg1)
                                import_flag = True

                            pkg2 = self.extract_import_pkg2(module_name, line)
                            if pkg2 is not None:
                                self.pkg_names.append(pkg2)
                                import_flag = True

                            if self.re_match(pattern_module, line) or self.re_match(pattern_module2, line):
                                self.res_python.append((file_path, i + 1, line))
                                import_flag = True


                            if import_flag and self.re_match(pattern_module_name, line, self.pattern_list1):
                                self.res_python.append((file_path, i + 1, line))

                            if len(self.pkg_names) != 0:
                                for pkg_name in self.pkg_names:
                                    pattern_pkg = fr'\b{pkg_name}\b'
                                    if self.re_match(pattern_pkg, line, self.pattern_list1):
                                        self.res_python.append((file_path, i + 1, line))

                            if len(self.pattern_list1) != 0:
                                for pat in self.pattern_list1:
                                    if self.re_match(pat, line, self.pattern_list2):
                                        self.res_python.append((file_path, i + 1, line))

                            if len(self.pattern_list2) != 0:
                                for pat in self.pattern_list2:
                                    if self.re_match(pat, line):
                                        self.res_python.append((file_path, i + 1, line))

    def find_main(self):
        self.find_module_name()
        for mn in self.module_name:
            self.find_boost_python(mn)
        self.res_python = myutils.list_deduplicated(self.res_python)
        self.res_c_files = myutils.list_deduplicated(self.res_c_files)


if __name__ == '__main__':
    pass
    # p_path = []
    # for p in p_path:
    #     bpf = BoostPyFinder(p)
    #     bpf.find_main()
    #     print('================= res_python ========================================================')
    #     for r in bpf.res_python:
    #         print(r)
    #     print('================= res_c_files ========================================================')
    #     for cf in bpf.res_c_files:
    #         print(cf)