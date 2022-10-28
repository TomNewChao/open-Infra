# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 18:04
# @Author  : Tom_zc
# @FileName: utils_kubeconfig.py
# @Software: PyCharm
import os
import shutil
import stat
import logging
import time
import traceback

from django.conf import settings

from open_infra.utils.common import execute_cmd3_with_tmp

logger = logging.getLogger("django")


class KubeconfigGlobalConfig:
    script_path = "config/kubeconfig/script"
    create_cmd = "cd {path} && {script_path} {namespace} {cluster} {new_kubeconfig_path} {server} {username} {role} {kubeconfig_path}"
    delete_cmd = "{script_path} {namespace} {kubeconfig_path} {username} {role}"


# noinspection PyMethodMayBeStatic
class KubeconfigLib(object):

    @staticmethod
    def create_kubeconfig(dict_data):
        """create kubeconfig
        @param dict_data: dict and contain namespace and cluster username role url
        @return: True/False, data
        """
        namespace = dict_data["namespace"]
        cluster = dict_data["cluster"]
        username = dict_data["username"]
        role = dict_data["role"]
        url = dict_data["url"]
        try:
            kubeconfig_path = os.path.join(settings.BASE_DIR,
                                           r"config/kubeconfig/cluster-kubeconfig/{}.yaml".format(cluster))
            # create kubeconfig dir
            kubeconfig_dir = os.path.join(settings.LIB_PATH, "kubeconfig")
            if not os.path.exists(kubeconfig_dir):
                os.mkdir(kubeconfig_dir)
            sub_kubeconfig_dir_name = "{}_{}_{}_{}".format(cluster, namespace, username, int(time.time()))
            sub_kubeconfig_full_path = os.path.join(kubeconfig_dir, sub_kubeconfig_dir_name)
            if not os.path.exists(sub_kubeconfig_full_path):
                os.mkdir(sub_kubeconfig_full_path)
            source_dir = os.path.join(settings.BASE_DIR, KubeconfigGlobalConfig.script_path)
            destination_dir = os.path.join(sub_kubeconfig_full_path, "script")
            shutil.copytree(source_dir, destination_dir)
            script_path = os.path.join(sub_kubeconfig_full_path, r"script/script.sh")
            out_path = os.path.join(sub_kubeconfig_full_path, r"script/{}".format(sub_kubeconfig_dir_name))
            os.chmod(script_path, stat.S_IXGRP)
        except Exception as e:
            logger.error("[create_kubeconfig] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return False, ""
        try:
            cmd = KubeconfigGlobalConfig.create_cmd.format(
                path=destination_dir,
                script_path=script_path,
                namespace=namespace,
                cluster=cluster,
                new_kubeconfig_path=out_path,
                server=url,
                username=username,
                role=role,
                kubeconfig_path=kubeconfig_path
            )
            # logger.error("[create_kubeconfig] cmd is:{}".format(cmd))
            ret, out_data, err = execute_cmd3_with_tmp(cmd)
            if ret != 0:
                logger.error("[create_kubeconfig] {}".format(err))
                return False, ""
            with open(out_path, "rb") as f:
                out_data = f.read()
            return True, out_data
        except Exception as e:
            logger.error("[create_kubeconfig] {}".format(e))
            return False, ""
        finally:
            if os.path.exists(sub_kubeconfig_full_path):
                shutil.rmtree(sub_kubeconfig_full_path)

    @staticmethod
    def delete_kubeconfig(dict_data):
        """ delete kubeconfig
        @param dict_data: dict and contain namespace and cluster and role and username
        @return:
        """
        namespace = dict_data["namespace"]
        cluster = dict_data["cluster"]
        username = dict_data["username"]
        role = dict_data["role"]
        kubeconfig_path = os.path.join(settings.BASE_DIR,
                                       r"config/kubeconfig/cluster-kubeconfig/{}.yaml".format(cluster))
        script_path = os.path.join(settings.BASE_DIR,
                                   r"config/kubeconfig/script/deleteRoleScript.sh")
        os.chmod(script_path, stat.S_IXGRP)
        cmd = KubeconfigGlobalConfig.delete_cmd.format(
            script_path=script_path,
            namespace=namespace,
            kubeconfig_path=kubeconfig_path,
            username=username,
            role=role
        )
        # logger.error("[delete_kubeconfig] cmd is:{}".format(cmd))
        ret, out_data, err = execute_cmd3_with_tmp(cmd)
        if ret != 0 and "NotFound" not in err:
            raise Exception("[delete_kubeconfig] {}".format(err))
        return True
