from utils import CancelTrigger, Dir, PositionCloser, get_order_id

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
        if max_buy + 1 < price and min_sell - 1 > price:
            order_id = get_order_id()
            buy_orders.append(dict(
                order_id=order_id,
                symbol=sym,
                dir=Dir.BUY,
                price=max_buy + 1,
                size=buys[0][1],
                ))
            order_id = get_order_id()
            sell_orders.append(dict(
                order_id=order_id,
                symbol=sym,
                dir=Dir.SELL,
                price=min_sell - 1,
                size=sells[0][1],
                ))
            cancel_trigger_buy = CancelTrigger(
                order_id=order_id,
                trigger_price=max_buy + 2,
                action=Dir.BUY
            )
            cancel_trigger_sell = CancelTrigger(
                order_id=order_id,
                trigger_price=min_sell - 2,
                action=Dir.SELL
            )
            position_closer = PositionCloser(
                cancel_trigger_buy,
                cancel_trigger_sell
            )
        return buy_orders, sell_orders, position_closer
