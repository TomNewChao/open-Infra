# -*- coding: utf-8 -*-

import datetime


def calc_next_run_time(exec_interval):
    delta = datetime.timedelta(seconds=exec_interval)
    now_time = datetime.datetime.now()
    run_time = now_time + delta
    return run_time
