import datetime
import json
import logging
import random

import pytz
from django.conf import settings
from django.dispatch import Signal
from google.cloud.tasks_v2.proto.target_pb2 import HttpRequest
from google.cloud.tasks_v2.proto.task_pb2 import Task
from google.protobuf.timestamp_pb2 import Timestamp

from gcloudtasks.utils import get_client, get_path, get_model_class

client = get_client()

logger = logging.getLogger(__name__)

task_created_signal = Signal(providing_args=['context'])


def create_task(
        queue_name: str,
        call: str,
        payload: dict = None,
        name: str = None,
        delay: datetime.timedelta = None,
        scheduled_time: datetime.datetime = None,
        host: str = None
) -> str:
    """
    :param queue_name: This takes in the name of the queue we want to pass the task on to
    :param call: The absolute path of the class of the task
    :param payload: The data we want to pass into the executing function
    :param name: The name of the task, if none is provided, one is automatically generated.
    :param delay: This takes in a timedelta object which you want to delay the task for, this takes precedence over the
    schedule time, should both be provided.
    :param scheduled_time: This takes in datetime object of the schedule, you have to make sure this object is
    timezone-aware
    :param host: This is the host that collects the task, this is here for the sake of multi-tenant systems, or maybe
    you wish to let different systems process specific type of tasks
    :return taskname, this can be used to manage the task, maybe store it for future reference, delete it
    before it's executed
    """
    if not payload:
        payload = dict()
    parent = client.queue_path(settings.GTASK_PROJECT_ID, settings.GTASK_PROJECT_LOCATION, queue_name)
    if name:
        name = client.task_path(settings.GTASK_PROJECT_ID, settings.GTASK_PROJECT_LOCATION, queue_name, name)
    request = HttpRequest(url=get_path(host), headers={'Content-Type': 'application/json'},
                          body=json.dumps({'call': call, 'payload': payload}).encode('utf-8'))
    if scheduled_time and not delay:
        if not (scheduled_time.tzinfo is not None and scheduled_time.tzinfo.utcoffset(scheduled_time) is not None):
            logger.warning('The schedule time you passed is not timezone-aware, this would be converted to UTC, if '
                           'this is not the timezone you want, please make changes.')
            scheduled_time = scheduled_time.replace(tzinfo=pytz.utc)
    if delay:
        assert isinstance(delay, datetime.timedelta), 'Expected timedelta instance as delay'
        scheduled_time = datetime.datetime.utcnow() + delay
    if scheduled_time:
        scheduled_time = Timestamp(seconds=int(scheduled_time.timestamp()))
    task = {'name': name,
            'schedule_time': scheduled_time,
            'http_request': request}
    response = client.create_task(parent, Task(**task))
    return str(response.name)


def delete_task(name):
    """:param name: Takes in the full name of the task as returned in the create_task method above"""
    client.delete_task(name)


class CloudTask:
    def __init__(self, queue, name, call, payload):
        self.queue = queue
        self.name = name
        self.call = call
        self.payload = payload

    def run(self, delay=None, scheduled_time=None, host=None):
        task_id = str(random.randint(1000000000, 9999999999))
        to_remote = getattr(settings, 'GTASK_SEND_TO_REMOTE', True)
        if to_remote:
            task_id = create_task(self.queue, self.call, self.payload, self.name, delay, scheduled_time, host)
            logger.info(f'Task {self.name} has been sent to queue {self.queue}')
        else:
            logger.info(f'{self.call} has been executed locally')
            if delay:
                logger.info(f'But schedule parameter was added to run after {str(delay)} seconds.')

            if scheduled_time and not delay:
                logger.info(f'But schedule parameter was added to run on {str(scheduled_time)}')

        # Log it to the database
        Model = get_model_class()
        delay = delay.seconds if delay else 0
        obj = Model.objects.create(
            task_id=task_id, is_local=not to_remote, scheduled_time=scheduled_time, delay=delay
        )
        # Send out signal
        task_created_signal.send(obj.__class__, instance=obj, created=True)
