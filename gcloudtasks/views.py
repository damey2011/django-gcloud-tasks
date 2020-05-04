import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class TasksHandlerView(View):
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body.decode('utf-8'))
        function_path = body.get('call', None)
        function = import_string(function_path)
        if function:
            function(queue_task=False, **body.get('payload', {}))
        return HttpResponse('Done', status=200)
