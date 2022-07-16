from utils import CancelTimer, Dir, get_order_id

class PennyingStrategy:
    @staticmethod
    def pennying_strategy(sym, buys, sells, price=None):
        if not (buys and sells):
            return None
        max_buy = buys[0][0]
        min_sell = sells[0][0]
        if max_buy > min_sell:
            print("wtf")
            return None

        buy_orders = []
        sell_orders = []
        cancel_timers = {}
        if price is None:
            # Naive price estimate
            price = (buys[0][0] + sells[0][0]) / 2
        if max_buy + 1 < price and min_sell - 1 > price:
            buy_order_id = get_order_id()
            buy_orders.append(dict(
                order_id=buy_order_id,
                symbol=sym,
                dir=Dir.BUY,
                price=max_buy + 1,
                size=buys[0][1],
                ))
            sell_order_id = get_order_id()
            sell_orders.append(dict(
                order_id=sell_order_id,
                symbol=sym,
                dir=Dir.SELL,
                price=min_sell - 1,
                size=sells[0][1],
                ))
            cancel_timers[buy_order_id] = CancelTimer(
                order_id=buy_order_id,
            )
            cancel_timers[sell_order_id] = CancelTimer(
                order_id=sell_order_id,
            )
        return buy_orders, sell_orders, cancel_timers
