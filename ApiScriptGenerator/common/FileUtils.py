import yaml

def load_yaml_file(yaml_path):
    '''
    加载YAML
    '''
    data = {}
    with open(file=yaml_path,mode="rb") as yf:
        data = yaml.load(yf,Loader=yaml.FullLoader)
    return data