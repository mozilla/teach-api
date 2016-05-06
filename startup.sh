#!/usr/bin/env bash

# Init the DB (noop if already extant):
python manage.py initdb

# Make Django migrations, just in case...
python manage.py makemigrations

# Then migrate up.
python manage.py migrate

# Finally, start up the system with newrelic monitoring.
newrelic-admin run-program gunicorn teach.wsgi
