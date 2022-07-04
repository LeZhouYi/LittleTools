import os
from common.ApiMap import ApiMap
from common.TestApi import TestApi
from common.GenUtils import write_api_file,gen_testcase_yaml
from common.FileUtils import load_yaml_file
from common.GenUtils import gen_testcases,TestDot,gen_yaml

def gen_tescase_script_file():
    #设置此次测试用例脚本的对应关系
    method_mapping = {
        "add":{
            "key": 'user',
            "testdot": "testpack/新增父帐号.yaml",
            "api": "script/MathConcept-portal/用户/新增用户.yaml"
        },
        "find":{
            "key": "user",
            "testdot": "testpack/查看用户列表.yaml",
            "api": "script/MathConcept-portal/用户/获取用户列表.yaml",
        },
        "modify":{
            "key": "user",
            "testdot": "testpack/编辑父帐号.yaml",
            "api": "script/MathConcept-portal/用户/编辑用户.yaml"
        },
        "detail":{
            "key": "user",
            "testdot": "查看用户详情",#仅文字，用来指定测试步骤的标题
            "api": "script/MathConcept-portal/用户/获取用户详情.yaml"
        },
        "delete":{
            "key": "user",
            "testdot": "查看用户删除",#仅文字，用来指定测试步骤的标题
            "api": "script/MathConcept-portal/用户/删除用户.yaml"
        }
    }
    #初始化脚本数据结构并输出对应的脚本文件
    api_map = ApiMap(method_mapping)
    gen_testcase_yaml(api_map,str.format('{}/testcases',os.getcwd()))

def gen_api_script_file():
    #设置文件夹
    api_file_path = str.format('{}/api',os.getcwd())
    api_script_path = str.format('{}/script',os.getcwd())

    #遍历所有API文档
    for file_name in os.listdir(api_file_path):
        #获取API文档名和输出路径
        api_file_name = str.format('{}/{}',api_file_path,file_name)
        api_script_name = str.format('{}/{}',api_script_path,file_name[:-5])

        #载入API文档并初始化
        test_api = TestApi(load_yaml_file(api_file_name))
        test_api.set_client_env('portal_access_token')

        #获取脚本数据并写入文件
        script_datas = test_api.gen_api_scripts()
        write_api_file(script_datas,api_script_name)

def gen_testcase():

    #设置放置功能点的文件夹，导出禅道测试用例的文件夹，和存放解析过后的功能点模块的文件
    test_dot_path = str.format('{}/testdot',os.getcwd())
    test_case_path = str.format('{}/testcase',os.getcwd())
    test_pack_path = str.format('{}/testpack',os.getcwd())

    #遍历所有功能点文件
    for file_name in os.listdir(test_dot_path):
        #获取功能点文件和输出的文件名
        dot_file_name = str.format('{}/{}',test_dot_path,file_name)
        out_file_name = str.format('{}/{}.csv',test_case_path,file_name[:-3])

        #载入功能点文点并解析,生成禅道测试用例，生成解析的功能点模块文件
        test_dots = TestDot.load_test_dots(dot_file_name)
        gen_testcases(test_dots,out_file_name)
        gen_yaml(test_dots,test_pack_path)

if __name__ == '__main__':
    gen_testcase() #生成禅道用例
    gen_api_script_file() #生成API脚本
    gen_tescase_script_file() #生成API测试用例脚本