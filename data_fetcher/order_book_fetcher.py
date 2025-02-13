class OrderBookFetcher:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    def data(self):
        return self.client.futures_order_book(symbol=self.symbol, limit=1000)
