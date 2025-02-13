from . import fetch_data, fetch_fng
import time
from datetime import datetime, timedelta

class OtherFetcher:
    def __init__(self, symbol):
        self.symbol = symbol

    def data(self, days, end_date):
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        start_date_dt = end_date_dt - timedelta(days=days)

        startTime = int(start_date_dt.timestamp() * 1000)
        endTime = int(end_date_dt.timestamp() * 1000)

        # 获取资金费率
        fundingRate = fetch_data("/fapi/v1/fundingRate", params={
            "symbol": self.symbol,
            "startTime": startTime,
            "endTime": endTime
        })
        
        # 未平仓合约数
        openInterest = fetch_data("/fapi/v1/openInterest", params={
            "symbol": self.symbol
        })
        
        # 合约持仓量历史
        openInterestHist = fetch_data("/futures/data/openInterestHist", params={
            "symbol": self.symbol,
            "period": "1h",
            "startTime": startTime,
            "endTime": endTime
        })

        # 大户持仓量多空比
        topLongShortPositionRatio = fetch_data("/futures/data/topLongShortPositionRatio", params={
            "symbol": self.symbol,
            "period": "1h",
            "startTime": startTime,
            "endTime": endTime
        })

        #大户账户数多空比
        topLongShortAccountRatio = fetch_data("/futures/data/topLongShortAccountRatio", params={
            "symbol": self.symbol,
            "period": "1h",
            "startTime": startTime,
            "endTime": endTime
        })

        #多空持仓人数比
        globalLongShortAccountRatio = fetch_data("/futures/data/globalLongShortAccountRatio", params={
            "symbol": self.symbol,
            "period": "1h",
            "startTime": startTime,
            "endTime": endTime
        })

        #合约主动买卖量
        takerlongshortRatio = fetch_data("/futures/data/takerlongshortRatio", params={
            "symbol": self.symbol,
            "period": "1h",
            "startTime": startTime,
            "endTime": endTime
        })

        # 恐慌指数
        fng = fetch_fng()

        return {
            "fundingRate": fundingRate,
            "openInterest": openInterest,
            "openInterestHist": openInterestHist,
            "topLongShortPositionRatio": topLongShortPositionRatio,
            "topLongShortAccountRatio": topLongShortAccountRatio,  
            "globalLongShortAccountRatio": globalLongShortAccountRatio,
            "takerlongshortRatio": takerlongshortRatio,
            "fng": fng
        }
