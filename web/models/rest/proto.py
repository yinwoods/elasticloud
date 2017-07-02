# coding:utf-8
import json
from django.http import HttpResponse


class JsonResponse:
    def __init__(self, success=True, message=None, data=None):
        self.data = {}
        self.data['success'] = success
        self.data['message'] = message
        self.data['data'] = data

    def toJSON(self):
        return HttpResponse(json.dumps(self.data, ensure_ascii=False),
                            content_type="application/json")
