#!/usr/bin/env bash

# Init the DB.
python manage.py initdb

# Run Django migrations.
python manage.py migrate

# Start up the system with newrelic monitoring
newrelic-admin run-program gunicorn teach.wsgi
