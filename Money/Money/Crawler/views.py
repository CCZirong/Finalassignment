import os
import csv
import urllib.parse
import logging
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render
from reportlab.pdfgen import canvas
from pyecharts import options as opts
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from pyecharts.charts import Line, Bar, Scatter
from django.http import JsonResponse, HttpResponse

from .models import DBHandler
from .scheduler import update_times
from .EastMoneyCrawler import EastMoneyCrawler as Crawler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class ResultData(DBHandler):
    def __init__(self):
        super().__init__()
        self.crawler = Crawler()

    async def get_stack_list(self, table_name="hong_kong_stocks"):
        cache_key = f"stock_data_{table_name}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        results = await self.get_east_from_db(table_name)
        cache.set(cache_key, results, timeout=settings.INTERVAL_MINUTES * 60)
        return results

    async def get_east_from_db(self, table_name="hong_kong_stocks"):
        await self._create_pool()
        query = f"""
        SELECT DISTINCT name, latest_price, previous_close FROM {table_name}
        """
        results = await self.fetchall(query, None)
        if not results:
            await self.crawler.run_all_crawlers()
            results = await self.fetchall(query, None)

        await self.close()
        return results


class ViewEast(ResultData):
    def __init__(self):
        super().__init__()

    async def index(self, request, *args, **kwargs):
        return render(request, "index.html")
    
    @staticmethod
    async def public_methods(results, *args, **kwargs):
        seen_names = set()
        unique_results = []

        for stock in results:
            if stock['name'] not in seen_names:
                seen_names.add(stock['name'])
                unique_results.append(stock)

        filtered_results = [stock for stock in unique_results if 1 <= stock['latest_price'] <= 5]

        if len(filtered_results) < 200:
            additional_results = [stock for stock in unique_results if stock not in filtered_results]
            filtered_results.extend(additional_results[:200 - len(filtered_results)])

        return [stock['name'] for stock in filtered_results[:200]], [stock['latest_price'] for stock in
                                                                     filtered_results[:200]], [stock['previous_close']
                                                                                               for stock in
                                                                                               filtered_results[:200]]

    async def line(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        results = await self.get_stack_list(table_name)
        stock_names, latest_prices, previous_prices = await self.public_methods(results)
        line = (
            Line()
            .add_xaxis(stock_names)
            .add_yaxis("最新价格", latest_prices, is_smooth=True, color='blue')
            .add_yaxis("昨收价格", previous_prices, is_smooth=True, color='red')
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票价格变化趋势"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        font_size=8
                    )
                ),
                yaxis_opts=opts.AxisOpts(name="价格"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
            )
        )
        chart_line = line.render_embed(devicePixelRatio=3)
        return render(request, 'line.html', {'chart_line': chart_line})

    async def bar(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        results = await self.get_stack_list(table_name)
        stock_names, latest_prices, previous_prices = await self.public_methods(results)

        bar = (
            Bar()
            .add_xaxis(stock_names)
            .add_yaxis("最新价格", latest_prices, color='blue')
            .add_yaxis("昨收价格", previous_prices, color='red')
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票价格对比"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        font_size=8
                    )
                ),
                yaxis_opts=opts.AxisOpts(name="价格"),
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
            )
        )
        chart_bar = bar.render_embed(devicePixelRatio=3)
        return render(request, 'bar.html', {'chart_bar': chart_bar})

    async def line_with_area(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        results = await self.get_stack_list(table_name)
        stock_names, latest_prices, previous_prices = await self.public_methods(results)

        line = (
            Line()
            .add_xaxis(stock_names)
            .add_yaxis(
                "最新价格",
                latest_prices,
                is_smooth=True,
                color='blue',
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5)
            )
            .add_yaxis(
                "昨收价格",
                previous_prices,
                is_smooth=True,
                color='red',
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票价格变化趋势（带面积填充）"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        font_size=8
                    )
                ),
                yaxis_opts=opts.AxisOpts(name="价格"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
            )
        )
        chart_line = line.render_embed(devicePixelRatio=3)
        return render(request, 'line_with_area.html', {'chart_line': chart_line})

    async def scatter(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        results = await self.get_stack_list(table_name)
        stock_names, latest_prices, previous_prices = await self.public_methods(results)

        scatter = (
            Scatter()
            .add_xaxis(stock_names)
            .add_yaxis("最新价格", latest_prices, symbol_size=10, color='blue')
            .add_yaxis("昨收价格", previous_prices, symbol_size=10, color='red')
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票价格散点图"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        font_size=8
                    )
                ),
                yaxis_opts=opts.AxisOpts(name="价格"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
            )
        )
        chart_scatter = scatter.render_embed(devicePixelRatio=3)
        return render(request, 'scatter.html', {'chart_scatter': chart_scatter})


class LatestTime:
    @staticmethod
    async def latest_update_time(request, *args, **kwargs):
        if update_times is not None:
            latest_time = update_times[-1]
        else:
            latest_time = "暂无更新"
        return JsonResponse({'latest_update_time': latest_time, 'time': settings.INTERVAL_MINUTES})


class ExportData(ResultData):
    def __init__(self):
        super().__init__()

    async def export_data_csv(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        stocks = await self.get_stack_list(table_name)

        stock_type = self.get_table_name(table_name)
        filename = f"{stock_type}_数据导出.csv"
        encoded_filename = urllib.parse.quote(filename)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'

        response.write('\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow(['股票名字', '最新价格', '昨收'])

        for stock in stocks:
            writer.writerow([stock['name'], stock['latest_price'], stock['previous_close']])

        return response

    async def export_data_pdf(self, request, *args, **kwargs):
        table_name = request.GET.get('table', 'hong_kong_stocks')
        stocks = await self.get_stack_list(table_name)

        stock_type = self.get_table_name(table_name)
        filename = f"{stock_type}_数据导出.pdf"
        encoded_filename = urllib.parse.quote(filename)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'

        p = canvas.Canvas(response, pagesize=letter)

        font_path = os.path.join(
            os.path.dirname(
                __file__
            ), 'ttf', 'SimHei.ttf'
        )
        pdfmetrics.registerFont(TTFont('SimHei', font_path))
        p.setFont('SimHei', 12)

        p.drawString(100, 750, f"{stock_type}_股票数据导出")

        y = 720
        for stock in stocks:
            p.drawString(100, y,
                         f"股票名字: {stock['name']}, 最新价格: {stock['latest_price']}, 昨收: {stock['previous_close']}")
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont('SimHei', 12)
                y = 750

        p.showPage()
        p.save()
        return response

    def get_table_name(self, table_name):
        table_type = {
            'hong_kong_stocks': '港股',
            'US_shares_stocks': '美股',
            'Britain_stocks': '英股'
        }
        return table_type.get(table_name, '未知')
