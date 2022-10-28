# -*- coding: utf-8 -*-
# @Time    : 2022/10/11 14:02
# @Author  : Tom_zc
# @FileName: scan_server_info.py
# @Software: PyCharm
import os
import logging
import shutil
import traceback
from django.conf import settings

from open_infra.utils.common import execute_cmd3_with_tmp, load_yaml

logger = logging.getLogger("django")


class CollectServerInfoGlobalConfig:
    clone_cmd = "cd {} && git clone https://{}@github.com/opensourceways/infra-community"
    default_domain = "https://119.8.122.167:5443"


class CollectServerInfo:

    @staticmethod
    def get_data():
        infra_community_dir = os.path.join(settings.LIB_PATH, "infra-community")
        kubeconfig_path = os.path.join(settings.BASE_DIR, "config/kubeconfig/cluster-kubeconfig")
        try:
            server_name_dict, domain_dict, cluster_domain_dict = dict(), dict(), dict()
            if not os.path.exists(infra_community_dir):
                os.mkdir(infra_community_dir)
            cmd = CollectServerInfoGlobalConfig.clone_cmd.format(infra_community_dir, settings.GITHUB_SECRET)
            ret, out_data, err = execute_cmd3_with_tmp(cmd)
            if ret != 0:
                raise Exception("[CollectServerInfoGlobal] get data error{}".format(err))
            for dir_path, _, filenames in os.walk(infra_community_dir):
                for filename in filenames:
                    full_path = os.path.join(dir_path, filename)
                    if ".github" in full_path:
                        continue
                    elif filename == "project.yaml":
                        dict_data = load_yaml(full_path)
                        cluster_alias_list = dict_data["spec"]["destinations"]
                        for cluster_alias in cluster_alias_list:
                            if cluster_alias["server"] == "https://kubernetes.default.svc":
                                cluster_domain_temp = {
                                    cluster_alias["name"]: CollectServerInfoGlobalConfig.default_domain}
                            else:
                                cluster_domain_temp = {cluster_alias["name"]: cluster_alias["server"]}
                            cluster_domain_dict.update(cluster_domain_temp)
                    elif filename.endswith(".yaml"):
                        dict_data = load_yaml(full_path)
                        if not isinstance(dict_data, dict):
                            logger.error("[CollectServerInfoGlobal] {}:{}".format(full_path, dict_data))
                            continue
                        if dict_data.get("metadata") is None:
                            logger.error("[CollectServerInfoGlobal] {}:{}".format(full_path, dict_data))
                            continue
                        if dict_data["metadata"].get("name") is None:
                            logger.error("[CollectServerInfoGlobal] {}:{}".format(full_path, dict_data))
                            continue
                        server_name = dict_data["metadata"]["name"]
                        namespace = dict_data["spec"]["destination"]["namespace"]
                        cluster_alias = dict_data["spec"]["destination"]["name"]
                        server_name_dict[server_name] = {"namespace": namespace, "cluster": cluster_alias}
            for dir_path, _, filenames in os.walk(kubeconfig_path):
                for filename in filenames:
                    if filename.endswith(".yaml"):
                        full_path = os.path.join(dir_path, filename)
                        dict_data = load_yaml(full_path)
                        current_context = dict_data["current-context"]
                        domain_list = [cluster["cluster"]["server"] for cluster in dict_data["clusters"] if
                                       cluster["name"] == current_context]
                        cluster_name = filename.split(".")
                        domain_dict[domain_list[0]] = cluster_name[0]
            for _, info in server_name_dict.items():
                domain = cluster_domain_dict.get(info["cluster"])
                info["cluster"] = domain_dict.get(domain)
                info["cluster_url"] = domain
            return server_name_dict
        except Exception as e:
            logger.error("[CollectServerInfoGlobal] get data error:{}, traceback:{}".format(e, traceback.format_exc()))
            return dict()
        finally:
            if os.path.exists(infra_community_dir):
                shutil.rmtree(infra_community_dir)


def scan_server_info():
    collect_server_info = CollectServerInfo()
    collect_server_info.get_data()


if __name__ == '__main__':
    scan_server_info()
