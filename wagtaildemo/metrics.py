import os

import mod_wsgi
import datadog

from datadog import statsd

def event_handler(name, **kwargs):
    if name == 'request_finished':
        statsd.increment('mod_wsgi.request.count')
        statsd.histogram('mod_wsgi.request.application_time', kwargs.get('application_time'))
        statsd.gauge('mod_wsgi.request.cpu_user_time', kwargs.get('cpu_user_time'))
        statsd.gauge('mod_wsgi.request.cpu_system_time', kwargs.get('cpu_system_time'))

def initialize():
    if event_handler not in mod_wsgi.event_callbacks:
        api_key = os.environ.get('DATADOG_API_KEY')

        datadog.initialize(api_key=api_key)
        mod_wsgi.subscribe_events(event_handler)
