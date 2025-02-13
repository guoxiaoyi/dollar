from data_fetcher.ticker_24hr_fetcher import Ticker24hrFetcher
import os
from datetime import datetime, timezone, timedelta

class Ticker24hrHandler:
    """
    24hr价格变动情况
    """
    def __init__(self, symbol):
        self.symbol = symbol

    def generate(self):

        data = Ticker24hrFetcher(self.symbol).data()

        # 定义字段对应的中文描述
        field_map = {
            "symbol": "币种",
            "priceChange": "24小时价格变动",
            "priceChangePercent": "24小时价格变动百分比",
            "weightedAvgPrice": "加权平均价",
            "lastPrice": "最近一次成交价",
            "lastQty": "最近一次成交额",
            "openPrice": "24小时内第一次成交价",
            "highPrice": "24小时最高价",
            "lowPrice": "24小时最低价",
            "volume": "24小时成交量",
            "quoteVolume": "24小时成交额",
            "openTime": "24小时内第一笔成交时间",
            "closeTime": "24小时内最后一笔成交时间",
            "firstId": "首笔成交id",
            "lastId": "末笔成交id",
            "count": "成交笔数"
        }

        # 转换时间字段：openTime 和 closeTime 转成北京时间（UTC+8）
        if "openTime" in data:
            beijing_time = datetime.fromtimestamp(data["openTime"] / 1000, tz=timezone(timedelta(hours=8)))
            data["openTime"] = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        if "closeTime" in data:
            beijing_time = datetime.fromtimestamp(data["closeTime"] / 1000, tz=timezone(timedelta(hours=8)))
            data["closeTime"] = beijing_time.strftime("%Y-%m-%d %H:%M:%S")

        markdown_content = "# 24小时价格变动情况\n\n"
        for key, value in data.items():
            desc = field_map.get(key, key)
            markdown_content += f"- **{desc}**: {value}\n"

        os.makedirs("data", exist_ok=True)
        with open("data/ticker_24hr.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return data
