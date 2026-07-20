#!/bin/sh
set -e
echo "Migration is running ..."
python manage.py migrate
exec $@
