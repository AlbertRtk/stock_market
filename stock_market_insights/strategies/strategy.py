

class Strategy:
    def __init__(self):
        self.take_profit = 0.0
        self.stop_loss = 0.0
        self.linear_stop_lose_slop = 0.0

    def get_stocks_take_profit(self, wallet):
        stocks_to_sell = dict()

        for tck in wallet.list_stocks():
            # take profit the next day
            if wallet.change(tck) > self.take_profit:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        return stocks_to_sell

    def get_stocks_stop_loss(self, wallet):
        stocks_to_sell = dict()

        for tck in wallet.list_stocks():
            # stop loss the next day - price below purchase price
            if wallet.change(tck) < -self.stop_loss:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        return stocks_to_sell

    def get_stocks_linear_stop_loss(self, wallet):
        pass
        # TODO: wallet needs to store purchase date
        # stocks_to_sell = dict()
        #
        # for tck in wallet.list_stocks():
        #     purchase_price = wallet.get_purchase_price_of_stocks(tck)
        #     # stop loss the next day - price below purchase price
        #     if wallet.change(tck) < -self.stop_loss:
        #         stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
        #
        # return stocks_to_sell
