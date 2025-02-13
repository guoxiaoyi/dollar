import os
import csv
import requests
import time
from datetime import datetime, timedelta


class KlineFetcher:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    def data(self, days: int, end_date: str):
        """
        获取 K 线数据，并返回 {"4h": [], "1h": []}
        end_date 格式应为 "YYYY-MM-DD HH:MM:SS"
        """
        # 使用包含时分秒的格式解析 end_date
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        # 计算开始日期（注意：start_date 同样可能不在整点）
        start_date = end_date - timedelta(days=days)

        directory_4h = 'klines/4h'
        directory_1h = 'klines/1h'
        os.makedirs(directory_4h, exist_ok=True)
        os.makedirs(directory_1h, exist_ok=True)

        kline_data = {"4h": [], "1h": []}

        current_date = start_date
        # 循环天数（按日期区分）
        while current_date.date() <= end_date.date():
            date_str = current_date.strftime('%Y-%m-%d')

            # 针对第一天，如果start_date不在 00:00:00，则使用实际时间
            if current_date.date() == start_date.date():
                day_start = start_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                day_start = f"{date_str} 00:00:00"

            # 针对最后一天，如果 end_date 不在 23:59:59，则使用实际时间
            if current_date.date() == end_date.date():
                day_end = end_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                day_end = f"{date_str} 23:59:59"

            klines_4h = self.fetch_kline_data('4h', date_str, directory_4h, day_start, day_end)
            kline_data["4h"].extend(klines_4h)

            klines_1h = self.fetch_kline_data('1h', date_str, directory_1h, day_start, day_end)
            kline_data["1h"].extend(klines_1h)

            current_date += timedelta(days=1)

        return kline_data

    def fetch_kline_data(self, interval: str, date_str: str, directory: str, start_time_str: str = None, end_time_str: str = None):
        """
        先检查本地是否存在数据，
        若存在则读取本地数据，否则从 Binance 获取
        可以传入特定的起始和结束时间字符串以精确定义查询区间
        """
        file_path = os.path.join(directory, f"{date_str}.csv")

        # if os.path.exists(file_path):
        #     print(f"读取本地 {interval} K 线数据: {file_path}")
        #     return self.read_kline_data_from_csv(file_path)

        if start_time_str is None:
            start_time_str = f"{date_str} 00:00:00"
        if end_time_str is None:
            end_time_str = f"{date_str} 23:59:59"

        start_time = self.date_to_timestamp(start_time_str)
        end_time = self.date_to_timestamp(end_time_str)

        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {
            "symbol": self.symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            klines = response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")

        formatted_klines = [
            [kline[0], kline[1], kline[2], kline[3], kline[4], kline[5], kline[6], kline[7], kline[8], kline[9], kline[10]]
            for kline in klines
        ]

        self.save_kline_data_to_csv(formatted_klines, file_path)
        return formatted_klines

    def read_kline_data_from_csv(self, file_path: str):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过表头
            return [row for row in reader]

    def save_kline_data_to_csv(self, klines, file_path: str):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "open_time", "open", "high", "low",
                "close", "volume", "close_time", "quote_volume",
                "count", "taker_buy_volume", "taker_buy_quote_volume"
            ])
            writer.writerows(klines)

    def date_to_timestamp(self, date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(dt.timetuple())) * 1000  # 毫秒级时间戳
    