# Deploying to an OpenShift Cluster

To deploy the application to OpenShift, the built-in support for Source to Image (S2I) is used. It is only a matter of telling OpenShift the correct S2I builder to use in conjunction with the source code repository for the application.

## Creating the Application

To create the application in OpenShift, the ``oc new-app`` command is used. The two inputs required are the name of the S2I builder and the URL for the source code repository for the application. In this case, we have created the application in an existing project called ``snakes``.

```
$ oc new-app grahamdumpleton/warp0-centos7-python27~https://github.com/GrahamDumpleton/openshift3-wagtail.git --name wagtail
--> Found Docker image 5fb96c2 (24 hours old) from Docker Hub for "grahamdumpleton/warp0-centos7-python27"

    Python 2.7 (Warp Drive - CentOS 7)
    ----------------------------------
    S2I builder for Python web applications (CentOS 7).

    Tags: builder, python, python27, warpdrive, warpdrive-python27

    * An image stream will be created as "warp0-centos7-python27:latest" that will track the source image
    * A source build using source code from https://github.com/GrahamDumpleton/openshift3-wagtail.git will be created
      * The resulting image will be pushed to image stream "wagtail:latest"
      * Every time "warp0-centos7-python27:latest" changes a new build will be triggered
    * This image will be deployed in deployment config "wagtail"
    * Port 8080/tcp will be load balanced by service "wagtail"
      * Other containers can access this service through the hostname "wagtail"

--> Creating resources with label app=wagtail ...
    imagestream "warp0-centos7-python27" created
    imagestream "wagtail" created
    buildconfig "wagtail" created
    deploymentconfig "wagtail" created
    service "wagtail" created
--> Success
    Build scheduled, use 'oc logs -f bc/wagtail' to track its progress.
    Run 'oc status' to view your app.
```

The S2I builder used here is a derived version of the default Python 2.7 S2I builder for OpenShift based on CentOS 7. The changes from the default builder are the inclusion of the ``warpdrive`` scripts in place of the default S2I builder scripts.

To expose the application so that it can be accessed, ``oc expose`` needs to be run.

```
$ oc expose service/wagtail
route "wagtail" exposed
```

The hostname created for the application can then be found using ``oc describe`` on the route.

```
$ oc describe route/wagtail
Name:			wagtail
Created:		16 seconds ago
Labels:			app=wagtail
Annotations:		openshift.io/host.generated=true
Requested Host:		wagtail-snakes.apps.10.2.2.2.xip.io
			  exposed on router router 16 seconds ago
Path:			<none>
TLS Termination:	<none>
Insecure Policy:	<none>
Service:		wagtail
Endpoint Port:		8080-tcp
Endpoints:		172.17.0.4:8080
```

In particular, the ``Request Host`` field shows the URL for the application as ``wagtail-snakes.apps.10.2.2.2.xip.io``.

As with other deployments, in this default deployment scenario, development settings will be used, resulting in a SQLite database being used which only survives as long as the container running the application. That SQLite database will also not have been initialised.

To initialise the application data and the database, you should identify the name of the pod running the application and run ``warpdrive setup`` against it using the ``oc rsh`` command.

```
$ oc get pods --selector app=wagtail
NAME              READY     STATUS    RESTARTS   AGE
wagtail-1-3mfo5   1/1       Running   0          4m

$ oc rsh wagtail-1-3mfo5 warpdrive setup
 -----> Running .warpdrive/action_hooks/setup
+ set -eo pipefail
+ '[' '!' -f /opt/app-root/data/markers/setup ']'
+ mkdir -p /opt/app-root/data/django/media
+ python manage.py shell
+ cat -
Python 2.7.8 (default, Oct  1 2015, 16:23:56)
[GCC 4.8.3 20140911 (Red Hat 4.8.3-9)] on linux2
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
Username (leave blank to use 'default'): graham
Email address: graham@example.com
Password:
Password (again):
Superuser created successfully.
+ mkdir -p /opt/app-root/data/markers
+ date
+ chmod -w /opt/app-root/data/markers/setup
```

This would need to be re-run every time the application is restarted or re-deployed. For production usage we need to update the update the configuration to enable production environment settings, add persistent volumes and introduce a database.

## Creating a Database

For the database, we can use the PostgreSQL instant application provided with OpenShift.

