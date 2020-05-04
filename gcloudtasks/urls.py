from django.urls import path

from gcloudtasks import views

urlpatterns = [
    path('oya-hit-me/', views.TasksHandlerView.as_view(), name='gtask-handler')
]