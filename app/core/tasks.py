from celery import shared_task

@shared_task
def upload_file(file):
    return True;