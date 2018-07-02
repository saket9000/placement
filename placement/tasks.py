from celery.decorators import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

from .add import add_celery, add_schedule

logger = get_task_logger(__name__)


@task(name="celery_test_task")
def celery_test_task(num1, num2):
    """sends an email when feedback form is filled successfully"""
    logger.info("Testing Celery")
    return add_celery(num1, num2)


@periodic_task(run_every=(crontab(minute='*/1')),
               name="add_number",
               ignore_result=True)
def add_number():
    add_schedule()
    logger.info("ADDING")
