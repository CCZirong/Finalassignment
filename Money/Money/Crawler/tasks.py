import asyncio
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from .views import ResultData


@shared_task
def update_cache(table_name):
    result_data = ResultData()
    results = asyncio.run(result_data.get_east_from_db(table_name))

    cache_key = f"stock_data_{table_name}"
    cache.set(cache_key, results, timeout=settings.INTERVAL_MINUTES * 60)
