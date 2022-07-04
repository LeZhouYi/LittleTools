

class ApiMap(object):
    '''测试点和API对应关系的数据结构'''
    ADD = 'add'
    DELETE = 'delete'
    FIND = 'find'
    DETAIL = 'detail'
    EDIT = 'modify'


    def __init__(self,mapping:dict) -> None:
        self.add = None
        self.delete = None
        self.find = None
        self.detail = None
        self.modify = None
        for key,value in mapping.items():
            assert 'key' in value and 'api' in value and 'testdot' in value
            if key == self.ADD:
                self.add = value
            elif key == self.DELETE:
                self.delete = value
            elif key == self.FIND:
                self.find = value
            elif key == self.DETAIL:
                self.detail = value
            elif key == self.EDIT:
                self.modify = value

    def __find_method__(self,method:str)->dict:
        '''获取对应的方法结构'''
        if method == self.ADD:
            return self.add
        elif method == self.DELETE:
            return self.delete
        elif method == self.FIND:
            return self.find
        elif method == self.DETAIL:
            return self.detail
        elif method == self.EDIT:
            return self.modify
        return None

    def is_exist_method(self,method:str)->bool:
        '''是否存在对应方法'''
        return self.__find_method__(method)!=None

    def get_api(self,method:str)->str:
        '''获取api的文件路径'''
        method_dict = self.__find_method__(method)
        return None if method_dict==None else method_dict['api']

    def get_testdot(self,method:str)->str:
        '''获取功能点的文件路径'''
        method_dict = self.__find_method__(method)
        return None if method_dict==None else method_dict['testdot']

    def get_key(self,method:str)->str:
        '''获取关键字前缀'''
        method_dict = self.__find_method__(method)
        return None if method_dict==None else method_dict['key']