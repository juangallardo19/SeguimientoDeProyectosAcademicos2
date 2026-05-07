#!/bin/bash
python3 -m venv /tmp/venv
/tmp/venv/bin/pip install -r requirements.txt
/tmp/venv/bin/python manage.py collectstatic --noinput --clear
/tmp/venv/bin/python manage.py migrate --noinput
/tmp/venv/bin/python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='juang').exists():
    User.objects.create_superuser('juang', 'juang@admin.com', '12345678')
    print('Superuser juang creado.')
else:
    print('Superuser juang ya existe.')
"
