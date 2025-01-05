import sys
import asyncio
import logging
from collections import deque
from django.utils import timezone
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from .EastMoneyCrawler import EastMoneyCrawler

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

update_times = deque([timezone.now()], maxlen=1)


class StockScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore(DjangoJobStore(), "default")

    def start(self):
        """
        启动定时任务
        """

        interval_minutes = getattr(settings, 'INTERVAL_MINUTES', 15)

        self.scheduler.add_job(
            crawl_us_stock_data,
            'interval',
            minutes=interval_minutes,
            name='crawl_us_stock_data',
            jobstore='default',
            id='crawl_us_stock_data',
            replace_existing=True
        )

        self.scheduler.add_job(
            crawl_hk_stock_data,
            'interval',
            minutes=interval_minutes,
            name='crawl_hk_stock_data',
            jobstore='default',
            id='crawl_hk_stock_data',
            replace_existing=True
        )

        self.scheduler.add_job(
            crawl_britain_stock_data,
            'interval',
            minutes=interval_minutes,
            name='crawl_britain_stock_data',
            jobstore='default',
            id='crawl_britain_stock_data',
            replace_existing=True
        )

        try:
            self.scheduler.start()
            logger.info("定时任务已启动")
        except Exception as e:
            logger.error(f"启动定时任务时出错: {e}")
            sys.exit(1)


def crawl_us_stock_data():
    run_crawler(EastMoneyCrawler().us_run_crawler)


def crawl_hk_stock_data():
    run_crawler(EastMoneyCrawler().hk_run_crawler)


def crawl_britain_stock_data():
    run_crawler(EastMoneyCrawler().britain_run_crawler)


def run_crawler(crawler_method):
    """
    运行指定的爬虫方法
    """
    try:
        asyncio.run(crawler_method())
        update_times.append(timezone.now())
        logger.info(f"{crawler_method.__name__} 爬虫运行成功")
    except Exception as e:
        logger.error(f"运行爬虫时出错: {e}")
