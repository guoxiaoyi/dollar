import json
from data_fetcher.order_book_fetcher import OrderBookFetcher
from datetime import datetime

class OrderBookHandler:
    """
    负责处理和分析 OHLCV 数据的类
    """

    def __init__(self, client, symbol):
        self.order_book_fetcher = OrderBookFetcher(client, symbol)  # K 线数据获取器
        self.client = client
        self.symbol = symbol

    def generate(self):

        # 1. 解析数据为列表结构
        order_book_raw = self.order_book_fetcher.data()
        order_book_parts = {
            "meta": {
                "lastUpdateId": order_book_raw['lastUpdateId'],
                "E": order_book_raw['E'],
                "T": order_book_raw['T']
            },
            "bids": self.order_book_split_list(order_book_raw['bids'], 3),
            "asks": self.order_book_split_list(order_book_raw['asks'], 3)
        }
        return order_book_parts
    
        output = []
        bids, asks = self.parse_depth_data(order_book_raw)
        
        # 2. 获取最优买价和卖价
        best_bid, best_ask = self.get_best_bid_ask(bids, asks)
        output.append(f"最优买价 (price={best_bid[0]:.2f}, qty={best_bid[1]:.4f})")
        output.append(f"最优卖价 (price={best_ask[0]:.2f}, qty={best_ask[1]:.4f})\n")
        
        # 3. 统计买单卖单的总数量
        total_bid_qty, total_ask_qty = self.get_total_quantity(bids, asks)
        output.append(f"买盘总数量: {total_bid_qty:.4f}")
        output.append(f"卖盘总数量: {total_ask_qty:.4f}\n")
        
        # 4. 计算中位价
        mid_price = self.get_mid_price(best_bid, best_ask)
        output.append(f"中位价: {mid_price:.2f}\n")
        
        # 5. 计算前 N 档买盘和卖盘的 VWAP
        bids_sorted_desc = sorted(bids, key=lambda x: x[0], reverse=True)
        asks_sorted_asc = sorted(asks, key=lambda x: x[0])
        top_n = 5
        vwap_bids_top5 = self.calculate_vwap(bids_sorted_desc, top_n)
        vwap_asks_top5 = self.calculate_vwap(asks_sorted_asc, top_n)
        output.append(f"前 {top_n} 档买盘VWAP: {vwap_bids_top5:.2f}")
        output.append(f"前 {top_n} 档卖盘VWAP: {vwap_asks_top5:.2f}\n")
        
        # 6. 寻找买卖盘中挂单量最大的前 n 个价位
        n_big_orders = 50
        top_bids_by_qty, top_asks_by_qty = self.find_top_n_levels_by_quantity(bids, asks, n=n_big_orders)
        
        output.append(f"--- 挂单量最大的前 {n_big_orders} 个买单(潜在支撑位) ---")
        for i, (p, q) in enumerate(top_bids_by_qty, start=1):
            output.append(f"  {i}. Price={p:.2f}, Qty={q:.4f}")
        
        output.append(f"\n--- 挂单量最大的前 {n_big_orders} 个卖单(潜在压力位) ---")
        for i, (p, q) in enumerate(top_asks_by_qty, start=1):
            output.append(f"  {i}. Price={p:.2f}, Qty={q:.4f}")
        
        # 7. 简单的突破/跌破逻辑提示（示例）
        #    假设我们把 "最大的买单价" 看作重要支撑，"最大的卖单价" 看作重要压力：
        if top_bids_by_qty:
            major_support_price = top_bids_by_qty[0][0]  # 买盘中qty最大的那个价
            if best_ask[0] < major_support_price:
                output.append(f"\n[提示] 当前卖一({best_ask[0]:.2f})远低于最大买单价({major_support_price:.2f})，说明价格在支撑位之上。")
            else:
                output.append(f"\n[提示] 当前卖一({best_ask[0]:.2f})已经低于或逼近最大买单价({major_support_price:.2f})，可能面临跌破支撑的风险。")
        
        if top_asks_by_qty:
            major_resistance_price = top_asks_by_qty[0][0]  # 卖盘中qty最大的那个价
            if best_bid[0] > major_resistance_price:
                output.append(f"[提示] 当前买一({best_bid[0]:.2f})高于最大卖单价({major_resistance_price:.2f})，说明价格在压力位之上。")
            else:
                output.append(f"[提示] 当前买一({best_bid[0]:.2f})尚未突破最大卖单价({major_resistance_price:.2f})，可能仍受压制。")
        
        return '\n'.join(output)
    def parse_depth_data(self, depth_data: dict):
        """
        将订单簿的 bids 和 asks 转化为便于分析的列表结构 (price, quantity)，并且转成浮点类型。
        """
        bids = [(float(price), float(qty)) for price, qty in depth_data['bids']]
        asks = [(float(price), float(qty)) for price, qty in depth_data['asks']]
        return bids, asks

    def get_best_bid_ask(self, bids, asks):
        """
        获取最优买价（最高的买价）和最优卖价（最低的卖价）。
        返回：
            best_bid (price, qty)
            best_ask (price, qty)
        """
        best_bid = max(bids, key=lambda x: x[0])
        best_ask = min(asks, key=lambda x: x[0])
        return best_bid, best_ask

    def get_total_quantity(self, bids, asks):
        """
        计算所有买单和所有卖单的总数量（累加）。
        """
        total_bid_qty = sum(qty for _, qty in bids)
        total_ask_qty = sum(qty for _, qty in asks)
        return total_bid_qty, total_ask_qty

    def get_mid_price(self, best_bid, best_ask):
        """
        计算中位价（mid price），即 (best_bid_price + best_ask_price)/2
        """
        return (best_bid[0] + best_ask[0]) / 2

    def calculate_vwap(self, levels, top_n):
        """
        演示基于前 N 档计算成交量加权平均价（VWAP）的思路：
        vwap = (Σ (price_i * qty_i)) / (Σ qty_i)
        
        参数：
            levels: [(price, qty), (price, qty), ...] 已按价格从高到低(买盘)或从低到高(卖盘)排好
            top_n: 需要取多少档来计算
            
        返回：
            对应前 N 档的 VWAP
        """
        selected_levels = levels[:top_n]
        total_notional = 0.0
        total_qty = 0.0
        
        for price, qty in selected_levels:
            total_notional += price * qty
            total_qty += qty
        
        if total_qty == 0:
            return 0
        return total_notional / total_qty

    def find_top_n_levels_by_quantity(self, bids, asks, n=3):
        """
        找到挂单量最大的前 n 档买单、前 n 档卖单
        返回:
        top_bids_by_qty: [(price, qty), ...] (从大到小)
        top_asks_by_qty: [(price, qty), ...] (从大到小)
        """
        # 先分别按quantity大小排序
        bids_sorted_by_qty = sorted(bids, key=lambda x: x[1], reverse=True)
        asks_sorted_by_qty = sorted(asks, key=lambda x: x[1], reverse=True)
        
        top_bids_by_qty = bids_sorted_by_qty[:n]
        top_asks_by_qty = asks_sorted_by_qty[:n]
        
        return top_bids_by_qty, top_asks_by_qty
    

    def order_book_split_list(self, lst, n):
        """将列表lst分成n个大致相等的部分"""
        k, m = divmod(len(lst), n)
        return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]