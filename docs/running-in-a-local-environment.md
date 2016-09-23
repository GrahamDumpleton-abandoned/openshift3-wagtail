# Running in a Local Environment

To run the application in a local environment for the purposes of development and testing you should use ``warpdrive`` to handle builds and deployments.


## Installing WarpDrive

To use ``warpdrive`` you should install it either in your global Python installation, or dedicate a Python virtual environment to it. The only package that needs to be installed in the virtual environment is ``warpdrive`` as it is used to merely bootstrap a new separate Python environment for each application it is used with.

If using ``virtualenvwrapper``, the steps to install ``warpdrive`` would be:

```
$ mkvirtualenv warpdrive
New python executable in /Users/graham/Python/warpdrive/bin/python
Installing setuptools, pip, wheel...done.
virtualenvwrapper.user_scripts creating /Users/graham/Python/warpdrive/bin/predeactivate
virtualenvwrapper.user_scripts creating /Users/graham/Python/warpdrive/bin/postdeactivate
virtualenvwrapper.user_scripts creating /Users/graham/Python/warpdrive/bin/preactivate
virtualenvwrapper.user_scripts creating /Users/graham/Python/warpdrive/bin/postactivate
virtualenvwrapper.user_scripts creating /Users/graham/Python/warpdrive/bin/get_env_details

(warpdrive) $ pip install warpdrive
Collecting warpdrive
  Downloading warpdrive-0.20.1.tar.gz
Building wheels for collected packages: warpdrive
  Running setup.py bdist_wheel for warpdrive ... done
  Stored in directory: /Users/graham/Library/Caches/pip/wheels/4e/38/4a/42baead57bdc72af5240220fcf9af3ccc127349c8ab45d57ba
Successfully built warpdrive
Installing collected packages: warpdrive
Successfully installed warpdrive-0.20.1
```

Next update your ``$HOME/.bash_profile`` script to add a helper function which will make it possible to use ``warpdrive``.


```
# Set up warpdrive.

WARPDRIVE=$HOME/Python/warpdrive/bin/warpdrive
export WARPDRIVE

source `$WARPDRIVE rcfile`
```

Create a new shell so the changes are picked up. There is no need to activate the ``warpdrive`` virtual environment.

## Preparing the Environment

To create a ``warpdrive`` environment for the project, from the top level directory of the project source code, use ``warpdrive`` to activate the environment. If the environment doesn't already exist, it will be created.

```
$ warpdrive project wagtail
(warpdrive+wagtail) $
```

This creates a separate Python virtual environment for the project, but no packages required by the project are yet installed. To install required packages and also perform any other build steps necessary to prepare the application for deployment, such as collect together static resources for Django, use the ``warpdrive build`` command.

```
(warpdrive+wagtail) $ warpdrive build
 -----> Installing dependencies with pip (requirements.txt)
Collecting Django<1.10,>=1.9 (from -r requirements.txt (line 1))
  Downloading Django-1.9.6-py2.py3-none-any.whl (6.6MB)
    100% |████████████████████████████████| 6.6MB 621kB/s
...
Collecting mod_wsgi
  Downloading mod_wsgi-4.5.2.tar.gz (1.8MB)
    100% |████████████████████████████████| 1.8MB 1.1MB/s
Installing collected packages: mod-wsgi
  Running setup.py install for mod-wsgi ... done
Successfully installed mod-wsgi-4.5.2
 -----> Collecting static files for Django
Copying '/Users/graham/Projects/openshift3-wagtail/wagtaildemo/static/css/wagtaildemo.css'
...

182 static files copied to '/Users/graham/.warpdrive/warpdrive+wagtail/tmp/django/static'.
```

This command should be re-run every time you make a change to the list of required packages in the ``requirements.txt`` file, or any static resources are modified or added.

## Initialising the Database

When running in a local environment, Django settings will be configured for a development environment. This will include using the SQLite database for persistent storage.

To initialise the database, run the ``warpdrive setup`` command. This will create the database and prompt for details of the initial super user account.

