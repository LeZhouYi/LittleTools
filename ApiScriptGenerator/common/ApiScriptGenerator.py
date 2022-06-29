import os
import yaml
import copy
from typing import List

def load_yaml_file(yaml_path):
    '''
    加载YAML
    '''
    data = {}
    with open(file=yaml_path,mode="rb") as yf:
        data = yaml.load(yf,Loader=yaml.FullLoader)
    return data

def get_tag(tags:list,tag_key):
    '''
    获取模块名
    '''
    for tag in tags:
        if tag_key == tag['name']:
            return tag['description']
    return tag_key

def get_component(apis:dict,path_str:str):
    '''获取组件'''
    paths = path_str.split('/')
    result = apis
    for path in paths:
        if path == '#':
            result = apis
        else:
            result = result[path]
    return result

class ApiScript(object):
    '''
    存储API数据的结构
    '''
    def __init__(self) -> None:
        self.client_env = "" #客户端环境
        self.data = {
            "name": "", #接口名
            "base_url": "", #基础URL
            "variables": {}, #参数列表
            "request":{
                "headers":{}
            }
        }

    def set_client_env(self,client_env:str)->None:
        '''
        设置客户端环境
        '''
        self.client_env = client_env

    def update_client_variables(self)->None:
        '''
        添加并更新与Client_env相关的变量
        '''
        self.data['variables'][self.client_env]=self.client_env
        self.data['base_url']= '${ENV(app_base_url)}' if self.client_env!='portal_access_token' else '${ENV(portal_base_url)}'

    def update_authorization(self,apis:dict)->None:
        '''
        添加校验的相关变量和方法
        '''
        authorization = None if 'security' not in apis else apis['security'][0] #获取验证方式
        if authorization!=None:
            if str(authorization).find('bearerAuth'):
                self.data['request']['headers']['Authorization'] = str.format('Bearer ${}',self.client_env) #验证

    def set_url(self,path_key:str)->None:
        '''
        设置url
        '''
        self.data['request']['url'] = path_key #API路径

    def set_method(self,method_type:str)->None:
        '''
        设置方法
        '''
        self.data['request']['method'] = method_type.upper()

    def set_name(self,name:str)->None:
        '''
        设置名字
        '''
        self.data['name']=name

    def set_tag(self,tag:str)->None:
        '''
        设置所属模块
        '''
        self.data['tag'] = tag

    def is_method(self,method:str)->bool:
        '''
        判断当前标志的方法与给出的是否一致
        '''
        return self.data['request']['method'] == method.upper()

    def add_headers_variable(self,key:str,value:str)->None:
        '''
        给Headers添加变量
        '''
        self.data['request']['headers'][key]=value

    def add_json_variable(self,key:str)->None:
        '''
        初始化Json(若无)，并添加变量
        '''
        if 'json' not in self.data['request']:
            self.data['request']['json']={}
        if self.is_method('POST') and key == 'id':
            pass
        elif self.is_method('PUT') and key == 'id':
            pass
        else:
            self.data['request']['json'][key]=str.format('${}',key)

    def add_query(self,key:str)->None:
        '''
        添加参数
        '''
        if 'params' not in self.data['request']:
            self.data['request']['params'] = str.format('{}=${}',key,key)
        else:
            self.data['request']['params'] = str.format('{}&{}=${}',self.data['request']['params'],key,key)

    def add_variables(self,key:str,type:str)->None:
        '''
        在Variables中添加变量，并根据type设置默认值
        '''
        if type == 'string':
            self.data['variables'][key] = 'TEST${gen_num_char_string(8,16)}'
        elif type == 'integer':
            if key == '_page':
                self.data['variables'][key] = '0'
            elif key == '_limit':
                self.data['variables'][key] = '50'
            elif key == 'id' and self.is_method('POST'):
                pass
            else:
                self.data['variables'][key] = '${gen_random_integer(0,100)}'
        elif type == 'object':
            self.data['variables'][key] = {}
        elif type == 'array':
            self.data['variables'][key] = []

    def update_url_path(self,key:str):
        '''
        更新url，如/user/{id}更新为/user/$id
        '''
        pattern = str.format('{}{}{}','{',key,'}')
        new_value = str.format('${}',key)
        self.data['request']['url']=str(self.data['request']['url']).replace(pattern,new_value)

    def get_file_name(self)->str:
        '''
        获取文件名称
        '''
        return str(self.data['name']).replace(" ","_")

    def get_tag(self)->str:
        '''
        获取模块名
        '''
        return self.data['tag']

    def get_name(self)->str:
        '''
        获取接口名
        '''
        return self.data['name']

    def get_base_url(self)->str:
        '''
        获取base_url
        '''
        return self.data['base_url']

    def get_variables(self)->dict:
        '''
        获取Variables
        '''
        return self.data['variables']

    def get_request(self)->dict:
        '''
        获取Variables
        '''
        return self.data['request']

