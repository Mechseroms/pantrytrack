@echo off
REM Start Flask web server
start "Flask Server" cmd /k python webserver.py

REM Start Celery worker (use --pool=solo for Windows)
start "Celery Worker" cmd /k python -m celery -A celery_worker.celery worker --pool=solo --loglevel=info

REM Start Celery beat scheduler
start "Celery Beat" cmd /k python -m celery -A celery_worker.celery beat --loglevel=info