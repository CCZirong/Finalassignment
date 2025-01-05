import sys
from django.apps import AppConfig


class CrawlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Crawler'

    def ready(self):
        if 'runserver' in sys.argv:
            from .scheduler import StockScheduler
            StockScheduler().start()
