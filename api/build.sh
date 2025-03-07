#!/usr/bin/env bash
# exit on error
set -o errexit

pip3 install -r requirements.txt

python3 manage.py collectstatic --no-input
python manage.py makemigrations challenges
python3 manage.py migrate
# python manage.py loaddata data.json
# cd /opt/render/project/src/api
# python manage.py migrate
