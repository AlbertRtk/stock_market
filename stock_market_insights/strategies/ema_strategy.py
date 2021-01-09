"""
Strategy based on EMAs crossing.
"""

from marketools.analysis import ema
import math


class EmaStrategy:
    def __init__(self):
        self.ema_long_period = 180
        self.ema_mid_period = 14
        self.ema_short_period = 5
        self.take_profit = 1.1
        self.stop_loss = 0.015
        self.max_positions = 3
        self.min_investment = 1000
        self.max_investment = 1000000

    def __call__(self, day, wallet, traded_stocks, *args, **kwargs):
        stocks_to_buy = dict()
        # buy_sort_keys = dict()
        stocks_to_sell = dict()

        for tck in traded_stocks:
            tck_ohlc = traded_stocks[tck].ohlc[:day]
            close_price = tck_ohlc['Close'].get(day, None)

            if close_price and (tck_ohlc.shape[0] >= self.ema_long_period):
                # calculate EMAs
                ema_long = ema(ohlc=tck_ohlc, window=self.ema_long_period)
                ema_mid = ema(ohlc=tck_ohlc, window=self.ema_mid_period)
                ema_short = ema(ohlc=tck_ohlc, window=self.ema_short_period)

                # buy signals
                buy = (ema_short[-1] > ema_mid[-1] > ema_long[-1]) and (ema_mid[-2] > ema_short[-2] > ema_long[-2])

                if buy:
                    if not wallet.get_volume_of_stocks(tck):
                        # buy!
                        invest = wallet.total_value / self.max_positions
                        invest = max(invest, self.min_investment)
                        invest = min(invest, self.max_investment)
                        invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                        volume_to_buy = math.floor(invest / close_price)
                        # buy_sort_keys[tck] = (ema_mid[-1]-ema_long[-1])/ema_long[-1]
                        stocks_to_buy[tck] = (volume_to_buy, None)

                # sell signals
                sell = (ema_short[-1] < ema_long[-1]) and (ema_long[-2] < ema_short[-2])

                if sell and (tck in wallet.list_stocks()):
                    stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        for tck in wallet.list_stocks():
            # take profit the next day
            if wallet.change(tck) > self.take_profit:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
            # stop loss the next day - price below purchase price
            if wallet.change(tck) < -self.stop_loss:
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        # sort stocks to buy - lower volume increase first
        # sorted_items = sorted(stocks_to_buy.items(),
        #                       key=lambda item: buy_sort_keys[item[0]],
        #                       reverse=True)
        # stocks_to_buy = dict(sorted_items)

        return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
