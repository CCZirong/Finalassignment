import asyncio
import aiohttp
from fake_useragent import UserAgent

from .models import DBHandler


class EastMoneyCrawler(DBHandler):
    def __init__(self):
        super().__init__()
        self.headers = {'User-Agent': UserAgent().random}

    async def fetch_data(self, session, url):
        async with session.get(url, headers=self.headers, ssl=False) as response:
            if response.status == 200:
                return await response.json()

    async def parse_data(self, data, keys, table_name):
        results = data['data']['diff']
        east_data = []
        for result in results:
            try:
                if all(key in result and result[key] != '-' for key in keys):
                    values = [result[key] for key in keys]
                    if table_name == "Britain_stocks":
                        values = await self.convert_to_decimal(values)
                        if values is None:
                            continue
                    east_data.append(tuple(values))
            except (ValueError, KeyError, Exception) as e:
                continue
        return east_data

    async def convert_to_decimal(self, values):
        values[1] = values[1] / 100
        values[2] = values[2] / 100
        if values[1] > 50 or values[2] > 50:
            return None
        return values

    async def run_crawler(self, url_template, pages, keys, table_name, key):
        await self._create_pool()
        await self.execute(f"TRUNCATE TABLE {table_name}", None)
        tasks = []
        async with aiohttp.ClientSession() as session:
            for page in range(1, pages):
                url = url_template.format(page=page)
                tasks.append(self.fetch_data(session, url))
            pages_data = await asyncio.gather(*tasks)

        all_east_data = []
        for data in pages_data:
            if data is not None:
                all_east_data.extend(await self.parse_data(data, keys, table_name))
        query = f"""
                INSERT INTO {table_name}({', '.join(key)})
                VALUES ({', '.join(['%s'] * len(key))});
                """
        print(all_east_data[:10])
        print(len(all_east_data))
        await self.execute_batch([(query, all_east_data)])
        await self.close()

    async def us_run_crawler(self):
        url_template = "https://47.push2.eastmoney.com/api/qt/clist/get?&pn={page}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&dect=1&wbp2u=|0|0|0|web&fid=f3&fs=m:105,m:106,m:107&"
        await self.run_crawler(url_template, 400, ['f14', 'f2', 'f18'], 'US_shares_stocks',
                               ['name', 'latest_price', 'previous_close'])

    async def hk_run_crawler(self):
        url_template = "https://50.push2.eastmoney.com/api/qt/clist/get?&pn={page}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&dect=1&wbp2u=|0|0|0|web&fid=f3&fs=m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152&_=1733933566415"
        await self.run_crawler(url_template, 200, ['f12', 'f14', 'f2', 'f18'], 'hong_kong_stocks',
                               ['code', 'name', 'latest_price', 'previous_close'])

    async def britain_run_crawler(self):
        url_template = "https://push2.eastmoney.com/api/qt/clist/get?&pn={page}&pz=20&po=1&fid=f3&np=1&ut=fa5fd1943c7b386f172d6893dbfba10b&fs=m:155+t:1,m:155+t:2,m:155+t:3,m:156+t:1,m:156+t:2,m:156+t:5,m:156+t:6,m:156+t:7,m:156+t:8&"
        await self.run_crawler(url_template, 200, ['f14', 'f2', 'f18'], 'Britain_stocks',
                               ['name', 'latest_price', 'previous_close'])

    async def run_all_crawlers(self):
        await self.us_run_crawler()
        await self.hk_run_crawler()
        await self.britain_run_crawler()
