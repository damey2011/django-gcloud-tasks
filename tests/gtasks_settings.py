import os

from django.conf import settings


GTASK_PROJECT_ID = os.environ.get('GTASK_PROJECT_ID', 'cccbusiness-201513')
GTASK_PROJECT_LOCATION = os.environ.get('GTASK_PROJECT_LOCATION', 'us-central1')
GTASK_CREDENTIAL_FILE = os.environ.get('GTASK_CREDENTIAL_FILE', os.path.join(
    settings.BASE_DIR, 'virtualmatches', 'cccbusiness-201513-57bbaefb5fc5.json'
))
GTASK_ON_ERROR = os.environ.get('GTASK_ON_ERROR', None)
GTASK_RETRY_DEADLINE = os.environ.get('GTASK_RETRY_DEADLINE', 10)
# only applies to new queues
GTASK_TARGET_WORKER_HOST = os.environ.get('GTASK_TARGET_WORKER_HOST', 'https://62bf2114.ngrok.io')
# Can be overridden also, this makes support for django-tenant-schemas by passing host='http://exmpla.com' in the task
# function, you can also use ngrok on your machine to debug
GTASK_SEND_TO_REMOTE = os.environ.get('GTASK_SEND_TO_REMOTE', True)
# To remove: Default is true within code
GTASK_MODEL_CLASS = 'gcloudtasks.Task'

GTASK_HANDLER_NAMESPACE = ''
# This is not required, as long as the URLS  included were not included under a namespace

"""
You can receive signal when a task was created by:
from gcloudtasks.tasks import task_created_signal

@receiver(task_created_signal)
def some_function(sender, instance, created, **kwargs):
    pass
"""

"""
On the worker Instance, you can use the same instance doesnt matter, anyways, I'm refering to the machine that runs in
GTASK_TARGET_WORKER_HOST
Include URLS

from gcloudtasks import urls as gcloud_urls


urlpatterns += [path('__tasks/', include(gcloud_urls))]

If you add a namespace to this, make sure to declare it in GTASK_HANDLER_NAMESPACE

"""

"""
Create tasks by decorating them with

from gcloudtasks.executor import task

# specify the queue name which this task is supposed to run on (required)
# specify a name for the task (optional)

@task(queue='default', name='someuniqueidforthetask')
def sum(a + b):
    print(a + b)

"""
