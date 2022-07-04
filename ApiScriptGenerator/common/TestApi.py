import copy
from typing import Any, List
from ApiScript import ApiScript

class TestApi(object):
    '''储存API文档的数据结构'''

    def __init__(self,apis:dict) -> None:
        self.tags = apis['tags'] #获得模块划分
        self.api_paths = apis['paths'] #所有API路径
        self.client_env = ""
        self.authorization = None if 'security' not in apis else str(apis['security'][0]) #获取验证方式
        self.apis = apis #备份

    def set_client_env(self,client_env)->None:
        '''设置客户端环境'''
        self.client_env = client_env

    def get_tag(self,tag_key:str)->str:
        '''
        获取模块名
        '''
        for tag in self.tags:
            if tag_key == tag['name']:
                return tag['description']
        return tag_key

    def get_component(self,path_str:str)->Any:
        '''获取组件'''
        paths = path_str.split('/')
        result = self.apis
        for path in paths:
            if path == '#':
                result = self.apis
            else:
                result = result[path]
        return result

    def gen_api_scripts(self)->List[ApiScript]:
        '''解析并提供API脚本生成所需数据'''
        api_scripts = [] #储存所有API脚本数据

        api_script = ApiScript() #初始化
        api_script.set_client_env(self.client_env)#客户端环境
        api_script.update_client_variables()#添加Token变量
        api_script.update_authorization(self.authorization)#添加安全验证

        #遍历所有API
        for path_key,path_body in self.api_paths.items():
            api_script.set_url(path_key) #API路径
            #遍历单个路径的所有操作方法
            for method_type,method_body in path_body.items():
                api_script.set_method(method_type) #API方法类型:GET,DELETE等
                api_script.set_name(method_body['summary']) #标题
                api_script.set_tag(self.get_tag(method_body['tags'][0])) #所属模块

                #备份,各方法的数据体存在差异
                temp_script = copy.deepcopy(api_script)

                #POST方法的数据体解析
                if api_script.is_method('POST'):
                    if 'application/json' not in method_body['requestBody']['content']:
                        continue
                    api_script.add_headers_variable('Content-Type','application/json')
                    schema = method_body['requestBody']['content']['application/json']['schema']

                    #获取所需结构体
                    if '$ref' in schema:
                        properties = self.get_component(schema['$ref'])['properties']
                    elif 'properties' in schema:
                        properties = schema['properties']
                    else:
                        continue
                    for content_key,content_value in properties.items():
                        api_script.add_json_variable(content_key) #添加Json
                        api_script.add_variables(content_key,content_value['type']) #添加变量

                elif api_script.is_method('DELETE'):
                    #遍历参数
                    for param in method_body['parameters']:
                        if '$ref' in param:
                            param = self.get_component(param['$ref'])
                        api_script.add_variables(param['name'],param['schema']['type']) #添加变量
                        #Query部分
                        if param['in']=='query':
                            api_script.add_query(param['name'])
                        elif param['in']=='path':
                            api_script.update_url_path(param['name'])

                elif api_script.is_method('GET'):
                    if 'parameters' in method_body:
                        #遍历参数
                        for param in method_body['parameters']:
                            if '$ref' in param:
                                param = self.get_component(param['$ref'])
                            #Query部分
                            if param['in']=='query':
                                api_script.add_query(param['name'])
                                if str(param['name']).find('_page')<0 and str(param['name']).find('_limit')<0:
                                    api_script.add_variables(param['name'],"",is_random=False) #添加变量
                                    continue
                            elif param['in']=='path':
                                api_script.update_url_path(param['name'])
                            api_script.add_variables(param['name'],param['schema']['type']) #添加变量

                elif api_script.is_method('PUT'):
                    api_script.add_headers_variable('Content-Type','application/json')
                    schema = method_body['requestBody']['content']['application/json']['schema']
                    properties = schema['properties'] if '$ref' not in schema else self.get_component(schema['$ref'])['properties'] #获取所需结构体
                    for content_key,content_value in properties.items():
                        api_script.add_json_variable(content_key) #添加Json
                        api_script.add_variables(content_key,content_value['type']) #添加变量
                    #遍历参数
                    for param in method_body['parameters']:
                        if '$ref' in param:
                            param = self.get_component(param['$ref'])
                        api_script.add_variables(param['name'],param['schema']['type']) #添加变量
                        #Query部分
                        if param['in']=='path':
                            api_script.update_url_path(param['name'])

                #完成单个路径的单个方法的解析
                api_scripts.append(copy.deepcopy(api_script))
                api_script = copy.deepcopy(temp_script) #复原至最简状态

                print(str.format('{} {}',path_key,method_type))
        return api_scripts