from operator import mod
import re
import csv

value_pattern = '\[[\S]+\]' #值提取正则式

module_name_pattern = '^# [^#]+\[\/[^#]+\(#[0-9]+\)\]$' #模块名正则式

functional_test_pattern = '^## 功能测试$'
ui_test_pattern = '^## UI测试$'

requiredment_pattern = '^### [^#]+\[[^#]+\(#[0-9]+\)\]$' #研发需求匹配模块

pre_step_pattern = '^- 前置条件$'
main_success_pattern = '^- 主成功场景$'
extend_pattern = '^- 扩展$'
constraint_pattern = '^- 约束条件$'

tesecase_pattern = '^- [\S]+:[\S]*$' #测试用例正则式
constraint_key_pattern = '^- \[[\S]+\]$' #约束条件名

def load_test_dot(file_path:str):
    '''
    载入测试功能点,并规整为合适的数据格式
    '''
    #读取测试功能点文件
    with open(file_path) as file:
        lines = file.readlines();
    lines = [i.strip() for i in lines]

    #识别并处理合适的数据格式
    test_dot_parts = []
    test_dot_sign = {}

    for line in lines:

        #录入用例,约束条件,前置条件
        if re.search(tesecase_pattern,line):
            if test_dot_sign['test_case_sign']=='constraint_list':
                test_dot_sign['constraint_list'][-1]['cases'].append(line[1:])
            elif test_dot_sign['test_case_sign']!=None:
                test_dot_sign[test_dot_sign['test_case_sign']].append(line[1:])
            print(line)
        #录入约束条件的键值
        elif re.search(constraint_key_pattern,line):
            result = re.search(value_pattern,line)
            constraint_part ={}
            constraint_part['key']=line[result.span()[0]+1:result.span()[1]-1]
            constraint_part['cases']=[]
            test_dot_sign['constraint_list'].append(constraint_part)
            print(line)
        #非上述文本但跳过处理的，如【- 前置条件】
        elif re.search('^-',line):
            pass
        #非上述文本，标记该模块已录入完毕，如新的模块名
        elif 'test_case_sign'in test_dot_sign and test_dot_sign['test_case_sign']!=None:
            test_dot_parts.append(test_dot_sign.copy())
            test_dot_sign['main_success_list']=[]
            test_dot_sign['extend_list']=[]
            test_dot_sign['constraint_list']=[]
            test_dot_sign['pre_step_list'] = []
            test_dot_sign['test_case_sign']=None

        #匹配到模块名
        if re.search(module_name_pattern,line):
            result = re.search(value_pattern,line);
            test_dot_sign['module_value'] = line[result.span()[0]+1:result.span()[1]-1]
            print(test_dot_sign['module_value'])
        #匹配到功能测试
        elif re.search(functional_test_pattern,line):
            test_dot_sign['is_functional_test']=True
            print(line)
        #匹配到UI测试
        elif re.search(ui_test_pattern,line):
            pass
            # test_dot_sign['is_functional_test']=False
            # print(line)
        #匹配到研发需求
        elif re.search(requiredment_pattern,line):
            result = re.search(value_pattern,line);
            test_dot_sign['requirement_value'] = line[result.span()[0]+1:result.span()[1]-1]
            test_dot_sign['function_base_name'] = line[4:result.span()[0]]
            print(test_dot_sign['requirement_value'])
            print(test_dot_sign['function_base_name'])
        #匹配到主成功场景
        elif re.search(main_success_pattern,line):
            test_dot_sign['main_success_list']=[]
            test_dot_sign['test_case_sign']= 'main_success_list' #标志后续用例为主成功场景
            print(line)
        #匹配到扩展
        elif re.search(extend_pattern,line):
            test_dot_sign['extend_list']=[]
            test_dot_sign['test_case_sign']= 'extend_list' #标志后续用例为扩展
            print(line)
        #匹配到约束条件
        elif re.search(constraint_pattern,line):
            test_dot_sign['constraint_list']=[]
            test_dot_sign['test_case_sign']= 'constraint_list' #标志后续用例为约束条件
            print(line)
        #匹配到前置步骤
        elif re.search(pre_step_pattern,line):
            test_dot_sign['pre_step_list']=[]
            test_dot_sign['test_case_sign']= 'pre_step_list' #标志后续用例为前置步骤条件
            print(line)
    print(test_dot_parts)
    return test_dot_parts

