from analyzer.ohlcv import OhlcvHandler
from analyzer.order_book import OrderBookHandler
from analyzer.agg_trades import AggTradesHandler
from analyzer.ticker_24hr import Ticker24hrHandler
from analyzer.other import OtherHandler

class Analyzer:
    """
    统一分析器类，封装所有数据分析逻辑
    """
    def __init__(self, client):
        """
        初始化 Analyzer 类
        """
        # 使用在 __init__.py 中初始化的 ohlcv_handler
        self.client = client  


    def ohlcv(self, symbol, days, end_data):
        """
        提供 K 线数据分析
        """

        ohlcv_handler = OhlcvHandler(self.client, symbol)
        return ohlcv_handler.generate(days, end_data)
    
    def order_book(self, symbol):
        """
        提供订单簿数据分析
        """
        order_book_handler = OrderBookHandler(self.client, symbol)
        return order_book_handler.generate()

    def agg_trades(self, symbol, days, end_data):
        """
        提供订单簿数据分析
        """
        agg_trades_handler = AggTradesHandler(self.client, symbol)
        return agg_trades_handler.generate(days, end_data)

    def ticker_24hr(self, symbol):
        """
        提供24小时价格变动数据分析
        """
        return Ticker24hrHandler(symbol).generate()

    def other(self, symbol, days, end_data):
        """
        提供24小时价格变动数据分析
        """
        return OtherHandler(symbol).generate(days, end_data)

