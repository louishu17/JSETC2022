from enum import Enum
import random

CANCEL_IN = 15
CLOSE_IN = 15

class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

def get_order_id():
    return random.randint(1, 4294967290)

order_ids = {}
close_future_orders = {}
net = 0

def invert_order(order):
    order = order.copy()
    order["dir"] = Dir.BUY if order["dir"] == Dir.SELL else Dir.SELL
    return order

def valbz_order(message, history, tick):
    orders = []
    cancels = []
    if message["symbol"] == "VALE":
        close_future_orders[tick] = []
        if len(message["buy"]) == 0 or len(message["sell"]) == 0:
            return orders, cancels
        vale_bid_price = message["buy"][0]  # these are tuples
        vale_ask_price = message["sell"][0]
        valbz = history.last_ba("VALBZ")
        if valbz:
            valbz_bid_price, valbz_ask_price = valbz
            fair_price = (valbz_bid_price[0] + valbz_ask_price[0]) / 2
            if fair_price > 0.01:
                print("got here!")
                if vale_bid_price[0] / fair_price > 1.01:
                    # sell VALE
                    price = vale_bid_price[0]
                    orders.append(
                        dict(order_id=get_order_id(), symbol="VALE", dir=Dir.SELL, price=price, size=vale_bid_price[1])
                    )

                elif vale_ask_price[0] / fair_price < 0.99:
                    # buy VALE
                    price = vale_ask_price[0]
                    orders.append(
                        dict(order_id=get_order_id(), symbol="VALE", dir=Dir.BUY, price=price, size=vale_ask_price[1])
                    )
    # add our orders to be closed in the future
    close_future_orders[tick + CLOSE_IN] = [invert(o) for o in orders]
    orders += close_future_orders[tick] if tick in close_future_orders else []
    for order in orders:
        order_ids[tick + CANCEL_IN].append(order["order_id"])
    if tick in order_ids:
        cancels = order_ids[tick]
    return orders, cancels
