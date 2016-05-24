# Deploying to a Docker Service

To create a Docker image for the application, the Source to Image (S2I) system is used. You first therefore need to have installed the ``s2i`` program and have it installed in your ``PATH``. S2I binaries can be downloaded from the releases page of the S2I project at:

* https://github.com/openshift/source-to-image

## Building the Docker Image

To build the Docker image use the ``warpdrive image`` command.

```
(warpdrive+wagtail) grumpy-old-man:openshift3-wagtail graham$ warpdrive image wagtail
I0523 21:50:30.529721 52649 install.go:251] Using "assemble" installed from "image:///usr/local/s2i/bin/assemble"
I0523 21:50:30.529863 52649 install.go:251] Using "run" installed from "image:///usr/local/s2i/bin/run"
I0523 21:50:30.529887 52649 install.go:251] Using "save-artifacts" installed from "image:///usr/local/s2i/bin/save-artifacts"
---> Installing application source
---> Building application from source
-----> Installing dependencies with pip (requirements.txt)
Collecting Django<1.10,>=1.9 (from -r requirements.txt (line 1))
Downloading Django-1.9.6-py2.py3-none-any.whl (6.6MB)
Collecting wagtail<1.5,>=1.4.5 (from -r requirements.txt (line 2))
Downloading wagtail-1.4.5-py2.py3-none-any.whl (6.6MB)
...
-----> Collecting static files for Django
Copying '/opt/app-root/src/wagtaildemo/static/js/wagtaildemo.js'
...

182 static files copied to '/opt/app-root/src/static'.
---> Fix permissions on application source
```

This will create a Docker image with name of ``wagtail``.

```
wagtail                                  latest              3144d5bc2679        2 minutes ago       876.4 MB
```

## Running the Docker Image

Once the Docker image has been created, it can be run. The default ``CMD`` specified by the image is sufficient, so no additional command need be provided. The HTTP listener port which needs to be exposed is port 8080.

```
(warpdrive+wagtail) $ docker run --rm -p 8080:8080 --name wagtail wagtail
---> Executing the start up script
 -----> Configuring for deployment type of 'auto'
 -----> Default WSGI server type is 'mod_wsgi'
 -----> Running server script start-mod_wsgi
 -----> Executing server command 'mod_wsgi-express start-server --log-to-terminal --startup-log --port 8080 --url-alias /media/ /opt/app-root/data/django/media/ --trust-proxy-header X-Forwarded-For --trust-proxy-header X-Forwarded-Port --trust-proxy-header X-Forwarded-Proto  --application-type module --entry-point wagtaildemo.wsgi --callable-object application --url-alias /static/ /opt/app-root/tmp/django/static/'
[Mon May 23 12:21:24.895591 2016] [mpm_event:notice] [pid 29:tid 140655642904320] AH00489: Apache/2.4.18 (Unix) mod_wsgi/4.5.0 Python/2.7.11 configured -- resuming normal operations
[Mon May 23 12:21:24.895771 2016] [core:notice] [pid 29:tid 140655642904320] AH00094: Command line: 'httpd (mod_wsgi-express)   -f /tmp/mod_wsgi-localhost:8080:1001/httpd.conf -E /dev/stderr -D MOD_WSGI_WITH_PROXY_HEADERS -D MOD_WSGI_MPM_ENABLE_EVENT_MODULE -D MOD_WSGI_MPM_EXISTS_EVENT_MODULE -D MOD_WSGI_MPM_EXISTS_WORKER_MODULE -D MOD_WSGI_MPM_EXISTS_PREFORK_MODULE -D FOREGROUND'
```

This can then be accessed at:

```
http://$(docker-machine ip default):8080
```

Note that by default this will run with Django settings for development and a local SQLite database within the container will be used. This database would need to be initialised for the application to work.

Relying on the fact that the container was named as ``wagtail`` when ``docker run`` was run, the database can be initialised using:

```
$ docker exec -it wagtail warpdrive setup
 -----> Running .warpdrive/action_hooks/setup
+ set -eo pipefail
+ '[' '!' -f /opt/app-root/data/markers/setup ']'
+ python manage.py shell
+ cat -
Python 2.7.11 (default, May 23 2016, 12:13:08)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> >>> Check whether database is ready...

>>> + echo ' -----> Running Django database migration'
 -----> Running Django database migration
+ python manage.py migrate
Operations to perform:
  Apply all migrations: wagtailimages, taggit, admin, wagtaildocs, home, wagtailforms, wagtailsearch, wagtailusers, auth, wagtailcore, wagtailembeds, contenttypes, wagtailredirects, sessions, wagtailadmin
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
...
+ '[' x '!=' x ']'
+ tty
+ echo ' -----> Running Django super user creation'
 -----> Running Django super user creation
+ python manage.py createsuperuser
Username (leave blank to use 'default'): graham
Email address: graham@example.com
Password:
Password (again):
Superuser created successfully.
+ mkdir -p /opt/app-root/data/markers
+ date
+ chmod -w /opt/app-root/data/markers/setup
```

The database and any uploaded media files will only exist for the life of the container and will be lost when the application is shutdown.

To have the database and any media files survive beyond the life of the container and able to be reused on subsequent invocations of the application as a new container, an external volume can be mounted on the directory ``/opt/app-root/data``.

```
$ docker run --rm -p 8080:8080 -v `pwd`/data:/opt/app-root/data --name wagtail wagtail
```

## Using production settings

By default the application will be run with development settings. This means a SQLite database is used, along with a fixed Django secret and Django debug enabled. These settings should not be used in production.

To enable production mode you need to set the following three environment variables when running the image.

* DJANGO_SETTINGS_MODULE=wagtaildemo.settings.production
* DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789
* DATABASE_URL=postgres://wagtail:secret@postgres:5432/wagtail

The ``DJANGO_SETTINGS_MODULE`` environment variable must be set to ``wagtail.settings.production``. The ``DJANGO_SECRET_KEY`` should be set to a random string of characters of suitable size. The ``DATABASE_URL`` should be set to the resolve location of the database you wish to use, along with the login credentials and database name.

To test the production configuration you can use the ``docker-compose.yml`` file:

```
version: '2'
services:
  web:
    image: wagtail
    ports:
     - "8080:8080"
    depends_on:
     - postgres
    environment:
     - DJANGO_SETTINGS_MODULE=wagtaildemo.settings.production
     - DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789
     - DATABASE_URL=postgres://wagtail:secret@postgres:5432/wagtail
    volumes:
     - /opt/app-root/data
  postgres:
    image: postgres
    environment:
     - POSTGRES_USER=wagtail
     - POSTGRES_PASSWORD=secret
```

You can startup the application and database by running:

```
docker-compose -f docker-compose.yml up
```

To initialise the application data and the separate database, you would then need to identify the running ``web`` container and then using ``docker exec``, run:

```
docker exec -it openshift3wagtail_web_1 warpdrive setup
```

You should adopt this recipe to your own requirements for production deployment. This should include using proper persistent volumes storage for application data and the separate database, rather than storage local to the Docker service. The mount point of the volume for application data in the ``web`` container should be ``/opt/app-root/data``. The mount point of the volume for the database data in the ``postgres`` container should be ``/var/lib/postgresql/data``.