#!/bin/bash
python manage.py migrate      # Apply database migrations
if [ "$ENV" == "dev" ]        # Collect static files on in DEV
then
   python manage.py collectstatic --noinput
fi

sh /code/docker/sync_wca_database.sh

# Launch supervisor
/usr/local/bin/supervisord