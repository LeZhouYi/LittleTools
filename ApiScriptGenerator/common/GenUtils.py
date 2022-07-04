import os
import re
import csv
import yaml
import copy
from TestScript import TestConfig,TestStep
from ApiMap import ApiMap
from FileUtils import load_yaml_file
from typing import List
from TestDot import TestDot
from ApiScript import ApiScript
from common.ApiMap import ApiMap

def gen_testcases(test_dots:List[TestDot],file_path:str)->None:
    '''生成CSV文件格式的测试用例'''
    with open(file_path,mode='w',encoding='utf-8',newline="") as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(TestDot.header_list)
        for test_dot in test_dots:
            writer.writerows(test_dot.to_csv_lines())

def gen_yaml(test_dots:List[TestDot],file_path:str)->None:
    '''
    生成yaml文件
    '''
    for test_dot in test_dots:
        file_name = str.format('{}/{}.yaml',file_path,test_dot.get_function_module())
        with open(file_name,'w+') as file:
            file.write(yaml.dump(test_dot.get_yaml_dict(),allow_unicode=True,indent=4,sort_keys=False))

def write_api_file(api_script_bodys:List[ApiScript],out_path:str):
    '''
    生成YAML格式的API脚本
    '''
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for api_item in api_script_bodys:
        file_name = api_item.get_file_name() #文件名
        file_path = str.format('{}/{}/{}.yaml',out_path,api_item.get_tag(),file_name)
        if not os.path.exists(str.format('{}/{}',out_path,api_item.get_tag())):
            os.makedirs(str.format('{}/{}',out_path,api_item.get_tag()))
        with open(file_path,'w+') as file:
            file.write(yaml.dump({'name':api_item.get_name()},allow_unicode=True,indent=4,sort_keys=False))
            file.write(yaml.dump({'base_url':api_item.get_base_url()},allow_unicode=True,indent=4,sort_keys=False))
            file.write(yaml.dump({'variables':api_item.get_variables()},allow_unicode=True,indent=4,sort_keys=False))
            file.write(yaml.dump({'request':api_item.get_request()},allow_unicode=True,indent=4,sort_keys=False))

def rebuild_yaml_file(file_path:str):
    '''
    调整yaml的字符和缩进结构
    '''
    #重处理文本
    with open(file_path,'r') as file:
        lines = file.readlines()
    with open(file_path,'w+') as file:
        for line in lines:
            line = line.replace("'","")
            if re.match('^      ',line):
                line = "  "+line
            elif re.match('^    -',line):
                line = "    "+line
            elif re.match('^- test:$',line):
                file.write("\n")
            file.write(line)

#----------------------------------------------------------------------------------------------------

def gen_success_add_testcase(api_map:ApiMap):
    '''
    生成新增类型的成功用例
    '''
    testcase = [] #用例
    method_sign = ApiMap.ADD #标记当前的方法类型

    api = load_yaml_file(api_map.get_api(method_sign))#API
    testdot = TestDot() #载入相关功能点模块
    testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(method_sign)))

    if testdot.has_mains():
        #用例头
        config = TestConfig(is_full=True)
        config.set_name(str.format('{}成功',testdot.get_function_module()))

        #添加Gen变量和output变量
        config.add_output(str.format('{}_id_output',api_map.get_key(method_sign)))
        for key,value in api['variables'].items():
            if key!='access_token':
                config.add_variable(str.format('{}_{}_gen',api_map.get_key(method_sign),key),value)
                config.add_output(str.format('{}_{}_output',api_map.get_key(method_sign),key))
            else:
                config.add_output(str.format('{}_output',value))

        #添加variables中output变量对gen变量的引用
        for key,value in api['variables'].items():
            if key!='access_token':
                config.add_variable(str.format('{}_{}_output',api_map.get_key(method_sign),key),str.format('${}_{}_gen',api_map.get_key(method_sign),key))
        testcase.append(config.get_dict())

        #测试步骤
        tempcase = TestStep(is_full=True)
        tempcase.set_name(testdot.get_mains_name()) #测试步骤名
        tempcase.set_api(api_map.get_api(method_sign))#测试步骤引用名
        #添加测试步骤中的变量
        for key,value in api['variables'].items():
            if key!='access_token':
                tempcase.add_variables(key,str.format('${}_{}_gen',api_map.get_key(method_sign),key))
            else:
                tempcase.add_variables(key,str.format('${}_output',value))
        tempcase.add_validate('eq: [status_code, 200]')#测试步骤的校验
        tempcase.add_extract(str.format('{}_id_output: content.id',api_map.get_key(method_sign)))#测试步骤的导出

        testcase.append(tempcase.get_dict())
    return testcase

