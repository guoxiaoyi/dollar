import os
from data_fetcher.other_fetcher import OtherFetcher
from datetime import datetime, timezone

class OtherHandler():
    def __init__(self, symbol):
        self.other_fetcher = OtherFetcher(symbol)  # K 线数据获取器

    def generate(self, days, end_date):
        data = self.other_fetcher.data(days, end_date)
        # Create markdown content
        markdown = self.create_markdown(data)

        # Write to markdown file
        os.makedirs("data", exist_ok=True)
        with open("data/other.md", "w") as file:
            file.write(markdown)

        return data
    def timestamp_to_date(self, timestamp):
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Function to create markdown content
    def create_markdown(self, data):
        markdown_content = "# 资金费率\n\n"
        markdown_content += "| Funding Time | Funding Rate | Mark Price |\n"
        markdown_content += "|--------------|--------------|------------|\n"
        
        for entry in data['fundingRate']:
            funding_time = self.timestamp_to_date(entry['fundingTime'])
            markdown_content += f"| {funding_time} | {entry['fundingRate']} | {entry['markPrice']} |\n"
        
        markdown_content += "\n# 未平仓合约数\n\n"
        markdown_content += "| 未平仓合约数量 | 撮合引擎时间 |\n"
        markdown_content += "|--------------|--------------|\n"
        markdown_content += f"|{data['openInterest']['openInterest']}|{self.timestamp_to_date(data['openInterest']['time'])}|\n"
        

        # {'symbol': 'BTCUSDT', 'sumOpenInterest': '76382.48600000', 'sumOpenInterestValue': '7462561243.95140000', 'timestamp': 1739185200000}
        markdown_content += "\n# 合约持仓量历史\n\n"
        markdown_content += "| 持仓总数量 | 持仓总价值 | 时间 |\n"
        markdown_content += "|--------------|--------------|------------|\n"

        for entry in data['openInterestHist']:
            timestamp = self.timestamp_to_date(entry['timestamp'])
            markdown_content += f"| {entry['sumOpenInterest']} | {entry['sumOpenInterestValue']} | {timestamp} |\n"


        markdown_content += "\n# 大户持仓量多空比\n\n"
        markdown_content += "| 大户多空持仓量比值 | 大户多仓持仓量比例 | 大户空仓持仓量比例 | 时间 |\n"
        markdown_content += "|--------------|--------------|------------|------------|\n"
        # {'symbol': 'BTCUSDT', 'longAccount': '0.6632', 'longShortRatio': '1.9691', 'shortAccount': '0.3368', 'timestamp': 1739185200000}
        for entry in data['topLongShortPositionRatio']:
            timestamp = self.timestamp_to_date(entry['timestamp'])
            markdown_content += f"| {entry['longShortRatio']} | {entry['longAccount']} | {entry['shortAccount']} | {timestamp} |\n"
     
     
        markdown_content += "\n# 大户账户数多空比\n\n"
        markdown_content += "| 大户多空账户数比值 | 大户多仓账户数比例 | 大户空仓账户数比例 | 时间 |\n"
        markdown_content += "|--------------|--------------|------------|------------|\n"
        # {'symbol': 'BTCUSDT', 'longAccount': '0.6632', 'longShortRatio': '1.9691', 'shortAccount': '0.3368', 'timestamp': 1739185200000}
        for entry in data['topLongShortAccountRatio']:
            timestamp = self.timestamp_to_date(entry['timestamp'])
            markdown_content += f"| {entry['longShortRatio']} | {entry['longAccount']} | {entry['shortAccount']} | {timestamp} |\n"
  
  
        markdown_content += "\n# 多空持仓人数比\n\n"
        markdown_content += "| 多空人数比值 | 多仓人数比例 | 空仓人数比例 | 时间 |\n"
        markdown_content += "|--------------|--------------|------------|------------|\n"
        # { "symbol":"BTCUSDT", "longShortRatio":"0.1960", // 多空人数比值 "longAccount": "0.6622", // 多仓人数比例 "shortAccount":"0.3378", // 空仓人数比例 "timestamp":"1583139600000" }
        for entry in data['globalLongShortAccountRatio']:
            timestamp = self.timestamp_to_date(entry['timestamp'])
            markdown_content += f"| {entry['longShortRatio']} | {entry['longAccount']} | {entry['shortAccount']} | {timestamp} |\n"

        markdown_content += "\n# 合约主动买卖量\n\n"
        markdown_content += "| buySellRatio | 主动买入量 | 主动卖出量 | 时间 |\n"
        markdown_content += "|--------|--------------|--------------|------------|\n"
        #  { buySellRatio: "1.5586", buyVol: "387.3300", // 主动买入量 sellVol: "248.5030", // 主动卖出量 timestamp: "1585614900000", },
        for entry in data['takerlongshortRatio']:
            timestamp = self.timestamp_to_date(entry['timestamp'])
            markdown_content += f"| {entry['buySellRatio']} | {entry['buyVol']} | {entry['sellVol']} | {timestamp} |\n"


        markdown_content += "\n# 恐慌指数\n\n"
        markdown_content += "| Value | Classification | Timestamp |\n"
        markdown_content += "|-------|----------------|-----------|\n"

        for entry in data['fng']['data']:
            timestamp = self.timestamp_to_date(int(entry['timestamp']) * 1000 )
            markdown_content += f"| {entry['value']} | {entry['value_classification']} | {timestamp} |\n"
        
        return markdown_content
