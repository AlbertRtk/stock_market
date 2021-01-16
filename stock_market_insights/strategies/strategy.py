

class Strategy:
    def __init__(self):
        self.take_profit = 0.0
        self.stop_loss = 0.0

    def tp_stocks(self, wallet):
        stocks_to_sell = dict()

        for tck in wallet.list_stocks():
            # take profit the next day
            if wallet.change(tck) > self.take_profit:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        return stocks_to_sell

    def sl_stocks(self, wallet):
        stocks_to_sell = dict()

        for tck in wallet.list_stocks():
            # stop loss the next day - price below purchase price
            if wallet.change(tck) < -self.stop_loss:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        return stocks_to_sell