def gen_extra_add_testcase(api_map:ApiMap):
    '''生成新增类型的扩展和约束条件用例'''
    testcases = []
    method_sign = ApiMap.ADD #标记当前的方法类型

    api = load_yaml_file(api_map.get_api(method_sign))#API
    testdot = TestDot() #载入相关功能点模块
    testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(method_sign)))

    #测试步骤
    tempcase = TestStep(is_testcase=False,is_full=False)
    tempcase.set_api(api_map.get_api(method_sign))#测试步骤接口名
    #添加测试步骤中的变量
    for key,value in api['variables'].items():
        if key!='access_token':
            tempcase.add_variables(key,value)
        else:
            tempcase.add_variables(key,str.format('${}_output',value))

    if testdot.has_extends():
        extend_case = [] #用例
        #用例头
        config = TestConfig(is_full=False)
        config.set_name(str.format('{}的扩展',testdot.get_function_module()))

        extend_case.append(config.get_dict())
        for extend in testdot.get_extends():
            extend_step = copy.deepcopy(tempcase)#备份测试步骤
            extend_step.set_name(extend.split(":")[0].strip())
            extend_step.add_validate('eq: [status_code, 200]')
            extend_case.append(extend_step.get_dict())
        testcases.append(extend_case)
    if testdot.has_constraints():
        constraint_case = [] #用例
        #用例头
        config = TestConfig(is_full=False)
        config.set_name(str.format('{}的约束条件',testdot.get_function_module()))
        constraint_case.append(config.get_dict())

        for constraint in testdot.get_constraints():
            for case in constraint['cases']:
                constraint_step = copy.deepcopy(tempcase)#备份测试步骤
                constraint_step.set_name(case.split(":")[0].strip())
                constraint_step.add_validate('eq: [status_code, 400]')
                constraint_case.append(constraint_step.get_dict())
        testcases.append(constraint_case)
    return testcases

def gen_find_testcase(api_map:ApiMap):
    '''
    生成查看列表相关的用例
    '''
    testcase = []#用例
    method_sign = ApiMap.FIND #标记当前的方法类型

    api = load_yaml_file(api_map.get_api(method_sign))#API
    testdot = TestDot() #载入相关功能点模块
    testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(method_sign)))

    #用例头
    config = TestConfig()
    config.set_name(str.format('{}成功',testdot.get_function_module()))
    testcase.append(config.get_dict())

    #新增
    if api_map.is_exist_method(ApiMap.ADD):
        add_sign = ApiMap.ADD
        add_api = load_yaml_file(api_map.get_api(add_sign))#API
        add_testdot = TestDot() #载入相关功能点模块
        add_testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(add_sign)))

        add_step = TestStep(is_testcase=True,is_full=False)
        add_step.set_name(str.format('{}成功',add_testdot.get_function_module()))
        add_step.set_testcase(str.format('testcases/{}成功.yaml',add_testdot.get_function_module()))
        add_step.add_extract(str.format('{}_id_output',api_map.get_key(add_sign)))
        for key,value in add_api['variables'].items():
            if key == 'access_token':
                add_step.add_extract(str.format('{}_output',value))
            else:
                add_step.add_extract(str.format('{}_{}_output',api_map.get_key(add_sign),key))
        testcase.append(add_step.get_dict())

    #测试步骤
    teststep = TestStep(is_testcase=False,is_full=False)
    teststep.set_api(api_map.get_api(method_sign))
    teststep.add_validate('eq: [status_code, 200]')

    #主成功场景
    if testdot.has_mains():
        tempstep = copy.deepcopy(teststep)
        tempstep.set_name(testdot.get_mains_name())
        for key,value in api['variables'].items():
            if key == 'access_token':
                tempstep.add_variables(key,str.format('${}_output',value))
            elif key=='_page' or key=='_limit':
                pass
            else:
                tempstep.add_variables(key,str.format('${}_{}_output',api_map.get_key(method_sign),key))
        testcase.append(tempstep.get_dict())

    #扩展
    if len(testdot.get_extends())>0:
        testcase[0]['config']['name']=str.format('{}和扩展',config.get_name())
        tempstep = copy.deepcopy(teststep)
        for key,value in api['variables'].items():
            if key == 'access_token':
                tempstep.add_variables(key,str.format('${}_output',value))
            elif key=='_page' or key=='_limit':
                pass
            else:
                tempstep.add_variables(key,str.format('${}_{}_output',api_map.get_key(method_sign),key))
        for case in testdot.get_extends():
            tempstep.set_name(str(case).split(":")[0].strip())
            testcase.append(tempstep.get_dict())
    return testcase

