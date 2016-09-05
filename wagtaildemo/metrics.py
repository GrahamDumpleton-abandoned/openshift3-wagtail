import os

import mod_wsgi
import datadog

from datadog import statsd

def event_handler(name, **kwargs):
    if name == 'request_finished':
        statsd.increment('mod_wsgi.request.count')

        application_time = kwargs.get('application_time')

        statsd.histogram('mod_wsgi.request.application_time', application_time)

        statsd.gauge('mod_wsgi.request.input_reads', kwargs.get('input_reads'))
        statsd.gauge('mod_wsgi.request.input_length', kwargs.get('input_length'))
        statsd.gauge('mod_wsgi.request.input_time', kwargs.get('input_time'))

        statsd.gauge('mod_wsgi.request.output_writes', kwargs.get('output_writes'))
        statsd.gauge('mod_wsgi.request.output_length', kwargs.get('output_length'))
        statsd.gauge('mod_wsgi.request.output_time', kwargs.get('output_time'))

        cpu_user_time = kwargs.get('cpu_user_time')
        cpu_system_time = kwargs.get('cpu_system_time')

        statsd.gauge('mod_wsgi.request.cpu_user_time', cpu_user_time)
        statsd.gauge('mod_wsgi.request.cpu_system_time', cpu_system_time)

        if cpu_user_time is not None and application_time:
            cpu_burn = (cpu_user_time + cpu_system_time) / application_time
            statsd.gauge('mod_wsgi.request.cpu_burn', cpu_burn)

def initialize():
    if event_handler not in mod_wsgi.event_callbacks:
        mod_wsgi.subscribe_events(event_handler)
