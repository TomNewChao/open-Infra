# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 16:03
# @Author  : Tom_zc
# @FileName: init_task.py
# @Software: PyCharm
from consumption_control.resources.bill_mgr import BillMgr
from consumption_control.resources.resource_utilization_mgr import ResourceUtilizationInitialMgr
from open_infra.utils.common import func_retry
from logging import getLogger

logger = getLogger("django")


class InitMgr:
    @classmethod
    @func_retry()
    def refresh_bill_info(cls):
        """refresh bill info"""
        # execution frequency every month
        logger.info("------------------1.start to refresh bill info----------------------")
        bill_mgr = BillMgr()
        bill_mgr.scan_bill()
        logger.info("------------------1.finish to refresh bill info---------------------")

    @classmethod
    @func_retry()
    def refresh_resource_utilization(cls):
        # execution frequency every week
        logger.info("------------------2.start to refresh resource utilization----------------------")
        resource_utilization_mgr = ResourceUtilizationInitialMgr()
        resource_utilization_mgr.resouce_utilization()
        logger.info("------------------2.start to refresh resource utilization----------------------")

    @classmethod
    def test_task(cls):
        cls.refresh_resource_utilization()
        cls.refresh_bill_info()

