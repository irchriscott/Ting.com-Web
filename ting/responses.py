from __future__ import unicode_literals
from django.http import HttpResponse
import json

class ResponseObject(object):

    def __init__(self, type, message, status, redirect=None, msgs=[], *args):
        if isinstance(status, int) is False : 
            raise TypeError('{0} must be an integer'.format(status))
        
        self.type = type
        self.message = message
        self.status = status
        self.redirect = redirect
        self.msgs = msgs

    def __str__(self):
        return self.message

    def __unicode__(self):
        return {
            'type': self.type,
            'message': self.message,
            'status': self.status,
            'redirect': self.redirect,
            'msgs': self.msgs
        }
    
    @property
    def get_object_dict(self):
        return self.__unicode__()

class HttpJsonResponse(HttpResponse):

    def __init__(self, content, *args, **kwargs):
        super(HttpResponse, self).__init__(
            content_type='application/json', *args, **kwargs)
        
        self.content = json.dumps(
            content.get_object_dict, indent=4, default=str, sort_keys=True) if isinstance(
            content, list) is not True else json.dumps(
            content, indent=4, default=str, sort_keys=True)
        self.content_type = 'application/json'
        self.data = content
    
    @property
    def status(self):
        return self.data.status if isinstance(
            self.data, object) is True and hasattr(self.data, 'status') else 200