def gen_api_scripts(apis:dict)->List[ApiScript]:
    '''
    解析并提供所需数据
    '''
    tags = apis['tags'] #获得模块划分

    api_scripts = [] #储存所有API脚本数据
    api_script = ApiScript()
    api_script.set_client_env('portal_access_token')#客户端环境
    api_script.update_client_variables()#添加Token变量
    api_script.update_authorization(apis)#添加安全验证

    #遍历所有API
    for path_key,path_body in apis['paths'].items():
        api_script.set_url(path_key) #API路径
        #遍历单个路径的所有操作方法
        for method_type,method_body in path_body.items():
            api_script.set_method(method_type) #API方法类型:GET,DELETE等
            api_script.set_name(method_body['summary']) #标题
            api_script.set_tag(get_tag(tags,method_body['tags'][0])) #所属模块

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
                    properties = get_component(apis,schema['$ref'])['properties']
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
                        param = get_component(apis,param['$ref'])
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
                            param = get_component(apis,param['$ref'])
                        api_script.add_variables(param['name'],param['schema']['type']) #添加变量
                        #Query部分
                        if param['in']=='query':
                            api_script.add_query(param['name'])
                        elif param['in']=='path':
                            api_script.update_url_path(param['name'])

            elif api_script.is_method('PUT'):
                api_script.add_headers_variable('Content-Type','application/json')
                schema = method_body['requestBody']['content']['application/json']['schema']
                properties = schema['properties'] if '$ref' not in schema else get_component(apis,schema['$ref'])['properties'] #获取所需结构体
                for content_key,content_value in properties.items():
                    api_script.add_json_variable(content_key) #添加Json
                    api_script.add_variables(content_key,content_value['type']) #添加变量
                #遍历参数
                for param in method_body['parameters']:
                    if '$ref' in param:
                        param = get_component(apis,param['$ref'])
                    api_script.add_variables(param['name'],param['schema']['type']) #添加变量
                    #Query部分
                    if param['in']=='path':
                        api_script.update_url_path(param['name'])

            #完成单个路径的单个方法的解析
            api_scripts.append(copy.deepcopy(api_script))
            api_script = copy.deepcopy(temp_script) #复原至最简状态

            print(str.format('{} {}',path_key,method_type))
    return api_scripts

def replace_name(name:str):
    '''调整文件名，使用_代替空格'''
    return name.replace(" ","_")

def write_api_file(api_script_bodys:List[ApiScript],out_path:str):
    '''
    生成YAML格式的API脚本
    '''
    for api_item in api_script_bodys:
        file_name = api_item.get_file_name() #文件名
        file_path = str.format('{}/{}/{}.yaml',out_path,api_item.get_tag(),file_name)
        if not os.path.exists(str.format('{}/{}',out_path,api_item.get_tag())):
            os.makedirs(str.format('{}/{}',out_path,api_item.get_tag()))
        with open(file_path,'w+') as file:
            file.write(yaml.dump({'name':api_item.get_name()},allow_unicode=True))
            file.write(yaml.dump({'base_url':api_item.get_base_url()},allow_unicode=True))
            file.write(yaml.dump({'variables':api_item.get_variables()},allow_unicode=True))
            file.write(yaml.dump({'request':api_item.get_request()},allow_unicode=True))