from enum import Enum
import random
class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

def get_order_id():
    return random.randint(1, 4294967290)

net = 0

def valbz_order(message, history):
    orders = []
    if message["symbol"] == "VALE":
        if len(message["buy"]) == 0 or len(message["sell"]) == 0:
            return []
        vale_bid_price = message["buy"][0]  # these are tuples
        vale_ask_price = message["sell"][0]
        valbz = history.last_ba("VALBZ")
        if valbz:
            valbz_bid_price, valbz_ask_price = valbz
            fair_price = (valbz_bid_price[0] + valbz_ask_price[0]) / 2
            if fair_price > 0.01:
                print("got here!")
                if vale_bid_price[0] / fair_price > 1.00:
                    # sell VALE
                    price = vale_bid_price[0] + 0.01
                    orders.append(
                        dict(order_id=get_order_id(), symbol="VALE", dir=Dir.SELL, price=price, size=vale_bid_price[1])
                    )
                    # sells.append(orders[-1])
                elif vale_ask_price[0] / fair_price < 1.00:
                    # buy VALE
                    price = vale_ask_price[0] - 0.01
                    orders.append(
                        dict(order_id=get_order_id(), symbol="VALE", dir=Dir.BUY, price=price, size=vale_ask_price[1])
                    )
                    # buys.append(orders[-1])

    return orders
