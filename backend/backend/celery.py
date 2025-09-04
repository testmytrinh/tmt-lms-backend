import os

from celery import Celery

RMBQ_BROKER_URI = "{protocol}://{user}:{password}@{host}:{port}{vhost}".format(
    protocol=os.getenv("RBMQ_PROTOCOL"),
    user=os.getenv("RBMQ_USER"),
    password=os.getenv("RBMQ_PASSWORD"),
    host=os.getenv("RBMQ_HOST"),
    port=os.getenv("RBMQ_PORT"),
    vhost=os.getenv("RBMQ_VHOST", ""),
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
app = Celery(
    "django_celery",
    broker=RMBQ_BROKER_URI,
)

# Find all task in django apps
app.autodiscover_tasks()
