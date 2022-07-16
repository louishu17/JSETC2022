from collections import deque
from enum import Enum


def init_order_id():
    global order_id
    order_id = 0


def get_order_id():
    global order_id
    order_id += 1
    return order_id


def mean(ls):
    return sum(ls) // len(ls)


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CONVERT = "CONVERT"


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
        # returns tuple: ([bid, quantity], [ask, quantity])
        if sym in self.history and len(self.history) > 0:
            x = self.history[sym][-1]
            if len(x["buy"]) > 0 and len(x["sell"]) > 0:
                return self.history[sym][-1]["buy"][0], self.history[sym][-1]["sell"][0]
        return None

    def last_n_ba(self, sym, n):
        # returns list of tuples: [([bid, quantity], [ask, quantity]), ...]
        res = []
        if sym in self.history and len(self.history) > 0:
            if n > len(self.history):
                n = 0
            for t in self.history[sym][-n:]:
                if len(t["buy"]) > 0 and len(t["sell"]) > 0:
                    res.append((t["buy"][0], t["sell"][0]))
            return res if res != [] else None
        return None

    def last_n_prices(self, sym, n):
        h = self.last_n_ba(sym, n)
        if h:
            for i in range(len(h)):
                h[i] = (h[i][0][0] + h[i][1][0]) / 2.0
        return h