def gen_success_modify_testcase(api_map:ApiMap):
    '''
    生成修改查看删除的测试用例
    '''
    testcase = []#用例
    method_sign = ApiMap.EDIT
    api = load_yaml_file(api_map.get_api(method_sign))#API
    testdot = TestDot() #载入相关功能点模块
    testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(method_sign)))

    #用例头
    config = TestConfig(is_full=False,need_variables=True)
    config.set_name(str.format('{}成功',testdot.get_function_module()))
    for key,value in api['variables'].items(): #遍历编辑API存在的变量
        if key == 'access_token' or key == 'id':
            pass
        else:
            config.add_variable(str.format('{}_{}_edit',api_map.get_key(method_sign),key),value)
    testcase.append(config.get_dict())

    #新增
    if api_map.is_exist_method(ApiMap.ADD):
        add_sign = ApiMap.ADD
        add_api = load_yaml_file(api_map.get_api(add_sign))#API
        add_testdot = TestDot() #载入相关功能点模块
        add_testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(add_sign)))

        add_step = TestStep(is_testcase=True,is_full=False)
        add_step.set_name(str.format('{}成功',add_testdot.get_function_module()))
        add_step.set_testcase(str.format('testcases/{}成功.yaml',add_testdot.get_function_module()))
        add_step.add_extract(str.format('{}_id_output',api_map.get_key(add_sign)))
        for key,value in add_api['variables'].items():
            if key == 'access_token':
                add_step.add_extract(str.format('{}_output',value))
            else:
                add_step.add_extract(str.format('{}_{}_output',api_map.get_key(add_sign),key))
        testcase.append(add_step.get_dict())

    #查看详情，对新增的校验
    if api_map.is_exist_method(ApiMap.DETAIL):
        detail_sign = ApiMap.DETAIL

        detail_step = TestStep(is_testcase=False,is_full=False)
        detail_step.set_name(api_map.get_testdot(detail_sign))#测试步骤名
        detail_step.set_api(api_map.get_api(detail_sign))#API
        detail_step.add_validate('eq: [status_code, 200]')
        for key,value in api['variables'].items(): #遍历编辑API存在的变量
            if key == 'access_token':
                detail_step.add_variables(key,str.format('${}_output',value))
            elif key == 'id':
                detail_step.add_variables(key,str.format('${}_id_output',api_map.get_key(detail_sign)))
            else:
                detail_step.add_validate(str.format('eq: [content.{}, ${}_{}_output]',key,api_map.get_key(detail_sign),key))
        testcase.append(detail_step.get_dict())

    #编辑的主成功场景
    if testdot.has_mains():
        main_step = TestStep(is_testcase=False,is_full=False)
        main_step.set_name(testdot.get_mains_name())
        main_step.set_api(api_map.get_api(method_sign))
        main_step.add_validate('eq: [status_code, 200]')
        for key,value in api['variables'].items(): #遍历编辑API存在的变量
            if key == 'access_token':
                main_step.add_variables(key,str.format('${}',value))
            elif key == 'id':
                main_step.add_variables(key,str.format('${}_id_output',api_map.get_key(method_sign)))
            else:
                main_step.add_variables(key,str.format('${}_{}_edit',api_map.get_key(method_sign),key))
        testcase.append(main_step.get_dict())

    #查看详情，对编辑的校验
    if api_map.is_exist_method(ApiMap.DETAIL):
        detail_sign = ApiMap.DETAIL
        detail_step = TestStep(is_testcase=False,is_full=False)
        detail_step.set_name(api_map.get_testdot(detail_sign))#测试步骤名
        detail_step.set_api(api_map.get_api(detail_sign))#API
        detail_step.add_validate('eq: [status_code, 200]')
        for key,value in api['variables'].items(): #遍历编辑API存在的变量
            if key == 'access_token':
                detail_step.add_variables(key,str.format('${}_output',value))
            elif key == 'id':
                detail_step.add_variables(key,str.format('${}_id_output',api_map.get_key(detail_sign)))
            else:
                detail_step.add_validate(str.format('eq: [content.{}, ${}_{}_edit]',key,api_map.get_key(detail_sign),key))
        testcase.append(detail_step.get_dict())

    #删除
    if api_map.is_exist_method(ApiMap.DELETE):
        delete_sign = ApiMap.DELETE
        delete_step = TestStep(is_testcase=False,is_full=False)
        delete_step.set_name(api_map.get_testdot(delete_sign)) #用例名
        delete_step.set_api(api_map.get_api(delete_sign)) #API
        delete_step.add_validate('eq:[status_code, 200]')

        delete_api = load_yaml_file(api_map.get_api(delete_sign))#API
        for key,value in delete_api['variables'].items(): #遍历API存在的变量
            if key == 'access_token':
                delete_step.add_variables(key,str.format('${}_output',value))
            elif key == 'id':
                delete_step.add_variables(key,str.format('${}_id_output',api_map.get_key(delete_sign)))
            else:
                delete_step.add_variables(key,str.format('${}_{}_output',api_map.get_key(delete_sign),key))
        testcase.append(delete_step.get_dict())

    return testcase

