#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 1
    done

    echo "PostgresSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata masterdata.json

exec "$@"