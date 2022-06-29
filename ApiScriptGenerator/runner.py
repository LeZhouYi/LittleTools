import os
from common.ApiScriptGenerator import *

if __name__ == '__main__':
    file_path = str.format('{}/{}',os.getcwd(),'api/MathConcept-portal.yaml')
    out_path = str.format('{}/{}',os.getcwd(),'script')
    api_dict = load_yaml_file(file_path)
    script_datas = gen_api_scripts(api_dict)
    write_api_file(script_datas,out_path)