```
(warpdrive+wagtail) $ warpdrive setup
 -----> Running .warpdrive/action_hooks/setup
+ set -eo pipefail
+ '[' '!' -f /Users/graham/.warpdrive/warpdrive+wagtail/data/markers/setup ']'
+ cat -
+ python manage.py shell
Python 2.7.10 (default, Oct 23 2015, 19:19:21)
[GCC 4.2.1 Compatible Apple LLVM 7.0.0 (clang-700.0.59.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> >>> Check whether database is ready...

>>> + echo ' -----> Running Django database migration'
 -----> Running Django database migration
+ python manage.py migrate
Operations to perform:
  Apply all migrations: wagtailusers, wagtailembeds, wagtailadmin, sessions, admin, wagtailcore, auth, contenttypes, wagtaildocs, taggit, wagtailsearch, home, wagtailforms, wagtailredirects, wagtailimages
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
...
+ '[' x '!=' x ']'
+ tty
+ echo ' -----> Running Django super user creation'
 -----> Running Django super user creation
+ python manage.py createsuperuser
Username (leave blank to use 'graham'): graham
Email address: graham@example.com
Password:
Password (again):
Superuser created successfully.
+ mkdir -p /Users/graham/.warpdrive/warpdrive+wagtail/data/markers
+ date
+ chmod -w /Users/graham/.warpdrive/warpdrive+wagtail/data/markers/setup
```

## Running Database Migrations

If the database model types are ever changed or new database model objects are added and a database migration needs to be triggered, run the ``warpdrive migrate`` command.

```
(warpdrive+wagtail) $ warpdrive migrate
 -----> Running .warpdrive/action_hooks/migrate
+ set -eo pipefail
+ cat -
+ python manage.py shell
Python 2.7.10 (default, Oct 23 2015, 19:19:21)
[GCC 4.2.1 Compatible Apple LLVM 7.0.0 (clang-700.0.59.5)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> >>> Check whether database is ready...

>>> + echo ' -----> Running Django database migration'
 -----> Running Django database migration
+ python manage.py migrate
Operations to perform:
  Apply all migrations: wagtailusers, wagtailembeds, wagtailadmin, sessions, admin, wagtailcore, auth, contenttypes, wagtaildocs, taggit, wagtailsearch, home, wagtailforms, wagtailredirects, wagtailimages
Running migrations:
  No migrations to apply.
```

## Starting Up the Application

To start Wagtail CMS application, run the ``warpdrive start`` command.

```
(warpdrive+wagtail) $ warpdrive start
 -----> Configuring for deployment type of 'auto'
 -----> Default WSGI server type is 'mod_wsgi'
 -----> Running server script start-mod_wsgi
 -----> Executing server command 'mod_wsgi-express start-server --log-to-terminal --startup-log --port 8080 --url-alias /media/ /Users/graham/.warpdrive/warpdrive+wagtail/data/django/media/ --trust-proxy-header X-Forwarded-For --trust-proxy-header X-Forwarded-Port --trust-proxy-header X-Forwarded-Proto  --application-type module --entry-point wagtaildemo.wsgi --callable-object application --url-alias /static/ /Users/graham/.warpdrive/warpdrive+wagtail/tmp/django/static/'
Server URL         : http://localhost:8080/
Server Root        : /tmp/mod_wsgi-localhost:8080:502
Server Conf        : /tmp/mod_wsgi-localhost:8080:502/httpd.conf
Error Log File     : /dev/stderr (warn)
Startup Log File   : /dev/stderr
Request Capacity   : 5 (1 process * 5 threads)
Request Timeout    : 60 (seconds)
Queue Backlog      : 100 (connections)
Queue Timeout      : 45 (seconds)
Server Capacity    : 20 (event/worker), 20 (prefork)
Server Backlog     : 500 (connections)
Locale Setting     : en_AU.UTF-8
[Mon May 23 21:32:03.965791 2016] [mpm_prefork:notice] [pid 50008] AH00163: Apache/2.4.18 (Unix) mod_wsgi/4.5.2 Python/2.7.10 configured -- resuming normal operations
[Mon May 23 21:32:03.966041 2016] [core:notice] [pid 50008] AH00094: Command line: 'httpd (mod_wsgi-express)  -f /tmp/mod_wsgi-localhost:8080:502/httpd.conf -E /dev/stderr -D MOD_WSGI_WITH_PROXY_HEADERS -D FOREGROUND'
```

All log output will be directed to the console. To shutdown the application, use ``CTRL-C``.

The application can be accessed using the server URL displayed in the output from the ``warpdrive start`` command.

The login details for super user account created when ``warpdrive setup`` was run can be used to access of the admin interface of Wagtail CMS.