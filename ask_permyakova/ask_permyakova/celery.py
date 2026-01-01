import os

from celery import Celery
from ask_permyakova.settings import REDIS_AUTO_UPDATE_POPULAR_TAGS, REDIS_AUTO_UPDATE_BEST_MEMBERS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ask_permyakova.settings')

app = Celery('ask_permyakova')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-update-popular-tags': {
        'task': 'app.views.update_cache_popular_tags',
        'schedule': REDIS_AUTO_UPDATE_POPULAR_TAGS,
    },
    'auto-update-best-members': {
        'task': 'app.views.update_cache_best_members_by_answers',
        'schedule': REDIS_AUTO_UPDATE_BEST_MEMBERS,
    },
}
app.conf.timezone = 'UTC'

@app.task(ignore_result=True)
def debug_task():
    print(f'From celery task')