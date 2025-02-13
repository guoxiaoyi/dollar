from . import fetch_data
class Ticker24hrFetcher:
    def __init__(self, symbol):
        self.symbol = symbol

    def data(self):
        data = fetch_data("/fapi/v1/ticker/24hr", params={"symbol": self.symbol})
        return data
