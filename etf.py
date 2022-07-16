from utils import PriceHistory, get_order_id, Dir


class ETFStrategy:
    @classmethod
    # there is only one ETF so we can hardcode it
    def etf_strategy(history: PriceHistory):
        fair_prices = {}
        for sym in ["BOND", "GS", "MS", "WFC"]:
            history_book = history.get_last(sym)
            fair_prices[sym] = (history_book["buy"][0][0] + history_book["sell"][0][0]) / 2
        etf_price = (
            3 * fair_prices["BOND"] +
            2 * fair_prices["GS"] +
            3 * fair_prices["MS"] +
            2 * fair_prices["WFC"]
        )

        buys = history_book["buy"]
        sells = history_book["sell"]

        buy_orders = []
        sell_orders = []
        for i in range(len(sells)):
            if sells[i][0] < etf_price:
                buy_orders.append(
                    dict(order_id=get_order_id(), symbol="BOND", dir=Dir.BUY, price=sells[i][0], size=sells[i][1])
                )

        for i in range(len(buys)):
            if buys[i][0] > etf_price:
                sell_orders.append(
                    dict(order_id=get_order_id(), symbol="BOND", dir=Dir.SELL, price=buys[i][0], size=buys[i][1]))
        return buy_orders, sell_orders
