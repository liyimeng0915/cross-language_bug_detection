import myutils
import FunctionGetter

import java_c.JNAFinder
import java_c.JNIFinder

import java_python.JythonFinder

import python_c.PythonCFinder
import python_c.SWIGFinder
import python_c.Pybind11Finder
import python_c.BoostPyFinder
import python_c.CtypesFinder
import python_c.CffiFinder


def process_java_c_jna(repo_path):
    print("- 2 -process_java_c_jna")
    finder = java_c.JNAFinder.JNAFinder(repo_path)
    finder.find_java_main()
    res = finder.res_java
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_java_c_jni(repo_path):
    print("- 1 -process_java_c_jni")
    finder = java_c.JNIFinder.JNIFinder(repo_path)
    finder.find_java()
    res = finder.res_java
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_python_c_boostpy(repo_path):
    print("- 5 -process_python_c_boostpy")
    finder = python_c.BoostPyFinder.BoostPyFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_python_c_cffi(repo_path):
    print("- 3 -process_python_c_cffi")
    finder = python_c.CffiFinder.CffiFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_python_c_ctypes(repo_path):
    print("- 4 -process_python_c_ctypes")
    finder = python_c.CtypesFinder.CtypesFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_python_c_pybind11(repo_path):
    print("- 6 -process_python_c_pybind11")
    finder = python_c.Pybind11Finder.Pybind11Finder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break

def process_python_c_pythonc(repo_path):
    print("- 7 -process_python_c_pythonc")
    finder = python_c.PythonCFinder.PythonCFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_python_c_swig(repo_path):
    print("- 8 -process_python_c_swig")
    finder = python_c.SWIGFinder.SWIGFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break


def process_java_python(repo_path):
    print("- 9 -process_java_python")
    finder = python_c.PythonCFinder.PythonCFinder(repo_path)
    finder.find_main()
    res = finder.res_python
    # print(len(res))
    return res
    # print(len(res))
    # for i in res:
    #     print(i)
    #     break



if __name__ == '__main__':
    pass

    # get_res_java_cpp(local_repo_java_cpp, 'D:\\mypythondata\\multilangs_res\\java_c_cpp')

    # ctags_res = FunctionGetter.get_function_main('D:\\mypythondata\\repo\\repo_java_cpp\\RLBot\RLBot\\src\\main\\java\\rlbot\\cppinterop\\ByteBufferStruct.java')
    # for cr in ctags_res:
    #     print(cr)
