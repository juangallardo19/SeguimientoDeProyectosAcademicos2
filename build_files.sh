#!/bin/bash
python3 -m venv /tmp/venv
/tmp/venv/bin/pip install -r requirements.txt
/tmp/venv/bin/python manage.py collectstatic --noinput --clear
/tmp/venv/bin/python manage.py migrate --noinput