```
$ oc describe templates/postgresql-persistent -n openshift
Name:		postgresql-persistent
Created:	6 weeks ago
Labels:		<none>
Description:	PostgreSQL database service, with persistent storage.  Scaling to more than one replica is not supported.  You must have persistent volumes available in your cluster to use this template.
Annotations:	iconClass=icon-postgresql
		tags=database,postgresql

Parameters:
    Name:		MEMORY_LIMIT
    Display Name:	Memory Limit
    Description:	Maximum amount of memory the container can use.
    Required:		false
    Value:		512Mi
    Name:		NAMESPACE
    Display Name:	Namespace
    Description:	The OpenShift Namespace where the ImageStream resides.
    Required:		false
    Value:		openshift
    Name:		DATABASE_SERVICE_NAME
    Display Name:	Database Service Name
    Description:	The name of the OpenShift Service exposed for the database.
    Required:		true
    Value:		postgresql
    Name:		POSTGRESQL_USER
    Display Name:	PostgreSQL User
    Description:	Username for PostgreSQL user that will be used for accessing the database.
    Required:		true
    Generated:		expression
    From:		user[A-Z0-9]{3}

    Name:		POSTGRESQL_PASSWORD
    Display Name:	PostgreSQL Password
    Description:	Password for the PostgreSQL user.
    Required:		true
    Generated:		expression
    From:		[a-zA-Z0-9]{16}

    Name:		POSTGRESQL_DATABASE
    Display Name:	PostgreSQL Database Name
    Description:	Name of the PostgreSQL database accessed.
    Required:		true
    Value:		sampledb
    Name:		VOLUME_CAPACITY
    Display Name:	Volume Capacity
    Description:	Volume space available for data, e.g. 512Mi, 2Gi.
    Required:		true
    Value:		1Gi

Object Labels:	template=postgresql-persistent-template

Objects:
    Service	${DATABASE_SERVICE_NAME}
```

To create the database we we once again use the ``oc new-app`` command.

```
$ oc new-app postgresql-persistent --param POSTGRESQL_DATABASE=wagtaildb --param POSTGRESQL_USER=wagtail --param DATABASE_SERVICE_NAME=wagtaildb
--> Deploying template "postgresql-persistent" in project "openshift" for "postgresql-persistent"
     With parameters:
      Memory Limit=512Mi
      Namespace=openshift
      Database Service Name=wagtaildb
      PostgreSQL User=wagtail
      PostgreSQL Password=iASoSr16cbvJClvR # generated
      PostgreSQL Database Name=wagtaildb
      Volume Capacity=1Gi
--> Creating resources ...
    service "wagtaildb" created
    persistentvolumeclaim "wagtaildb" created
    deploymentconfig "wagtaildb" created
--> Success
    Run 'oc status' to view your app.
```

Note that a password was automatically generated for the user which was created because we did not specify one. We will use that later when linking the application with the database.

## Adding Application Storage

The application being used needs persistent storage itself for saving uploaded media files. We will add this as the next step, using the ``oc set volume`` command.

```
$ oc volume dc/wagtail --add --claim-size 512M --claim-name wagtail --mount-path /opt/app-root/data --name media
persistentvolumeclaims/wagtail
deploymentconfigs/wagtail
```

We now have two persistent volumes being used, one for the database and one for the application itself.

```
$ oc get pvc
NAME        STATUS    VOLUME    CAPACITY   ACCESSMODES   AGE
wagtail     Bound     pv02      1Gi        RWO,RWX       16s
wagtaildb   Bound     pv01      1Gi        RWO,RWX       7m
```

Adding the volume to the deployment configuration for the application will result in the application being automatically redeployed with the newly mounted volume.

If we were once against to run ``warpdrive setup`` within the container to initialise the database, with a persistent volume now being used to handle the SQLite database, restarting the application would not result in the loss of the data. Don't do that though as we do not want to use SQLite, but use our separate PostgreSQL database.

## Enabling Production Settings

The next step is to now enable the production settings for the application and configure the application to use the PostgreSQL database. To do this we need to set a number of environment variables. These environment variables are:

* DJANGO_SETTINGS_MODULE=wagtaildemo.settings.production
* DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789
* DATABASE_URL=postgres://wagtail:iASoSr16cbvJClvR@wagtaildb:5432/wagtaildb

The ``DJANGO_SETTINGS_MODULE`` environment variable must be set to ``wagtail.settings.production``. The ``DJANGO_SECRET_KEY`` should be set to a random string of characters of suitable size. The ``DATABASE_URL`` should be set to the location of the database, along with the login credentials and database name.

To set these environment variables for the application we are going to use the ``oc set env`` command.

