import asyncio
import logging
import aiomysql
from django.conf import settings
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class DBHandler:
    def __init__(self):
        self.pool = None

    async def _create_pool(self):
        """创建数据库连接池"""
        db_config = settings.DATABASES['default']
        if self.pool:
            return
        try:
            self.pool = await aiomysql.create_pool(
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                db=db_config['NAME'],
                autocommit=True,
                loop=asyncio.get_event_loop()
            )
        except Exception as e:
            logging.error(e)
            raise e

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    @asynccontextmanager
    async def get_conn(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                yield cursor, conn

    async def execute(self, query, params):
        async with self.get_conn() as (cursor, _):
            try:
                await cursor.execute(query, params)
            except Exception as e:
                logging.error(e)
                raise e

    async def fetchall(self, query, params):
        async with self.get_conn() as (cursor, _):
            try:
                await cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row)) for row in await cursor.fetchall()
                ]
                return results
            except (RuntimeError, Exception) as e:
                logging.error(e)
                raise e

    async def fetchone(self, query, params):
        async with self.get_conn() as (cursor, _):
            try:
                await cursor.execute(query, params)
                return await cursor.fetchone()
            except Exception as e:
                logging.error(e)
                raise e

    async def execute_batch(self, queries):
        async with self.get_conn() as (cursor, conn):
            try:
                for query, params_list in queries:
                    await cursor.executemany(query, params_list)
                await conn.commit()
            except Exception as e:
                logging.error(e)
                await conn.rollback()
                raise e
