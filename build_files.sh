#!/usr/bin/env bash
python3 -m pip install requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