```
$ oc set env dc/wagtail --env DJANGO_SETTINGS_MODULE=wagtaildemo.settings.production --env DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789 --env DATABASE_URL=postgres://wagtail:iASoSr16cbvJClvR@wagtaildb:5432/wagtaildb

$ oc set env dc/wagtail --list
# deploymentconfigs wagtail, container wagtail
DJANGO_SETTINGS_MODULE=wagtaildemo.settings.production
DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789
DATABASE_URL=postgres://wagtail:iASoSr16cbvJClvR@wagtaildb:5432/wagtaildb
```

Setting the environment variables will result in our application being re-deployed with the new configuration.

We now need to initialise the application data and database once more.

```
$ oc get pods --selector app=wagtail
NAME              READY     STATUS    RESTARTS   AGE
wagtail-5-rxb1i   1/1       Running   0          3m

$ oc rsh wagtail-5-rxb1i warpdrive setup
 -----> Running .warpdrive/action_hooks/setup
+ set -eo pipefail
+ '[' '!' -f /opt/app-root/data/markers/setup ']'
+ mkdir -p /opt/app-root/data/django/media
+ cat -
+ python manage.py shell
Python 2.7.8 (default, Oct  1 2015, 16:23:56)
[GCC 4.8.3 20140911 (Red Hat 4.8.3-9)] on linux2
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
Username (leave blank to use 'default'): graham
Email address: graham@example.com
Password:
Password (again):
Superuser created successfully.
+ mkdir -p /opt/app-root/data/markers
+ date
+ chmod -w /opt/app-root/data/markers/setup
```

To ensure the application is starting up properly now that we have initialised the application data area and separate database, we are going to trigger a new deployment. This will cause the application to be restarted.

```
$ oc deploy dc/wagtail --latest
Started deployment #6
```

If we now browse to the URL for the application, we should see it displaying the default home page correctly. We can visit the admin interface, log in using the super user we created when running ``warpdrive setup`` and add new pages or upload media files.

## Customising the Application

At this point you would need to star customising the Wagtail page model objects. For details on how to do that see the Wagtail documentation at:

* http://docs.wagtail.io/en/latest/getting_started/tutorial.html#extend-the-homepage-model

Each time you have made code changes, update database migrations and commit all changes back to the source code repository. After having pushed changes up to GitHub, you can manually trigger a new build and deployment by running ``oc start-build wagtail``.

## Instant Deployment Using Templates

The above outlines the manual steps required to deploy the application to OpenShift. This process can be made easier using templates. To try out initial deployment using templates, start out by running:

```
oc create -f templates/wagtail-cms-multi-postgresql.json
oc create -f templates/wagtail-cms-single-postgresql.json
oc create -f templates/wagtail-cms-single-sqlite.json
```

This will create the templates:

```
wagtail-cms-multi-postgresql      Wagtail CMS (Multiple Pods / PostgreSQL)     11 (4 generated)   9
wagtail-cms-single-postgresql     Wagtail CMS (Single Pod / PostgreSQL)        10 (4 generated)   6
wagtail-cms-single-sqlite         Wagtail CMS (Single Pod / SQLite)            7 (2 generated)    6

```

You can select these templates from the OpenShift web console when adding an application to a project, or you can use ``oc new-app`` using the template as argument. Defaults will be used for any parameters such as passwords and secret keys. The values of the password will be displayed in the output of ``oc new-app``, or you can query them in the web console by looking at the deployment configuration details for the application.

```
$ oc new-app wagtail-cms-single-postgresql
--> Deploying template wagtail-cms-single-postgresql for "wagtail-cms-single-postgresql"
     With parameters:
      Application instance name=wagtail
      Application memory limit=384Mi
      Application volume capacity=512Mi
      Application admin user=admin # generated
      Application admin user password=TWYhHMUiv08Q3Mto # generated
      Application admin email=admin@example.com # generated
      Django secret key=INLbjtS2iRpsw1TNdbJvQXVSTdanKWP4cgLQ7a3rAcDVXmXObE6RSDbrhlYbVJsh # generated
      PostgreSQL database user=userVP5 # generated
      PostgreSQL user password=BwrbTfUFaoSGHK7A # generated
      PostgreSQL memory limit=384Mi
--> Creating resources with label app=wagtail ...
    imagestream "wagtail" created
    buildconfig "wagtail" created
    deploymentconfig "wagtail" created
    persistentvolumeclaim "wagtail-pvc" created
    service "wagtail" created
    route "wagtail" created
--> Success
    Build scheduled, use 'oc logs -f bc/wagtail' to track its progress.
    Run 'oc status' to view your app.
```

