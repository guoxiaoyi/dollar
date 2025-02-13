from . import fetch_data
from datetime import datetime, timedelta

class AggTradesFetcher:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    def data(self, days, end_date):
        # 将end_date转换为datetime对象，并计算开始日期
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        start_date_dt = end_date_dt - timedelta(days=days)
        all_results = []

        # 循环每1小时的时间间隔请求数据
        current = start_date_dt
        while current < end_date_dt:
            next_interval = current + timedelta(hours=1)
            if next_interval > end_date_dt:
                next_interval = end_date_dt

            params = {
                "symbol": self.symbol,
                "limit": 1000,
                "startTime": int(current.timestamp() * 1000),
                "endTime": int(next_interval.timestamp() * 1000)
            }
            data = fetch_data("/fapi/v1/aggTrades", params=params)
            all_results.extend(data)
            current = next_interval

        return all_results
