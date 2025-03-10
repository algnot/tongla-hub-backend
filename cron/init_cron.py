import os
import time
import importlib.util
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def init_job(cron_expr):
    def decorator(func):
        minute, hour, day, month, day_of_week = cron_expr.split()
        trigger = CronTrigger(
            minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
        )
        scheduler.add_job(func, trigger)
        return func
    return decorator

def load_jobs_from_dir(directory="cron/job"):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module_path = os.path.join(directory, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

def init_cron():
    load_jobs_from_dir()
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
