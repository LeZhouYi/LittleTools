
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
                "url":"",
                "method":"",
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
        self.data['variables']['access_token']=self.client_env
        self.data['base_url']= '${ENV(app_base_url)}' if self.client_env!='portal_access_token' else '${ENV(portal_base_url)}'

    def update_authorization(self,authorization:str)->None:
        '''
        添加校验的相关变量和方法
        '''
        if authorization!=None:
            if authorization.find('bearerAuth'):
                self.data['request']['headers']['Authorization'] = str.format('Bearer ${}','access_token') #验证

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

    def add_variables(self,key:str,type:str,is_random:bool=True)->None:
        '''
        在Variables中添加变量，并根据type设置默认值
        is_random=True时，根据type的类型字段来生成随机值或对应的生成函数
        is_random=False时，值等于Type的值
        '''
        if not is_random:
            self.data['variables'][key] = type
        elif type == 'string':
            self.data['variables'][key] = 'TEST${gen_num_char_string(8,16)}'
        elif type == 'integer':
            if key == '_page':
                self.data['variables'][key] = 0
            elif key == '_limit':
                self.data['variables'][key] = 50
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