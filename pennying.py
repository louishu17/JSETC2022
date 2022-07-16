from utils import Dir, get_order_id

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
        if price is None:
            # Naive price estimate
            price = (buys[0][0] + sells[0][0]) / 2
        if max_buy + 1 < price:
            buy_orders.append(dict(
                order_id=get_order_id(),
                symbol=sym,
                dir=Dir.BUY,
                price=max_buy + 1,
                size=buys[0][1],
                ))
        if min_sell - 1 > price:
            sell_orders.append(dict(
                order_id=get_order_id(),
                symbol=sym,
                dir=Dir.SELL,
                price=min_sell - 1,
                size=sells[0][1],
                ))
        return buy_orders, sell_orders
