

import copy
from distutils.command.config import config
from typing import Any


class TestConfig(object):
    '''测试用例脚本的Config结构'''

    def __init__(self,is_full:bool=False,need_variables:bool=False) -> None:
        if is_full:
            self.config = {"name":"","variables":{},"output":[]}#完全版
        elif need_variables:
            self.config = {"name":"","variables":{}}
        else:
            self.config = {"name":""}#简单版

    def set_name(self,name:str,is_rewrite:bool=True)->None:
        '''设置名称，默认覆写'''
        if is_rewrite:
            self.config['name']=name
        else:
            self.config['name']=str.format('{}{}',self.config['name'],name)

    def add_output(self,output:str)->None:
        '''添加输出'''
        self.config['output'].append(output)

    def add_variable(self,key:str,value:Any)->None:
        '''添加变量'''
        self.config['variables'][key]=value

    def get_name(self)->str:
        '''获取用例名'''
        return self.config['name']

    def get_dict(self)->dict:
        '''返回数据结构'''
        return {"config":self.config}

class TestStep(object):
    '''测试用例脚本的test结构'''

    def __init__(self,is_testcase:bool=False,is_full:bool=False) -> None:
        if is_testcase:
            self.teststep = {'name':"",'testcase':'','extract':[]} #引用用例的结构
        elif is_full:
            self.teststep = {'name':"",'api':'','variables':{},'validate':[],'extract':[]} #需导出的结构
        else:
            self.teststep = {'name':"",'api':'','variables':{},'validate':[]} #不需要导出的结构

    def set_name(self,name:str)->None:
        '''设置测试步骤名'''
        self.teststep['name'] = name

    def set_api(self,api_path:str)->None:
        '''设置引用的API路径'''
        self.teststep['api'] = api_path

    def set_testcase(self,testcase_path:str)->None:
        '''设置引用用例的路径'''
        self.teststep['testcase']= testcase_path

    def add_variables(self,key:str,value:Any)->None:
        '''添加变量'''
        self.teststep['variables'][key]=value

    def add_validate(self,validate:str)->None:
        '''添加校验'''
        self.teststep['validate'].append(validate)

    def add_extract(self,extract:str)->None:
        '''添加导出'''
        self.teststep['extract'].append(extract)

    def get_dict(self)->dict:
        '''返回数据结构'''
        return {"test":copy.deepcopy(self.teststep)}