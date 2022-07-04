import re
import copy
from typing import List
from TestCase import TestCase

class TestDot(object):
    '''功能测试模块的数据结构'''

    value_pattern = '\[[\S]+\]' #值提取正则式
    sign_type = ['constraint','extend','main','pre_step']#代表约束条件，扩展，主成功，前置条件
    header_list = ["所属模块","用例标题","前置条件","步骤","预期","关键词","优先级","用例类型","适用阶段","相关研发需求"]
    type_value = ['功能测试','性能测试','配置相关','安装部署','安全相关','接口测试','单元测试','其他']
    stage_value = ['单元测试阶段','功能测试阶段','集成测试阶段','系统测试阶段','冒烟测试阶段','版本验证阶段']

    def __init__(self) -> None:
        self.sign = None #标记后续的测试用例类型
        self.constraints = [] #存储约束条件相关用例
        self.mains = [] #存储主成功场景相关用例
        self.extends = [] #存储扩展相关用例
        self.pre_steps = [] #前置条件
        self.module = "" #存储模块名
        self.is_functional = True #是否是功能测试
        self.requirement = "" #存储研发需求
        self.function_module = "" #存储功能模块名

    def has_mains(self)->bool:
        '''是否存在主成功'''
        return len(self.mains)>0

    def has_constraints(self)->bool:
        '''是否存在约束'''
        return len(self.constraints)>0

    def has_extends(self)->bool:
        '''是否存在扩展'''
        return len(self.extends)>0

    def is_pre_step(line:str)->bool:
        '''
        检测是否是前置条件
        '''
        return re.search('^- 前置条件$',line)!=None

    def is_constraint(line:str)->bool:
        '''
        检测是否是约束条件
        '''
        return re.search('^- 约束条件$',line)!=None

    def is_extend(line:str)->bool:
        '''
        检测是否是扩展
        '''
        return re.search('^- 扩展$',line)!=None

    def is_main(line:str)->bool:
        '''
        检测是否是主成功场景
        '''
        return re.search('^- 主成功场景$',line)!=None

    def is_requirement(line:str)->bool:
        '''
        检测是否是功能模块&研发需求
        '''
        return re.search('^### [^#]+\[[^#]+\(#[0-9]+\)\]$',line)!=None

    def is_ui_title(line:str)->bool:
        '''
        检测是否是UI测试
        '''
        return re.search('^## UI测试$',line)!=None

    def is_functional_title(line:str)->bool:
        '''
        检测是否是功能测试
        '''
        return re.search('^## 功能测试$',line)!=None

    def is_module(line:str)->bool:
        '''
        检测是否是模块
        '''
        return re.search('^# [^#]+\[\/[^#]+\(#[0-9]+\)\]$',line)!=None

    def is_testcase(line:str)->bool:
        '''
        检测是否是测试用例
        '''
        return re.search('^- [\S]+:[\S]*$',line)!=None

    def is_constraint_key(line:str)->bool:
        '''
        检测是否是约束条件用例的键
        '''
        return re.search('^- \[[\S]+\]$',line)!=None

    def is_module_text(line:str)->bool:
        '''
        检测是否是模块相关的文本
        '''
        return re.search('^-',line)!=None

    def is_sign_empty(self)->bool:
        '''
        检测标志值是否存在
        '''
        return self.sign!=None

    def set_sign(self,sign:str)->None:
        '''
        设置当前标志
        '''
        self.sign = sign

    def set_module(self,line)->None:
        '''
        设置当前模块
        '''
        result = re.search(self.value_pattern,line);
        self.module = line[result.span()[0]+1:result.span()[1]-1]

    def set_functional_sign(self,is_functional:bool)->None:
        '''
        标记当前是否功能测试
        '''
        self.is_functional = is_functional

    def add_testcase(self,line:str)->None:
        '''
        添加测试用例
        '''
        line = line[1:]
        if self.sign == self.sign_type[0]: #约束条件的用例
            self.constraints[-1]['cases'].append(line)
        elif self.sign == self.sign_type[1]: #扩展
            self.extends.append(line)
        elif self.sign == self.sign_type[2]: #主成功
            self.mains.append(line)
        elif self.sign == self.sign_type[3]: #主成功
            self.pre_steps.append(line)

    def add_requirement(self,line:str)->None:
        '''
        设置当前功能模块和研发需求
        '''
        result = re.search(self.value_pattern,line);
        self.requirement = line[result.span()[0]+1:result.span()[1]-1]
        self.function_module = line[4:result.span()[0]]

    def add_constraint_key(self,line:str)->None:
        '''
        添加约束条件的键
        '''
        result = re.search('\[[\S]+\]',line)
        self.constraints.append({
            "key": line[result.span()[0]+1:result.span()[1]-1],
            "cases": []
        })

    def clear_testcase_data(self)->None:
        '''
        清空用例相关数据
        '''
        self.sign = None
        self.constraints = []
        self.mains = []
        self.extends = []
        self.pre_steps = []

    def load_test_dots(file_path:str)->list:
        '''
        载入测试功能点,并规整为合适的数据格式
        '''
        #读取测试功能点文件
        with open(file_path) as file:
            lines = file.readlines();
        lines = [i.strip() for i in lines]

        test_dots = []
        test_dot = TestDot()

        for line in lines:
            #录入用例,约束条件,前置条件
            if TestDot.is_testcase(line):
                test_dot.add_testcase(line)
            #录入约束条件的键值
            elif TestDot.is_constraint_key(line):
                test_dot.add_constraint_key(line)
            #非上述文本但跳过处理的，如【- 前置条件】
            elif TestDot.is_module_text(line):
                pass
            #非上述文本，标记该模块已录入完毕，如新的模块名
            elif test_dot.is_sign_empty():
                test_dots.append(copy.deepcopy(test_dot))
                test_dot.clear_testcase_data()

            #匹配到模块名
            if TestDot.is_module(line):
                test_dot.set_module(line)
            #匹配到功能测试
            elif TestDot.is_functional_title(line):
                test_dot.set_functional_sign(True)
            #匹配到UI测试
            elif TestDot.is_ui_title(line):
                pass
            #匹配到研发需求
            elif TestDot.is_requirement(line):
                test_dot.add_requirement(line)
            #匹配到主成功场景
            elif TestDot.is_main(line):
                test_dot.set_sign(TestDot.sign_type[2])
            #匹配到扩展
            elif TestDot.is_extend(line):
                test_dot.set_sign(TestDot.sign_type[1])
            #匹配到约束条件
            elif TestDot.is_constraint(line):
                test_dot.set_sign(TestDot.sign_type[0])
            #匹配到前置步骤
            elif TestDot.is_pre_step(line):
                test_dot.set_sign(TestDot.sign_type[3])
        print(test_dots)
        return test_dots

    def get_yaml_dict(self)->dict:
        '''
        返回用于生成Yaml的字典
        '''
        return {
            "sign":self.sign,
            "constraints": self.constraints,
            "mains": self.mains,
            "extends": self.extends,
            "pre_steps": self.pre_steps,
            "module": self.module,
            "is_functional": self.is_functional,
            "requirement": self.requirement,
            "function_module": self.function_module
        }

    def load_by_yaml_dict(self,yaml_dict:dict)->None:
        '''
        解析从yaml中读取出来的数据并存入对应变量
        '''
        self.sign = yaml_dict['sign']
        self.constraints = yaml_dict['constraints']
        self.mains = yaml_dict['mains']
        self.extends = yaml_dict['extends']
        self.pre_steps = yaml_dict['pre_steps']
        self.module = yaml_dict['module']
        self.is_functional = yaml_dict['is_functional']
        self.requirement = yaml_dict['requirement']
        self.function_module = yaml_dict['function_module']

    def get_constraints(self)->List[dict]:
        '''
        获取约束条件
        '''
        return self.constraints

    def get_extends(self)->List[str]:
        '''获取扩展'''
        return self.extends

    def get_mains(self)->List[str]:
        '''获取主成功场景'''
        return self.mains

    def get_mains_name(self)->str:
        '''获取主成功场景的用例名'''
        return self.get_mains()[0].split(":")[0].strip()

    def get_function_module(self)->str:
        '''
        获取功能模块名
        '''
        return self.function_module

    def get_csv_headers()->List[str]:
        '''
        返回CSV标头
        '''
        return TestDot.header_list

    def to_csv_lines(self)->List[List[str]]:
        '''
        转换成CSV所需格式
        '''
        csv_lines = []
        testcase = TestCase()

        testcase.set_module(self.module) #所属模块
        testcase.set_requirement(self.requirement) #相关研发需求
        testcase.set_testcase_key(self.function_module) #关键字
        testcase.set_priority(3) #优先级
        testcase.set_type(self.type_value[0]) #用例类型
        testcase.set_stage(self.stage_value[1]) #适用阶段

        #录入前置步骤文本
        for index in range(len(self.pre_steps)):
            step = str(self.pre_steps[index])[:-1]
            testcase.set_pre_step(index+1,step)#用例前置条件

        #录入主成功场景文本，若存在扩展文本，则后续录入扩展文本
        if len(self.mains)>0:
            testcase.set_name(str.format('{}的主成功场景',self.function_module)) #用例标题
            #录入主成功场景文本
            for i in range(len(self.mains)):
                step_results = str(self.mains[i]).split(':')
                testcase.set_step(i+1,step_results[0]) #步骤
                testcase.set_result(i+1,step_results[1]) #预期

            #若存在扩展文本，则录入扩展文本
            if len(self.extends)>0:
                testcase.set_name('和扩展',is_rewrite=False)
                for i in range(len(self.extends)):
                    step_results = str(self.extends[i]).split(':')
                    testcase.set_step(i+2,step_results[0]) #步骤
                    testcase.set_result(i+2,step_results[1]) #预期

        #录入约束条件，若不存在扩展文本，则与主成功场景合并。若存在扩展文本，则新起一条用例
        if len(self.constraints)>0:
            #存在扩展文本
            if testcase.is_name_exist("和"):
                csv_lines.append(testcase.get_csv_line())
                testcase.set_name(str.format('{}的约束条件',self.function_module)) #标题
                testcase.reset_step_result()
                index = 0
            #不存在扩展文本
            else:
                index = 1
                testcase.set_name("和约束条件",is_rewrite=False) #标题
            #录入约束条件文本
            for item in self.constraints:
                for case in item['cases']:
                    index+=1
                    step_results = str(case).split(':')
                    testcase.set_step(index,step_results[0]) #步骤
                    testcase.set_result(index,step_results[1]) #预期
            csv_lines.append(testcase.get_csv_line())
        print(csv_lines)
        return csv_lines