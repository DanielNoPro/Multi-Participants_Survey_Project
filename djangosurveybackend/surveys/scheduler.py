import logging
from datetime import datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution

logger = logging.getLogger(__name__)


# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def send_callback_token(
    token_service_class,
    mail_service,
    user: str,
    survey: str,
    redirect_link_patterns: str,
    alias_type: str,
    token_type: str,
    survey_end_time: datetime,
):
    success: bool = token_service_class.send_token(
        user=user,
        alias_type=alias_type,
        token_type=token_type,
        survey=survey,
        redirect_link_patterns=redirect_link_patterns,
    )

    if not success:
        logger.error("Send call back token failed")
        raise RuntimeError("Send call back token failed")
    else:
        logger.info("Send call back token success")
        send_survey_reminder(mail_service, user, survey, survey_end_time)


def send_survey_reminder(
    mail_service, user: str, survey: str, survey_end_time: datetime
):
    reminder_job_id = f"{user}_survey_{survey}_reminder"
    send_reminder_time = survey_end_time - settings.REMINDER_SURVEY_INTERVAL

    if send_reminder_time < timezone.now():
        logger.warning("Survey reminder time is in past")
        return

    if scheduler.get_job(job_id=reminder_job_id):
        logger.warning("Survey reminder job is already scheduled")
        return

    scheduler.add_job(
        mail_service.send,
        id=reminder_job_id,
        next_run_time=send_reminder_time,
        kwargs={
            "from_email": settings.SURVEY_SENDER,
            "to": user,
            "subject": settings.SURVEY_SUBJECT,
            "template": settings.SURVEY_TEMPLATE,
            "context": {},
            "reply_to": None,
        },
    )
    logger.info(f"Schedule sending survey reminder by '{str(send_reminder_time)}'")


def cancel_survey_reminder(email: str, survey_id: str):
    reminder_job_id = f"{email}_survey_{survey_id}_reminder"
    try:
        scheduler.remove_job(job_id=reminder_job_id)
        logger.info(f"Remove survey reminder job '{reminder_job_id}' successfully")
    except JobLookupError as e:
        logger.error(e)


def start():
    scheduler.start()
