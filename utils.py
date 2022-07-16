from collections import deque
from enum import Enum


def init_order_id():
    global order_id
    order_id = 0


def get_order_id():
    global order_id
    order_id += 1
    return order_id


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PriceHistory:
    """
    run history.update(msg) every book msg
    history.get(sym) -> [
        {
            "buy": list of buy orders as [price, qty],
            "sell": list of sell orders as [price, qty],
            "price": avg of max buy and min sell
        }, ...
    ]
    """

    def __init__(self):
        self.history = {}

    def update(self, msg):
        if msg["type"] != "book":
            print("WARN: PriceHistory update not a book msg")

        if msg["symbol"] not in self.history:
            self.history[msg["symbol"]] = deque(maxlen=100)
        self.history[msg["symbol"]].append({
            "buy": msg["buy"],
            "sell": msg["sell"],
            "price": (
                (msg["buy"][0][0] + msg["sell"][0][0]) / 2
                if msg["buy"] and msg["sell"] else None
            ),
        })

    def get(self, sym):
        if sym not in self.history:
            return []
        return self.history[sym]

    def last_price(self, sym):
        return self.history[sym][-1]["price"]

    def last_ba(self, sym):
        """# returns tuple: ([bid, quantity], [ask, quantity])
        return self.history[sym][-1]["buy"][0],


self.history[sym][-1]["sell"][0]
"""

class CancelTrigger:
    def __init__(self, order_id: int, trigger_price: int, action: Dir) -> None:
        self.order_id = order_id
        self.trigger_price = trigger_price
        self.action = action

    def tick(self, sym: str, history: PriceHistory):
        fair_price = (history[sym]["buy"][0][0] + history[sym]["sell"][0][0]) / 2
        return self.tick_helper(self, fair_price)

    def tick_helper(self, fair_price: int):
        cancel_order = None
        if self.action is Dir.BUY and fair_price < self.trigger_price:
            cancel_order = dict(order_id=self.order_id)
        elif self.action is Dir.SELL and fair_price > self.trigger_price:
            cancel_order = dict(order_id=self.order_id)
        return cancel_order
