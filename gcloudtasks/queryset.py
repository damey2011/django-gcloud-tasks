import logging

from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class TaskQuerySet(QuerySet):
    def delete(self):
        for task in self:
            logger.info('Deleting task ' + task.task_id)
            task.delete()
