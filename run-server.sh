#!/bin/bash
# Start Flask app
gnome-terminal -- bash -c "python webserver.py; exec bash" &
# Start Celery worker
gnome-terminal -- bash -c "celery -A celery_worker.celery worker --loglevel=info; exec bash" &
# Start Celery beat
gnome-terminal -- bash -c "celery -A celery_worker.celery beat --loglevel=info; exec bash" &