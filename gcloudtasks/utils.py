import os

from django.apps import apps
from django.conf import settings
from django.urls import reverse
from google.api_core.retry import Retry
from google.cloud import tasks_v2
from google.oauth2 import service_account


def get_credentials():
    cred = getattr(settings, 'GTASK_CREDENTIAL_FILE', os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None))
    if not cred:
        raise ValueError('Please set GOOGLE_APPLICATION_CREDENTIALS environmental variable to path to your json '
                         'credential file or add path to settings.py variable GTASK_CREDENTIAL_FILE')
    return cred


def get_client():
    cred = service_account.Credentials.from_service_account_file(filename=get_credentials())
    client = tasks_v2.CloudTasksClient(credentials=cred)
    return client


def get_retry():
    retry_kwargs = {}
    if getattr(settings, 'GTASK_ON_ERROR', None):
        retry_kwargs.update({'on_error': settings.GTASK_ON_ERROR})
    if getattr(settings, 'GTASK_RETRY_DEADLINE', None):
        retry_kwargs.update({'deadline': settings.GTASK_RETRY_DEADLINE})
    retry = Retry(deadline=10, **retry_kwargs)
    return retry


def get_path(host=None):
    namespace = getattr(settings, 'GTASK_HANDLER_NAMESPACE', None)
    if namespace:
        path = reverse(f'{namespace}:gtask-handler')
    else:
        path = reverse('gtask-handler')
    if not host:
        return f'{settings.GTASK_TARGET_WORKER_HOST}{path}'
    return f'{host}{path}'


def get_model_class():
    return apps.get_model(getattr(settings, 'GTASK_MODEL_CLASS', 'gcloudtasks.Task'))
