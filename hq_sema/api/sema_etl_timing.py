# -*- coding: utf-8 -*-

import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from etl.sema_etl import sema_etl_timing_execute


def start():
    def add_job(func, timeSpace, delaySeconds=0):
        # 先马上开始执行
        # scheduler.add_job(func, 'date',misfire_grace_time=120) #misfire_grace_time=120,
        # 后再抓取之后的某个时间段开始间隔执行
        # next_run_time:设置下一轮开始时间
        # max_instances：如 1：表示当前方法正在执行还没有执行完，则不能再次启动这个方法，需等待完成，同理其他数
        # misfire_grace_time:120代表2分钟，当一个任务missing之后，在两分钟内会被重试
        scheduler.add_job(func, 'interval', seconds=timeSpace, misfire_grace_time=120,
                          next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=delaySeconds),
                          start_date=datetime.datetime.now() + datetime.timedelta(seconds=timeSpace), max_instances=1)

    timeSpace = 2 * 60 * 60
    scheduler = BlockingScheduler(daemonic=False)

    add_job(sema_etl_timing_execute, timeSpace)

    scheduler.start()


if __name__ == '__main__':
    start()
