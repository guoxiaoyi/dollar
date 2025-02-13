import json
from data_fetcher.kline_fetcher import KlineFetcher
from datetime import datetime
import pandas as pd


class OhlcvHandler:
    """
    负责处理和分析 OHLCV 数据的类
    """

    def __init__(self, client, symbol):
        self.kline_fetcher = KlineFetcher(client, symbol)  # K 线数据获取器

    def generate(self, days, end_date):
        """
        生成 OHLCV 数据
        :param symbol: 交易对 (如 BTCUSDT)
        :param days: 获取多天的数据 (如 5)
        :param end_date: 结束日期 (如 2025-02-09)
        :return: OHLCV 数据
        """
        datas = self.kline_fetcher.data(days, end_date)


        md_tables = self.convert_to_markdown(datas)
        with open("data/ohlcv_data.md", "w", encoding="utf-8") as f:
            for period, table in md_tables.items():
                f.write(f"# {period} k线数据\n\n")
                f.write(table)
                f.write("\n\n")
        return datas

    def convert_to_markdown(self, data):
        markdown_tables = {}
      
        for time_period, rows in data.items():
            # 设置列名
            columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume"]
          
            # 创建 DataFrame
            df = pd.DataFrame(rows, columns=columns)
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True) \
                            .dt.tz_convert('Asia/Shanghai') \
                            .dt.strftime('%Y-%m-%d %H:%M:%S')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', utc=True) \
                            .dt.tz_convert('Asia/Shanghai') \
                            .dt.strftime('%Y-%m-%d %H:%M:%S')
          
            # 转换为 Markdown 格式
            markdown_table = df.to_markdown(index=False)
            markdown_tables[time_period] = markdown_table
      
        return markdown_tables
