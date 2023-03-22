# -*- coding: utf-8 -*-
# @Time    : 2023/2/23 15:58
# @Author  : Tom_zc
# @FileName: scan_image.py
# @Software: PyCharm
import itertools
import os
import shutil
import traceback
import yaml
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkswr.v2.region.swr_region import SwrRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkswr.v2 import *
from django.conf import settings
from open_infra.utils.common import execute_cmd3_with_tmp, convert_yaml, load_yaml
from logging import getLogger
from yaml.loader import SafeLoader

logger = getLogger("django")


class GlobalConfig:
    url_list = [
        "https://gitee.com/opengauss/infra.git",
        "https://github.com/opensourceways/infra-openeuler.git",
        "https://github.com/opensourceways/infra-mindspore.git",
        "https://github.com/opensourceways/infra-openlookeng.git",
        "https://github.com/opensourceways/infra-common.git"
    ]
    clone_cmd = "cd {} && git config --global user.name TomNewChao && git config --global user.email 353712216@qq.com && git clone {}"
    kustomize_cmd = "cd {} && kustomize build ."
    service_kind = ["deployment", "statefulset", "job", "deamonset"]
    job_kind = ["cronjob"]
    ak = settings.OBS_AK
    sk = settings.OBS_SK


class CollectServiceInfo:
    @staticmethod
    def get_swr():
        """through the http request to get the list of swr repo"""
        repos_list = list()
        request_begin = 0
        try:
            credentials = BasicCredentials(GlobalConfig.ak, GlobalConfig.sk)
            client = SwrClient.new_builder() \
                .with_credentials(credentials) \
                .with_region(SwrRegion.value_of("cn-north-4")) \
                .build()
            while True:
                request = ListReposDetailsRequest(limit='100', offset=str(request_begin))
                response = client.list_repos_details(request)
                repos_list.extend(response.body)
                if len(response.body) == 100:
                    request_begin += 100
                else:
                    break
            logger.info("[CollectServiceInfo] get_swr len:{}".format(len(repos_list)))
        except exceptions.ClientRequestException as e:
            logger.error("[CollectServiceInfo] request_id:{}, code:{}, msg:{}".format(e.request_id,
                                                                                      e.error_code,
                                                                                      e.error_msg))
        return repos_list

    @staticmethod
    def parse_swr(swr_list):
        """parse the swr data"""
        dict_data = dict()
        for swr_info in swr_list:
            if swr_info.description:
                meta_data = dict()
                try:
                    description_obj = convert_yaml(swr_info.description)
                    if isinstance(description_obj, list):
                        for des in description_obj:
                            meta_data.update(des)
                    elif isinstance(description_obj, dict):
                        meta_data.update(description_obj)
                    if len(meta_data) == 0:
                        continue
                    if "build_config" in meta_data.keys() and not isinstance(meta_data["build_config"], list):
                        continue
                    meta_data["path"] = swr_info.path
                    meta_data["num_download"] = swr_info.num_download
                    meta_data["size"] = swr_info.size
                    dict_data[swr_info.path] = meta_data
                except Exception as e:
                    logger.error("[CollectServiceInfo] parse_swr e:{}, traceback:{}".format(e, traceback.format_exc()))
        logger.info("[CollectServiceInfo] find the data:{}.".format(len(dict_data.keys())))
        return dict_data

    @staticmethod
    def read_deploy_config(kustomization_path):
        cluster, region = str(), str()
        try:
            kustomization_info = load_yaml(kustomization_path)
            if kustomization_info.get("commonAnnotations") and \
                    kustomization_info["commonAnnotations"].get("kubernetes.ops.cluster"):
                cluster = kustomization_info["commonAnnotations"]["kubernetes.ops.cluster"]
            if kustomization_info.get("commonAnnotations") and \
                    kustomization_info["commonAnnotations"].get("kubernetes.ops.region"):
                region = kustomization_info["commonAnnotations"]["kubernetes.ops.region"]
            return True, cluster, region
        except Exception as e:
            logger.error("[read_deploy_config] {}, tracekback:{}".format(e, traceback.format_exc()))
            return False, cluster, region

    @staticmethod
    def get_deploy_config():
        """get the config of k8s"""
        logger.info("[CollectServiceInfo] start to get config data...")
        infra_service_dir = os.path.join(settings.LIB_PATH, "service")
        if os.path.exists(infra_service_dir):
            shutil.rmtree(infra_service_dir)
        os.mkdir(infra_service_dir)
        all_list_data = list()
        for repo in GlobalConfig.url_list:
            try:
                logger.info("1.start to git clone:{}".format(repo))
                file_name = repo.split("/")[-1].split(".")[0]
                cmd = GlobalConfig.clone_cmd.format(infra_service_dir, repo)
                ret, out_data, err = execute_cmd3_with_tmp(cmd)
                if ret != 0 and "deprecated" not in err:
                    raise Exception("[CollectServiceInfo] git clone failed: {}".format(err))
                object_dirname = os.path.join(infra_service_dir, file_name)
                logger.info("2.start to parse data, the path is:{}".format(object_dirname))
                for dir_path, _, filenames in os.walk(object_dirname):
                    if ".github" in dir_path:
                        continue
                    elif ".git" in dir_path:
                        continue
                    elif "common-services" in dir_path:
                        continue
                    elif len(filenames) == 0:
                        continue
                    is_in_kustomization_dir,  cluster, region = False, str(), str()
                    for filename in filenames:
                        if "kustomization.yaml" == filename:
                            kustomization_path = os.path.join(dir_path, filename)
                            is_ok, cluster, region = CollectServiceInfo.read_deploy_config(kustomization_path)
                            if is_ok:
                                is_in_kustomization_dir = True
                                break
                            else:
                                continue
                    if is_in_kustomization_dir:
                        try:
                            cmd = GlobalConfig.kustomize_cmd.format(dir_path)
                            ret, out_data, err = execute_cmd3_with_tmp(cmd)
                            list_data = yaml.load_all(out_data, Loader=SafeLoader)
                            for data in list_data:
                                if data['kind'].lower() in GlobalConfig.service_kind:
                                    if int(data['spec'].get("replicas", 1)) == 0:
                                        continue
                                    dict_data = dict()
                                    dict_data["service_name"] = data["metadata"]["name"]
                                    dict_data["namespace"] = data["metadata"]["namespace"]
                                    dict_data["cluster"] = cluster
                                    dict_data["region"] = region
                                    dict_data["image"] = list()
                                    container_list = data["spec"]["template"]["spec"]["containers"]
                                    for container in container_list:
                                        c = dict()
                                        c["image"] = container["image"]
                                        if container.get("resources") and container["resources"].get("limits"):
                                            c["cpu"] = container["resources"]["limits"].get("cpu", "")
                                            c["mem"] = container["resources"]["limits"].get("memory", "")
                                        else:
                                            c["cpu"] = ""
                                            c["mem"] = ""
                                        dict_data["image"].append(c)
                                    all_list_data.append(dict_data)
                                elif data['kind'].lower() in GlobalConfig.job_kind:
                                    if data['spec'].get("suspend", False):
                                        continue
                                    dict_data = dict()
                                    dict_data["service_name"] = data["metadata"]["name"]
                                    dict_data["namespace"] = data["metadata"]["namespace"]
                                    dict_data["cluster"] = cluster
                                    dict_data["region"] = region
                                    dict_data["image"] = list()
                                    container_list = data["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"]
                                    for container in container_list:
                                        c = dict()
                                        c["image"] = container["image"]
                                        if container.get("resources") and container["resources"].get("limits"):
                                            c["cpu"] = container["resources"]["limits"].get("cpu", "")
                                            c["mem"] = container["resources"]["limits"].get("memory", "")
                                        else:
                                            c["cpu"] = ""
                                            c["mem"] = ""
                                        dict_data["image"].append(c)
                                    all_list_data.append(dict_data)
                        except Exception as e:
                            logger.error(
                                "[CollectServiceInfo] get_deploy_config, path:{},e:{},traceback:{}".format(dir_path, e,
                                                                                                           traceback.format_exc()))
                    else:
                        pass
                logger.info("[CollectServiceInfo] collect data is:{}".format(len(all_list_data)))
            except Exception as e:
                logger.error("[scan_image]e:{},traceback:{}".format(e, traceback.format_exc()))
        if os.path.exists(infra_service_dir):
            shutil.rmtree(infra_service_dir)
        return all_list_data

    @classmethod
    def get_service(cls):
        """get all the data"""
        swr_list = cls.get_swr()
        swr_info = cls.parse_swr(swr_list)
        config = cls.get_deploy_config()
        return swr_info, config
