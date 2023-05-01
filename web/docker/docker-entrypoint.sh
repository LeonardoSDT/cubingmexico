#!/bin/bash
python manage.py migrate      # Apply database migrations
if [ "$ENV" == "dev" ]        # Collect static files on in DEV
then
   python manage.py collectstatic --noinput
fi
# Launch supervisor
/usr/local/bin/supervisord