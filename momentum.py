from enum import Enum
import random

CLOSE_IN = 25

class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

def get_order_id():
    return random.randint(1, 4294967290)

close_future = {}

def invert(order):
    order = order.copy()
    order["dir"] = Dir.BUY if order["dir"] == Dir.SELL else Dir.SELL
    order["price"] = int(order["price"] // 10) if order["dir"] == Dir.SELL else int(order["price"] * 10)
    return order

def momentum_order(message, history, tick):
    orders = []
    cancels = []
    if message["symbol"] == "XLF":
        hist_orders = history.last_n_ba(sym, 100)
        if hist_orders and len(hist_orders) > 75:

    # add our orders to be closed in the future
    close_future_orders[tick + CLOSE_IN] = [invert(o) for o in orders]
    orders += close_future_orders[tick] if tick in close_future_orders else []
    order_ids[tick + CANCEL_IN] = []
    for order in orders:
        order_ids[tick + CANCEL_IN].append(order["order_id"])
    if tick in order_ids:
        cancels = order_ids[tick]
    return orders, cancels
