import os
from common.TestCaseGenerator import gen_testcases,TestDot

if __name__ == '__main__':
    test_dot_path = str.format('{}/testdot',os.getcwd())
    test_case_path = str.format('{}/testcase',os.getcwd())
    for file_name in os.listdir(test_dot_path):
        dot_file_name = str.format('{}/{}',test_dot_path,file_name)
        out_file_name = str.format('{}/{}.csv',test_case_path,file_name[:-3])
        test_dots = TestDot.load_test_dots(dot_file_name)
        gen_testcases(test_dots,out_file_name)