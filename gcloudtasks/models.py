from django.db import models

from gcloudtasks.queryset import TaskQuerySet
from gcloudtasks.tasks import delete_task


class Task(models.Model):
    """You can subclass this model, but make sure to declare the new class in the settings.py as GTASK_MODEL_CLASS"""
    task_id = models.CharField(max_length=500)
    is_local = models.BooleanField(default=False)
    delay = models.IntegerField(default=0)
    scheduled_time = models.DateTimeField(null=True, blank=True)

    objects = TaskQuerySet.as_manager()

    def __str__(self):
        return self.task_id

    def delete(self, using=None, keep_parents=False):
        if not self.is_local:
            delete_task(self.task_id)
        super(Task, self).delete(using, keep_parents)
