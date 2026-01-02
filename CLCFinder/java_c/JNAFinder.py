import datetime
import re
import os
import time
import myutils

# import logging
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     filename='JNAFinder.log',
#                     filemode='w')



class JNAFinder():
    def __init__(self,project_path):
        self.project_path = project_path
        # print(self.project_path)
        self.res_java = []

        self.res_class = []
        self.res_jna_file = []

        self.java_pattern = []
        self.c_pattern = []

        # 间接一层
        self.pattern_res1 = []
        # 间接两层
        self.pattern_res2 = []

        # 1
        self.pattern_jna = r'com.sun.jna'
        # 1 用以保存 com.sun.jna.xxx 的xxx名称
        self.pattern_jna_packages = []
        # 1
        self.p_native_load = r'\bNative.load\b'

        # 2 find_interface_name_exd_Library
        self.p_ext_Library_interfaces = [] 
        # 3 find_classes_name_imp_Library
        self.p_imp_Library_classes = [] 

        # 2 find_class_name_imp_NativeMapped
        self.p_imp_NativeMapped_classes = []  

        # 2 find_class_name_exd_Structure
        self.p_exd_Structure_classes = []

        # self.jna_path_test = []

        self.test_2_lines = []
        self.test_1_1_lines = []
        self.test_1_2_lines = []
        self.test_1_3_lines = []

    def extract_jna_pkg_name(self, input_string):
        # 定义正则表达式模式
        pattern = r'com\.sun\.jna\.(\w+)'
        match = re.search(pattern, input_string)
        if match:
            # 返回匹配的组内容，即xxx
            return match.group(1)
        else:
            return None

    def find_interface_name_exd_Library(self, text):
        pattern = r'interface\s+(\w+)\s+extends\s+Library\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    def find_classes_name_imp_Library(self, text, interface):
        pattern = fr'class\s+(\w+)\s+extends\s+{interface}\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    def find_class_name_imp_NativeMapped(self, text):
        pattern = r'class\s+(\w+)\s+implements\s+NativeMapped\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    def find_class_name_exd_Structure(self, text):
        pattern = r'class\s+(\w+)\s+extends\s+Structure\b'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

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

    def find_java(self):
        # print(f"{self.project_path} run find_java.")
        for path_root, dirs, files in os.walk(self.project_path):

            # logging.debug(f'= 1 = {path_root}')
            # print(f'= 1 = {path_root}')
            for file in files:
                # print(file)
                if file.endswith('.java'):
                    file_path = os.path.join(path_root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()
                        self.pattern_res1.clear()
                        self.pattern_res2.clear()
                        is_import_jna = False
                        # 只在当前文件下需要，每个文件单独一个，首次使用清空数据
                        self.pattern_jna_packages.clear()
                        is_import_jna_pkg = False

                        for i, line in enumerate(lines):
                            line = line.strip()
                            # 如果line是注释行则跳过
                            if myutils.java_line_starts_with_annotation(line):
                                continue

                            # # test
                            # if re.search(r'\bjna\b',line):
                            #     self.jna_path_test.append(self.project_path)
                            #     continue
                            # else:
                            #     continue

                            if self.re_match(self.pattern_jna, line):
                                is_import_jna = True
                                self.res_jna_file.append((file_path, i + 1, line))

                            #  com.sun.jna.xxx
                            pkg_name = self.extract_jna_pkg_name(line)
                            if pkg_name is not None:
                                is_import_jna_pkg = True
                                self.pattern_jna_packages.append(pkg_name)

                            if len(self.pattern_jna_packages) != 0:
                                for pkg in self.pattern_jna_packages:
                                    pat_pkg = fr'\b{pkg}\b'
                                    if self.re_match(pat_pkg,line):
                                        self.res_java.append((file_path, i + 1, line))



                            # Native.load
                            if self.re_match(self.p_native_load, line,self.pattern_res1) and is_import_jna:
                                self.res_java.append((file_path, i + 1, line))

                            if len(self.pattern_res1) != 0:
                                for pat in self.pattern_res1:
                                    if self.re_match(pat, line):
                                        # print(line)
                                        self.res_java.append((file_path, i + 1, line))

                            IName_exd_Library = self.find_interface_name_exd_Library(line)
                            if IName_exd_Library is not None and is_import_jna:
                                self.res_java.append((file_path, i + 1, line))
                                self.p_ext_Library_interfaces.append(IName_exd_Library)
                                # test
                                self.test_1_1_lines.append((IName_exd_Library,line))

                            CName_imp_NativeMapped = self.find_class_name_imp_NativeMapped(line)
                            if CName_imp_NativeMapped is not None and is_import_jna:
                                self.res_java.append((file_path, i + 1, line))
                                self.p_imp_NativeMapped_classes.append(CName_imp_NativeMapped)
                                # test
                                self.test_1_2_lines.append((CName_imp_NativeMapped, line))

                            CName_exd_Structure = self.find_class_name_exd_Structure(line)
                            if CName_exd_Structure is not None and is_import_jna:
                                self.res_java.append((file_path, i + 1, line))
                                self.p_exd_Structure_classes.append(CName_exd_Structure)
                                # test
                                self.test_1_3_lines.append((CName_exd_Structure, line))

    def find_java_second(self):
        if len(self.p_ext_Library_interfaces) != 0:

            for path_root, dirs, files in os.walk(self.project_path):
                # print(f'= 2 = {path_root}')
                for file in files:

                    if file.endswith('.java'):
                        file_path = os.path.join(path_root, file)
                        with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                line = line.strip()
                                # 如果line是注释行则跳过
                                if myutils.java_line_starts_with_annotation(line):
                                    continue
                                if len(self.p_ext_Library_interfaces) != 0:
                                    for Interface in self.p_ext_Library_interfaces:
                                        class_name = self.find_classes_name_imp_Library(line, Interface)
                                        if class_name is not None:
                                            self.test_2_lines.append((class_name,line))
                                            self.p_imp_Library_classes.append(class_name)

    def find_java_third(self):
        # 列表去重
        self.p_ext_Library_interfaces = list(set(self.p_ext_Library_interfaces))
        self.p_imp_NativeMapped_classes = list(set(self.p_imp_NativeMapped_classes))
        self.p_exd_Structure_classes = list(set(self.p_exd_Structure_classes))

        if len(self.p_ext_Library_interfaces) != 0 or len(self.p_imp_NativeMapped_classes) !=0 or len(self.p_exd_Structure_classes) != 0:
            # print(f"{self.project_path} 执行 find_java_third！")
            for path_root, dirs, files in os.walk(self.project_path):
                # print(f'= 3 = {path_root}')
                for file in files:
                    # print(file)
                    if file.endswith('.java'):
                        file_path = os.path.join(path_root, file)
                        with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                            lines = f.readlines()
                            self.pattern_res1.clear()
                            self.pattern_res2.clear()
                            for i, line in enumerate(lines):
                                line = line.strip()
                                # 如果line是注释行则跳过
                                if myutils.java_line_starts_with_annotation(line):
                                    continue

                                # eLi 为ext_Library_interfaces 首字符缩写
                                if len(self.p_ext_Library_interfaces) != 0:
                                    for eLi in self.p_ext_Library_interfaces:
                                        eLi_pat = fr'\b{eLi}\b'
                                        if self.re_match(eLi_pat,line,self.pattern_res1):
                                            self.res_java.append((file_path, i + 1, line))

                                if len(self.p_imp_NativeMapped_classes) != 0:
                                    for iNc in self.p_imp_NativeMapped_classes:
                                        iNc_pat = fr'\b{iNc}\b'
                                        if self.re_match(iNc_pat, line, self.pattern_res1):
                                            self.res_java.append((file_path, i + 1, line))

                                if len(self.p_exd_Structure_classes) != 0:
                                    for eSc in self.p_exd_Structure_classes:
                                        eSc_pat = fr'\b{eSc}\b'
                                        if self.re_match(eSc_pat, line, self.pattern_res1):
                                            self.res_java.append((file_path, i + 1, line))

                                # 列表去重
                                self.pattern_res1 = list(set(self.pattern_res1))
                                if len(self.pattern_res1) != 0:
                                    for pat in self.pattern_res1:
                                        if self.re_match(pat, line):
                                            self.res_java.append((file_path, i + 1, line))

    def find_java_main(self):
        time1 = time.time()
        self.find_java()
        time2 = time.time()
        # print(f'self.find_java() 用时{time2 - time1}秒！')
        self.find_java_second()
        # time3 = time.time()
        # print(f'self.find_java_second() 用时{time3 - time2}秒！')
        self.find_java_third()
        self.res_java = myutils.list_deduplicated(self.res_java)
        # time4 = time.time()
        # print(f'self.find_java_third() 用时{time4 - time3}秒！')

    def find_c(self):
        pass


if __name__ == '__main__':
    pass
    # repo_paths = [
    # ]
    #
    #
    # for path in repo_paths:
    #     if os.path.exists(path):
    #         print(f"{path}路径存在")
    #     else:
    #         print(f"{path}路径不存在")
    #
    #     jnafinder = JNAFinder(path)
    #     jnafinder.find_java_main()
    #
    #     with open('./JNA_results/res.txt', 'a',errors='ignore') as file:
    #         time = datetime.datetime.now()
    #         file.write(str(time) + " - " + jnafinder.project_path+'\n')
    #         for item in jnafinder.res_java:
    #             string_list = [str(i) for i in item]
    #             res = ' '.join(string_list)
    #             file.write(str(time) + " - " + res+'\n')
    #
    #     with open('./JNA_results/jnafile.txt', 'a',errors='ignore') as file:
    #         time = datetime.datetime.now()
    #         file.write(str(time) + " - " + jnafinder.project_path+'\n')
    #         for item in jnafinder.res_jna_file:
    #             string_list = [str(i) for i in item]
    #             res = ' '.join(string_list)
    #             file.write(str(time) + " - " + res+'\n')
    #
    #     logging.info('=' * 30 + 'p_ext_Library_interfaces' + '=' * 30)
    #     for item in jnafinder.test_1_1_lines:
    #         logging.info(item)
    #
    #     logging.info('=' * 30 + 'p_imp_NativeMapped_classes' + '=' * 30)
    #     for item in jnafinder.test_1_2_lines:
    #         logging.info(item)
    #
    #     logging.info('=' * 30 + 'p_exd_Structure_classes' + '=' * 30)
    #     for item in jnafinder.test_1_3_lines:
    #         logging.info(item)
    #
    #     logging.info('=' * 30 + 'p_imp_Library_classes' + '=' * 30)
    #     for item in jnafinder.test_2_lines:
    #         logging.info(item)



