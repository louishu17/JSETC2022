from enum import Enum
import random

MA_LENGTH = 75
CANCEL_IN = 10

up = True

class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

def get_order_id():
    return random.randint(1, 4294967290)

cancel_future = {}

def invert(order):
    order = order.copy()
    order["dir"] = Dir.BUY if order["dir"] == Dir.SELL else Dir.SELL
    order["price"] = int(order["price"] // 10) if order["dir"] == Dir.SELL else int(order["price"] * 10)
    return order

def momentum_order(message, history, tick):
    orders = []
    cancels = []
    sym = "GS"
    global up
    if message["symbol"] == sym:
        if len(message["buy"]) == 0 or len(message["sell"]) == 0:
            return orders, cancels
        current_price = (message["buy"][0][0] + message["sell"][0][0]) / 2.0
        hist_prices = history.last_n_prices(sym, 100)
        if hist_prices and len(hist_prices) > 75:
            ma = sum(hist_prices[-MA_LENGTH:]) / 1.0 / MA_LENGTH
            if current_price < ma and up:
                for i in range(5):
                    orders.append(
                        dict(order_id=get_order_id(), symbol=sym, dir=Dir.SELL, price=message["buy"][0][0], size=10)
                    )
                    up = False
            elif current_price > ma and not up:
                for i in range(5):
                    orders.append(
                        dict(order_id=get_order_id(), symbol=sym, dir=Dir.BUY, price=message["sell"][0][0], size=10)
                    )
                    up = True
    # add our orders to be closed in the future
    cancel_future[tick + CANCEL_IN] = []
    for order in orders:
        cancel_future[tick + CANCEL_IN].append(order["order_id"])
    if tick in cancel_future:
        cancels = cancel_future[tick]
    return orders, cancels
