=============================
django-gcloud-tasks
=============================


A simplified  package to integrate Google cloud tasks into your django application within 5 minutes.

Documentation
-------------

Quickstart
----------

Install django-gcloud-tasks::

    pip install gcloudtasks


Add it to your `INSTALLED_APPS`:

.. code-block::

    INSTALLED_APPS = (
        ...
        'gcloudtasks',
        ...
    )


On the instance that would be processing the tasks, add django-gcloud-tasks's URL patterns:

.. code-block::


    urlpatterns = [
        ...
        path('__tasks/', include('gcloudtasks.urls')),
        ...
    ]


You need to configure a few settings. Available settings include:

- :code:`GTASK_PROJECT_ID`: (required) This is your project ID which you obtain from your Google console.
- :code:`GTASK_PROJECT_LOCATION`: (required) Your project location, the default from Google console is usually us-central1, but I still advise you confirm yours.
- :code:`GTASK_CREDENTIAL_FILE`: Absolute file to your Google account credentials json file. This one is not required if GOOGLE_APPLICATION_CREDENTIALS is set to environmental variables.
- :code:`GTASK_TARGET_WORKER_HOST`: (required) Absolute URL of the worker instance that will process the task. (e.g. https://example.com)
- :code:`GTASK_SEND_TO_REMOTE`: Defaults to True, this says if the task should be forwarded to the Google tasks remote queue or not. You might want to change this to False in development environment.
- :code:`GTASK_MODEL_CLASS`: Defaults to 'gcloudtasks.Task'. You would want to change this if you intend to use a custom model for task management.
- :code:`GTASK_HANDLER_NAMESPACE`: Defaults to empty. Only required if you added a namespace to the URL pattern entry. Otherwise, not necessary.



Signals
-------

To use the signals, simply create a receiver like below:

.. code-block::

    from gcloudtasks.tasks import task_created_signal

    @receiver(task_created_signal)
    def some_function(sender, instance, created, **kwargs):
        pass


Extend the Task Model
---------------------

Create custom task model:

Assuming this model file is :code:`campaigns/models.py`

.. code-block::

    from gcloudtasks.models import Task

    class CustomTask(Task):
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        ...
        ...


Then in settings.py,
With respect to the file name, we do:

.. code-block::

    GTASK_MODEL_CLASS = 'campaigns.CustomTask'


Functions
---------

**Create Task**: To create a task, simple decorate the function with :code:`@task`.
This decorator takes in two parameters :code:`queue` and :code:`name`. Only the :code:`queue`
is compulsory. :code:`queue` is the name of the task queue which you want the task to run on.
The name is automatically generated if not provided.
If you do not have a queue already, there is a function that lets you check, and create if it
does not exist.

.. code-block::

    # To create get or create queue

    from gcloudtasks.queues import get_or_create_queue

    get_or_create_queue(queue_name)


To actually create task, you could create a specialized file and name it :code:`tasks.py` or whatever you want and add
your task functions there.

.. code-block::

    from gcloudtasks.executor import task


    @task(queue='my-default-queue')
    def sum_numbers(a, b):
        # do something in the function
        pass


You would then in your :code:`views.py` or anywhere for that matter, do something like this to execute this task

.. code-block::

    from .tasks import sum_numbers

    class SomeView(FormView):
        ....

        def form_valid(self, form):
            ...
            sum_numbers(a=10, b=20).run()

You would notice that the parameters were passed as keyword arguments. That is compulsory.
And should you want to schedule this task, :code:`run` takes two possible non-required arguments;
:code:`delay` and :code:`scheduled_time`. :code:`delay` should be a :code:`datetime.timedelta` instance
while the :code:`scheduled_time` is expected to be a timezone-aware :code:`datetime` instance.

To schedule the :code:`sum_numbers` function for after 2 days. I would do

.. code-block::

    sum_numbers(a=10, b=20).run(delay=timedelta(days=2))


Features
--------

* Tasks management through django admin. (when you delete tasks through the admin, they are deleted from the queue if they have not yet been processed).
* Extendable Task model.
* Task creation model signal.
* Extended support for libraries like :code:`django-tenant-schemas`.


Extended Support
----------------

Django tenant schemas was put into consideration when writing the library. It is understood that
you might want to route the task to a particular domain on the worker instance or whichever server is
handling the tasks, so it is possible to override :code:`GTASK_TARGET_WORKER_HOST` for every task execution by
simply passing :code:`host` parameter into the :code:`run` function like below.


.. code-block::

    sum_numbers(a=10, b=20).run(host='https://somedomain.example.com')



Gotchas
-------

* Pass only JSON serializable objects into the task functions. If you need a model in there, pass the :code:`id` and retrieve the model inside the function. e.g.

.. code-block::

    # Inside your tasks.py or wherever your task functions reside.
    @task(queue='my-default-queue')
    def mark_as_done(todo_id):
        todo = Todo.objects.get(pk=todo_id)
        ...


    # Where the task is being called
    mark_as_done(todo_id=todo.id).run()


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
