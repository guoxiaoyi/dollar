from data_fetcher.agg_trades_fetcher import AggTradesFetcher
from collections import defaultdict
import time
import numpy as np
import pandas as pd

class AggTradesHandler:
    def __init__(self, client, symbol):
        self.agg_trades_fetcher = AggTradesFetcher(client, symbol)  # K 线数据获取器
    def generate(self, days, end_date):
        """
        生成 OHLCV 数据
        :param symbol: 交易对 (如 BTCUSDT)
        :param days: 获取多天的数据 (如 5)
        :param end_date: 结束日期 (如 2025-02-09)
        :return: OHLCV 数据
        """
        datas = self.agg_trades_fetcher.data(days, end_date)
        summary = self.summarize_trades(datas)

        # 汇总结果
        result = []
        for timestamp, data in summary.items():
            result.append({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp / 1000)),
                "volume": data['volume'],
                "avg_price": data['avg_price'],
                "sell_ratio": f"{data['sell_ratio']:.2f}"
            })

        # 转换为DataFrame格式
        df = pd.DataFrame(result)

        # 计算过去几天的交易量的百分位数
        whale_threshold = np.percentile(df['volume'], 90)  # 获取90百分位数的交易量

        # 将 sell_ratio 转换为浮动数值
        df['sell_ratio'] = df['sell_ratio'].astype(float)

        # 识别鲸鱼交易
        df['is_whale_trade'] = df['volume'] > whale_threshold

        # 筛选鲸鱼交易记录
        whale_trades = df[df['is_whale_trade']]

        # 将鲸鱼交易数据转换为Markdown格式
        markdown_data = whale_trades.to_markdown(index=False)

        # 保存结果到 data 目录下的 markdown 文件
        with open('data/whale_trades.md', 'w') as file:
            file.write("# 鲸鱼交易记录\n")
            file.write(markdown_data)

        # 输出鲸鱼交易数据
        return whale_trades
    def summarize_trades(self, agg_trades):
        # 用于保存每个时间段的汇总数据
        summary = defaultdict(lambda: {'volume': 0, 'value': 0, 'buy_count': 0, 'sell_count': 0})
        
        for trade in agg_trades:
            timestamp = trade['T'] // 60000 * 60000  # 取整到分钟
            price = float(trade['p'])
            quantity = float(trade['q'])
            
            summary[timestamp]['volume'] += quantity
            summary[timestamp]['value'] += price * quantity
            
            if trade['m']:
                summary[timestamp]['sell_count'] += 1
            else:
                summary[timestamp]['buy_count'] += 1

        # 计算每分钟的平均成交价格和主动卖出单比例
        for timestamp in summary:
            summary[timestamp]['avg_price'] = summary[timestamp]['value'] / summary[timestamp]['volume'] if summary[timestamp]['volume'] > 0 else 0
            summary[timestamp]['sell_ratio'] = summary[timestamp]['sell_count'] / (summary[timestamp]['buy_count'] + summary[timestamp]['sell_count']) if (summary[timestamp]['buy_count'] + summary[timestamp]['sell_count']) > 0 else 0
        
        return summary
