from django.conf import settings
from google.api_core.exceptions import NotFound

from gcloudtasks.utils import get_client

client = get_client()


def get_or_create_queue(name):
    name = client.queue_path(settings.GTASK_PROJECT_ID, settings.GTASK_PROJECT_LOCATION, name)
    try:
        response = client.get_queue(name=name, retry=None, timeout=30)
    except NotFound:
        parent = client.location_path(settings.GTASK_PROJECT_ID, settings.GTASK_PROJECT_LOCATION)
        queue = {'name': name}
        response = client.create_queue(parent, queue)
    return response


def get_queue(name):
    name = client.queue_path(settings.GTASK_PROJECT_ID, settings.GTASK_PROJECT_LOCATION, name)
    return client.get_queue(name=name, retry=None, timeout=30)
