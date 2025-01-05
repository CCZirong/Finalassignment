import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Money.settings')

app = Celery('Money')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-hong-kong-stocks-cache-every-15-minutes': {
        'task': 'Crawler.tasks.update_cache',
        'schedule': crontab(minute=f'*/{settings.INTERVAL_MINUTES}'),
        'args': ('hong_kong_stocks',),
    },
    'update-us-shares-stocks-cache-every-15-minutes': {
        'task': 'Crawler.tasks.update_cache',
        'schedule': crontab(minute=f'*/{settings.INTERVAL_MINUTES}'),
        'args': ('US_shares_stocks',),
    },
    'update-britain-stocks-cache-every-15-minutes': {
        'task': 'Crawler.tasks.update_cache',
        'schedule': crontab(minute=f'*/{settings.INTERVAL_MINUTES}'),
        'args': ('Britain_stocks',),
    },
}
