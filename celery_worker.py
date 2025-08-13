from webserver import create_app  # This imports your initialized Flask app
from celery import Celery

def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker='redis://192.168.1.67:6379',  # Use your actual Redis config
        backend='redis://192.168.1.67:6379'
    )
    celery.conf.update(flask_app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(create_app())

@celery.task
def print_noon_message():
    print("It's noon! Task executed by Celery.")

from celery.schedules import crontab
celery.conf.beat_schedule = {
    'print-noon-task': {
        'task': 'celery_worker.print_noon_message',
        'schedule': crontab(minute='*/1'),
    },
}