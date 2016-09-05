import time
import threading

import mod_wsgi
import datadog

from datadog import statsd

last_metrics = None

def monitor(*args):
    global last_metrics

    while True:
        current_metrics = mod_wsgi.process_metrics()

        if last_metrics is not None:
            cpu_user_time = (current_metrics['cpu_user_time'] -
                    last_metrics['cpu_user_time'])
            cpu_system_time = (current_metrics['cpu_system_time'] -
                    last_metrics['cpu_system_time'])

            request_busy_time = (current_metrics['request_busy_time'] -
                    last_metrics['request_busy_time'])

            request_threads = current_metrics['request_threads']

            timestamp = int(current_metrics['current_time'] * 1000000000)

            statsd.gauge('mod_wsgi.process.cpu_user_time', cpu_user_time)
            statsd.gauge('mod_wsgi.process.cpu_system_time', cpu_system_time)

            statsd.gauge('mod_wsgi.process.cpu_usage', ((cpu_user_time +
                    cpu_system_time) / (current_metrics['current_time'] -
                    last_metrics['current_time'])))

            statsd.gauge('mod_wsgi.process.request_busy_time', request_busy_time)
            statsd.gauge('mod_wsgi.process.request_busy_usage',
                    (request_busy_time / mod_wsgi.threads_per_process))

            statsd.gauge('mod_wsgi.process.threads_per_process',
                    mod_wsgi.threads_per_process)
            statsd.gauge('mod_wsgi.process.request_threads', request_threads)

        last_metrics = current_metrics

        current_time = current_metrics['current_time']
        delay = max(0, (current_time + 1.0) - time.time())
        time.sleep(delay)

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

thread = None

def initialize():
    global thread

    if event_handler not in mod_wsgi.event_callbacks:
        mod_wsgi.subscribe_events(event_handler)

       thread = threading.Thread(target=monitor)
       thread.setDaemon(True)
       thread.start()
