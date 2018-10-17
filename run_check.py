import os
import json
import constants1
from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import azure
import gcp
import aws


if __name__ == '__main__':

    services = constants1.SERVICES

    SCHEDULER_INTERVAL = constants1.SCHEDULER_INTERVAL  # in seconds
    executors = {
        'default': ThreadPoolExecutor()
    }

    app_scheduler = BlockingScheduler(executors=executors, timezone=utc)

    for service in services:
        if service == 'aws':

            app_scheduler.add_job(aws.run , 'interval', seconds=10,
                                  id='aws check scheduler')

        if service == 'gcp':

            app_scheduler.add_job(gcp.run , 'interval', seconds=10,
                                  id='gcp check scheduler')

        if service == 'azure':

            app_scheduler.add_job(azure.run , 'interval', seconds=10,
                                  id='azure check scheduler')


    app_scheduler.start()
