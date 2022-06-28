import os
from common.TestCaseGenerator import load_test_dot,gen_testcases

if __name__ == '__main__':
    test_dot_path = str.format('{}/testdot',os.getcwd())
    test_case_path = str.format('{}/testcase',os.getcwd())
    for file_name in os.listdir(test_dot_path):
        dot_file_name = str.format('{}/{}',test_dot_path,file_name)
        out_file_name = str.format('{}/{}.csv',test_case_path,file_name[:-3])
        test_dot_parts = load_test_dot(dot_file_name)
        gen_testcases(test_dot_parts,out_file_name)