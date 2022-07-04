import copy
from typing import List

class TestCase(object):
    '''禅道测试用例的数据结构'''

    def __init__(self) -> None:
        self.line = [None for i in range(10)]

    def set_module(self,module:str)->None:
        '''设置模块名'''
        self.line[0] = module

    def set_requirement(self,requirement:str)->None:
        '''设置研发需求'''
        self.line[9] = requirement

    def set_testcase_key(self,testcase_key:str)->None:
        '''设置关键字'''
        self.line[5] = testcase_key

    def set_priority(self,priority:int)->None:
        '''设置优先级'''
        self.line[6] = str(priority)

    def set_type(self,type:str)->None:
        '''设置用例类型'''
        self.line[7] = type

    def set_stage(self,stage:str)->None:
        '''设置适用阶段'''
        self.line[8] = stage

    def set_pre_step(self,index:int,step:str)->None:
        '''设置前置步骤，重复设置则追加'''
        if self.line[2] == None:
            self.line[2] = str.format("{}. {}\n",index,step)
        else:
            self.line[2] = str.format("{}{}. {}\n",self.line[2],index,step)

    def set_step(self,index:int,step:str)->None:
        '''设置步骤，重复设置则追加'''
        if self.line[3] == None:
            self.line[3] = str.format("{}. {}\n",index,step)
        else:
            self.line[3] = str.format("{}{}. {}\n",self.line[3],index,step)

    def set_result(self,index:int,result:str)->None:
        '''设置结果，重复设置则追加'''
        if self.line[4] == None:
            self.line[4] = str.format("{}. {}\n",index,result)
        else:
            self.line[4] = str.format("{}{}. {}\n",self.line[4],index,result)

    def set_name(self,name:str,is_rewrite:bool=True)->None:
        '''设置用例标题，默认不追加'''
        if is_rewrite:
            self.line[1] = name
        else:
            before = "" if self.line[1]==None else self.line[1]
            self.line[1] = str.format('{}{}',before,name)

    def is_name_exist(self,find_str:str)->bool:
        '''检查标题是否包含某字段'''
        return str(self.line[1]).find(find_str)>=0

    def get_csv_line(self)->List[str]:
        '''返回适用于csv的列表数据'''
        return copy.deepcopy(self.line)

    def reset_step_result(self)->None:
        '''清空步骤和结果'''
        self.line[3] = None
        self.line[4] = None