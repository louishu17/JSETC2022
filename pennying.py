class PennyingStrategy:
    @staticmethod
    def pennying_strategy(buys, sells, price=None):
        if not (buys and sells):
            return []
        max_buy = buys[0][0]
        min_sell = sells[0][0]
        if max_buy > min_sell:
            print("wtf")
            return []

        out = []
        if price is None:
            price = (buys[0][0] + sells[0][0]) / 2
        if max_buy + 1 < price:
            out
