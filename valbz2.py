
from utils import Dir, PriceHistory, get_order_id, mean


def valbz_strategy(valbz_trade_info, vale_trade_info):

    vale_prices = list(map(lambda x: x[0], vale_trade_info))
    valbz_prices = list(map(lambda x: x[0], valbz_trade_info))

    if len(vale_prices) >= 10 and len(valbz_prices) >= 10:
        last_10_vale_prices = vale_prices[-10:]
        last_10_valbz_prices = valbz_prices[-10:]

        avg_strat = moving_10_day_average(
            last_10_valbz_prices, last_10_vale_prices)
        if avg_strat:
            res = []
            res.append({"order_id": get_order_id(),
                       "symbol": "VALE", "dir": Dir.BUY, "price": avg_strat[0] + 1, "size": 10})
            res.append({"order_id": get_order_id(),
                       "symbol": "VALE", "dir": Dir.SELL, "size": 10})
            res.append({"order_id": get_order_id(),
                       "symbol": "VALBZ", "dir": Dir.SELL, "price": avg_strat[1] - 1, "size": 10})
            return res
    return []


def moving_10_day_average(common_stock, adr_stock):
    avg_common_stock = mean(common_stock)
    avg_adr_stock = mean(adr_stock)

    diff = avg_common_stock - avg_adr_stock
    if diff >= 5:
        return [avg_adr_stock, avg_common_stock]

    return []
