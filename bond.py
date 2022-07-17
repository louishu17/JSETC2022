from utils import get_order_id, Dir


class BondStrategy:
    """
    def bondStrategy(buys, sells):
        buy_orders = []
        sell_orders = []
        for i in range(len(sells)):
            if sells[i][0] < 1000:
                buy_orders.append(
                    dict(order_id=get_order_id(), symbol="BOND", dir=Dir.BUY, price=sells[i][0], size=sells[i][1])
                )

        for i in range(len(buys)):
            if buys[i][0] > 1000:
                sell_orders.append(
                    dict(order_id=get_order_id(), symbol="BOND", dir=Dir.SELL, price=buys[i][0], size=buys[i][1]))
        return buy_orders, sell_orders
    """

    def bondStrategy(buys, sells, tick):
        buy_orders = []
        sell_orders = []
        if tick % 300 == 0:
            buy_orders.append(
                dict(order_id=get_order_id(), symbol="BOND",
                     dir=Dir.BUY, price=999, size=100)
            )
            sell_orders.append(
                dict(order_id=get_order_id(), symbol="BOND",
                     dir=Dir.SELL, price=1001, size=100)
            )
        return buy_orders, sell_orders