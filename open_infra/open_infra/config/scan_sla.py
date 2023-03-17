# -*- coding: utf-8 -*-
import yaml

with open("./sla.txt", "r", encoding="utf-8") as f:
    content = f.readlines()
ret_list = list()
for c in content:
    c_list = c.split("@")
    dict_data = dict()
    dict_data["service_alias"] = c_list[0].strip()
    dict_data["service_introduce"] = c_list[1].strip()
    dict_data["url"] = c_list[-1].strip()
    ret_list.append(dict_data)

with open("sla.yaml", 'w') as f:
    yaml.dump(ret_list, f, allow_unicode=True)
