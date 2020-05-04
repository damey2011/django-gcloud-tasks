from django.apps import AppConfig
from django.contrib import admin


class GcloudtasksConfig(AppConfig):
    name = 'gcloudtasks'

    def ready(self):
        from gcloudtasks.admin import TaskAdmin
        from gcloudtasks.utils import get_model_class
        Model = get_model_class()
        admin.site.register(Model, TaskAdmin)
