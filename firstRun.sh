#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/exhibit_types.json
python manage.py loaddata fixtures/user_groups.json
python manage.py createsuperuser
bower install