header_list = ["所属模块","用例标题","前置条件","步骤","预期","关键词","优先级","用例类型","适用阶段","相关研发需求"]
type_value = ['功能测试','性能测试','配置相关','安装部署','安全相关','接口测试','单元测试','其他']
stage_value = ['单元测试阶段','功能测试阶段','集成测试阶段','系统测试阶段','冒烟测试阶段','版本验证阶段']

def gen_testcases(test_dot_parts:list,file_path:str):
    '''生成CSV文件格式的测试用例'''
    with open(file_path,mode='w',encoding='utf-8',newline="") as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(header_list)
        for test_dot in test_dot_parts:
            testcase = [None for i in range(len(header_list))]
            testcase[0] = test_dot['module_value'] #所属模块
            testcase[9] = test_dot['requirement_value'] #相关研发需求
            testcase[5] = test_dot['function_base_name'] #关键字
            testcase[6] = str(3) #优先级
            testcase[7] = type_value[0] #用例类型
            testcase[8] = stage_value[1] #适用阶段

            #录入前置步骤文本
            for index in range(len(test_dot['pre_step_list'])):
                step = test_dot['pre_step_list'][index]
                testcase[2] = str.format("{}. {}\n",index+1,str(step)[:-1])#用例前置条件

            #录入主成功场景文本，若存在扩展文本，则后续录入扩展文本
            if 'main_success_list' in test_dot and len(test_dot['main_success_list'])>0:
                testcase[1]  = str.format('{}的主成功场景',test_dot['function_base_name']) #用例标题

                #录入主成功场景文本
                for i in range(len(test_dot['main_success_list'])):
                    main_case = test_dot['main_success_list'][i]
                    step_results = str(main_case).split(':')
                    testcase[3] = str.format('{}. {}',i+1,step_results[0]) #步骤
                    testcase[4] = str.format('{}. {}',i+1,step_results[1]) #预期

                #若存在扩展文本，则录入扩展文本
                if 'extend_list' in test_dot and len(test_dot['extend_list'])>0:
                    testcase[1] = str.format('{}和扩展',testcase[1])
                    for i in range(len(test_dot['extend_list'])):
                        extend_case = test_dot['extend_list'][i]
                        step_results = str(extend_case).split(':')
                        testcase[3] = str.format('{}\n{}. {}',testcase[3],i+2,step_results[0]) #步骤
                        testcase[4] = str.format('{}\n{}. {}',testcase[4],i+2,step_results[1]) #预期

            #录入约束条件，若不存在扩展文本，则与主成功场景合并。若存在扩展文本，则新起一条用例
            if 'constraint_list' in test_dot and len(test_dot['constraint_list']):
                #存在扩展文本
                if str(testcase[1]).find("和")>=0:
                    writer.writerow(testcase.copy())
                    testcase[1]=str.format('{}的约束条件',test_dot['function_base_name']) #标题
                    testcase[3]="" #步骤
                    testcase[4]="" #预期
                    index = 0
                #不存在扩展文本
                else:
                    index = 1
                    testcase[1]=str.format('{}和约束条件',testcase[2]) #标题
                #录入约束条件文本
                for item in test_dot['constraint_list']:
                    for case in item['cases']:
                        index+=1
                        step_results = str(case).split(':')
                        if index == 1:
                            testcase[3] = str.format('{}{}. {}',testcase[3],index,step_results[0])
                            testcase[4] = str.format('{}{}. {}',testcase[4],index,step_results[1])
                        else:
                            testcase[3] = str.format('{}\n{}. {}',testcase[3],index,step_results[0])
                            testcase[4] = str.format('{}\n{}. {}',testcase[4],index,step_results[1])

            writer.writerow(testcase.copy())
