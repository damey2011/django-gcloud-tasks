import inspect
from functools import wraps

from django.conf import settings

from gcloudtasks.tasks import CloudTask


def task(queue=None, name=None):
    """Name has to be unique in some way, if you cannot come up with a unique name, leave as None"""
    if not queue:
        raise ValueError('Please provide queue name')

    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            if kwargs.pop('queue_task', True):
                import_path = inspect.getmodule(func).__loader__.name + '.' + func.__name__
                if not getattr(settings, 'GTASK_SEND_TO_REMOTE', True):
                    # execute the task immediately if we are not running remote
                    func(**kwargs)
                result = CloudTask(queue, name, import_path, kwargs)
                return result
            else:
                func(**kwargs)
            return func

        return wrapper

    return decorator