def gen_extra_modify_testcase(api_map:ApiMap):
    '''编辑API的扩展和约束条件'''
    testcases = [] #用例集

    method_sign = ApiMap.EDIT
    api = load_yaml_file(api_map.get_api(method_sign))#API
    testdot = TestDot() #载入相关功能点模块
    testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(method_sign)))

    #测试步骤
    tempcase = TestStep(is_testcase=False,is_full=False)
    tempcase.set_api(api_map.get_api(method_sign))#测试步骤接口名
    #添加测试步骤中的变量
    for key,value in api['variables'].items():
        if key == 'access_token':
            tempcase.add_variables(key,str.format('${}_output',value))
        elif key == 'id':
            tempcase.add_variables(key,str.format('${}_id_output',value))
        else:
            tempcase.add_variables(key,value)

    #新增
    add_step = None
    if api_map.is_exist_method(ApiMap.ADD):
        add_sign = ApiMap.ADD
        add_api = load_yaml_file(api_map.get_api(add_sign))#API
        add_testdot = TestDot() #载入相关功能点模块
        add_testdot.load_by_yaml_dict(load_yaml_file(api_map.get_testdot(add_sign)))

        add_step = TestStep(is_testcase=True,is_full=False)
        add_step.set_name(str.format('{}成功',add_testdot.get_function_module()))
        add_step.set_testcase(str.format('testcases/{}成功.yaml',add_testdot.get_function_module()))
        add_step.add_extract(str.format('{}_id_output',api_map.get_key(add_sign)))
        for key,value in add_api['variables'].items():
            if key == 'access_token':
                add_step.add_extract(str.format('{}_output',value))
            else:
                add_step.add_extract(str.format('{}_{}_output',api_map.get_key(add_sign),key))

    #删除
    delete_step = None
    if api_map.is_exist_method(ApiMap.DELETE):
        delete_sign = ApiMap.DELETE
        delete_step = TestStep(is_testcase=False,is_full=False)
        delete_step.set_name(api_map.get_testdot(delete_sign)) #用例名
        delete_step.set_api(api_map.get_api(delete_sign)) #API
        delete_step.add_validate('eq:[status_code, 200]')

        delete_api = load_yaml_file(api_map.get_api(delete_sign))#API
        for key,value in delete_api['variables'].items(): #遍历API存在的变量
            if key == 'access_token':
                delete_step.add_variables(key,str.format('${}_output',value))
            elif key == 'id':
                delete_step.add_variables(key,str.format('${}_id_output',api_map.get_key(delete_sign)))
            else:
                delete_step.add_variables(key,str.format('${}_{}_output',api_map.get_key(delete_sign),key))

    if testdot.has_extends():
        extend_case = [] #用例
        #用例头
        config = TestConfig(is_full=False)
        config.set_name(str.format('{}的扩展',testdot.get_function_module()))
        extend_case.append(config.get_dict())

        if add_step!=None:
            extend_case.append(add_step.get_dict())

        for extend in testdot.get_extends():
            extend_step = copy.deepcopy(tempcase)#备份测试步骤
            extend_step.set_name(extend.split(":")[0].strip())
            extend_step.add_validate('eq: [status_code, 200]')
            extend_case.append(extend_step.get_dict())

        if delete_step!=None:
            extend_case.append(delete_step.get_dict())
        testcases.append(extend_case)

    if testdot.has_constraints():
        constraint_case = [] #用例
        #用例头
        config = TestConfig(is_full=False)
        config.set_name(str.format('{}的约束条件',testdot.get_function_module()))
        constraint_case.append(config.get_dict())

        if add_step!=None:
            constraint_case.append(add_step.get_dict())

        for constraint in testdot.get_constraints():
            for case in constraint['cases']:
                constraint_step = copy.deepcopy(tempcase)#备份测试步骤
                constraint_step.set_name(case.split(":")[0].strip())
                constraint_step.add_validate('eq: [status_code, 400]')
                constraint_case.append(constraint_step.get_dict())
        if delete_step!=None:
            constraint_case.append(delete_step.get_dict())
        testcases.append(constraint_case)
    return testcases


