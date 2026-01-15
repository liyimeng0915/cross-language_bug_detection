
import re
import os

import myutils


class JNIFinder:
    def __init__(self,project_path):
        self.project_path = project_path

        self.res_c=[]
        self.res_java = []

        # 间接一层
        self.pattern_res1 = []
        # 间接两层
        self.pattern_res2 = []

        self.re_native = r'\bnative\b'


        self.native_methods = []

        self.native_methods_dict = {}
        # jint  JNIEnv jclass JavaVM JNINativeMethod #include <jni.h>
        # JNIEXPORT 方法

        self.c_filedname = ['jint', 'JNIEnv', 'jclass', 'JavaVM', 'JNINativeMethod', '<jni.h>',
                            'jfieldID','JNICALL','jobject','jfieldID','jstring','jarray','jthrowable',
                            'jboolean', 'jbyte', 'jchar', 'jshort', 'jlong','jfloat','jdouble' ,'jbyteArray',
                            'JNIEXPORT','JNICALL','jvalue','jmethodID','jobjectArray']

    def extract_native_method_name(self, s):
        # 定义正则表达式模式
        # pattern = r'native\s+\w+\s+(\w+)'
        pattern = r'native\s+[\w\s]+\s+(\w+)\('
        # 使用正则表达式进行搜索
        match = re.search(pattern, s)

        # 如果匹配成功，返回method_name的值
        if match:
            return match.group(1)
        else:
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
        for path_root,dirs,files in os.walk(self.project_path):
            root = path_root.replace('\\', '/')
            self.native_methods_dict[root] = []

            # 第一次遍历提取所有的native方法名
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            line = line.strip()
                            # 如果line是注释行则跳过
                            if myutils.java_line_starts_with_annotation(line):
                                continue


                            if self.re_match(self.re_native, line):
                                # 获取方法名
                                method_name = self.extract_native_method_name(line)

                                if method_name is not None:
                                    # print(f'root{root}, method_name:{method_name}')
                                    self.native_methods_dict[root].append(myutils.string2re(method_name))
                                self.res_java.append((file_path, i + 1, line))

    def find_java_again(self):
        native_dict = {key: value for key, value in self.native_methods_dict.items() if value}
        path_keys = list(native_dict.keys())

        for path in path_keys:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                line = line.strip()
                                # 如果line是注释行则跳过
                                if myutils.java_line_starts_with_annotation(line):
                                    continue
                                for pat in native_dict[path]:
                                    if self.re_match(pat, line, self.pattern_res1):
                                        self.res_java.append((file_path, i + 1, line))
                                for pat in self.pattern_res1:
                                    if self.re_match(pat, line, self.pattern_res2):
                                        # print(line)
                                        self.res_java.append((file_path, i + 1, line))
                                for pat in self.pattern_res2:
                                    if self.re_match(pat, line):
                                        # print(line)
                                        self.res_java.append((file_path, i + 1, line))

    def find_c(self):
        for path_root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp') or file.endswith('.h'):
                    file_path = os.path.join(path_root, file)
                    with (open(file_path, 'r', encoding='ISO-8859-1',errors='ignore') as f):
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            line = line.strip()
                            # 如果line是注释行则跳过
                            if myutils.java_line_starts_with_annotation(line):
                                continue
                            for keyword in self.c_filedname:
                                re_pat = fr'\b{keyword}\b'
                                if self.re_match(re_pat, line):
                                    self.res_c.append((file_path, i + 1, line))

if __name__ == '__main__':

    jnifinder = JNIFinder('E:\\jni-example-code')
    jnifinder.find_c()
    resc = myutils.list_deduplicated(jnifinder.res_c)
    for item in resc:
        print(item)

    # jnifinder.find_java()
    # jnifinder.find_java_again()
    # for item in jnifinder.res_java:
    #     print(item)
