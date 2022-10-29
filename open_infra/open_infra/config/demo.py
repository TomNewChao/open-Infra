# -*- coding: utf-8 -*-
# @Time    : 2022/10/29 15:28
# @Author  : Tom_zc
# @FileName: demo.py.py
# @Software: PyCharm
import yaml


def load_yaml(file_path, method="load"):
    """read yaml to yaml obj"""
    yaml_load_method = getattr(yaml, method)
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml_load_method(file, Loader=yaml.FullLoader)


if __name__ == '__main__':
    list_data = load_yaml("./sla_bak.yaml")
    ret_list = list()
    print(list_data)
    for i in list_data:
        dict_data = dict()
        dict_data["name"] = i.get("name-alias", "")
        dict_data["name-alias"] = i.get("name", "")
        dict_data["introduce"] = i["introduce"]
        ret_list.append(dict_data)
    print(ret_list)
    with open("./sla_demo.yaml", "w", encoding="utf-8") as f:
        yaml.dump(ret_list, f, encoding="utf-8", default_flow_style=False, allow_unicode=True)