def gen_testcase_yaml(api_map:ApiMap,out_path:str):
    testcases = []#储存用例[成功，扩展，约束条件]
    if api_map.is_exist_method('add'):
        tempcase=gen_success_add_testcase(api_map)#生成新增的主成功
        if tempcase!=None and len(tempcase)>0:
            testcases.append(tempcase)
        tempcases=gen_extra_add_testcase(api_map)#生成新增的扩展和约束
        for tempcase in tempcases:
            testcases.append(tempcase)
    if api_map.is_exist_method('find'):
        tempcase=gen_find_testcase(api_map)#生成查找列表的主成功
        if tempcase!=None and len(tempcase)>0:
            testcases.append(tempcase)
    if api_map.is_exist_method('modify'):
        tempcase=gen_success_modify_testcase(api_map)#生成编辑的主成功
        if tempcase!=None and len(tempcase)>0:
            testcases.append(tempcase)
        tempcases=gen_extra_modify_testcase(api_map)#生成编辑的扩展和约束
        for tempcase in tempcases:
            testcases.append(tempcase)

    #生成文件
    for testcase in testcases:
        with open(str.format('{}/{}.yaml',out_path,testcase[0]['config']['name']),'w+') as file:
            file.write(yaml.dump(testcase,allow_unicode=True,indent=2,sort_keys=False))
        rebuild_yaml_file(str.format('{}/{}.yaml',out_path,testcase[0]['config']['name']))