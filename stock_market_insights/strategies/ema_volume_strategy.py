"""
TODO: description
"""

from marketools.analysis import ema, mean_volume_on_date
from .strategy import Strategy
import math


class EmaVolStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.ema_long_period = 180
        self.ema_mid_period = 14
        self.ema_short_period = 5
        self.vol_mean_long_window = 75
        self.vol_mean_short_window = 1
        self.min_vol_increase_to_buy = 1.6
        # self.min_vol_increase_to_sell = 6
        self.take_profit = 1.1
        self.stop_loss = 0.022
        self.max_positions = 3
        self.min_investment = 1000
        self.max_investment = 1000000

    def __call__(self, day, wallet, traded_stocks, *args, **kwargs):
        stocks_to_buy = dict()
        buy_sort_keys = dict()
        stocks_to_sell = dict()

        for tck in traded_stocks:
            tck_ohlc = traded_stocks[tck].ohlc[:day]
            close_price = tck_ohlc['Close'].get(day, None)

            if close_price and (tck_ohlc.shape[0] >= self.ema_long_period):
                # calculate EMAs
                ema_long = ema(ohlc=tck_ohlc, window=self.ema_long_period)
                ema_mid = ema(ohlc=tck_ohlc, window=self.ema_mid_period)
                ema_short = ema(ohlc=tck_ohlc, window=self.ema_short_period)

                vol_mean_long = mean_volume_on_date(tck_ohlc, day, window=self.vol_mean_long_window)
                vol_mean_short = mean_volume_on_date(tck_ohlc, day, window=self.vol_mean_short_window)
                vol_mean_short_long_ratio = vol_mean_short / vol_mean_long

                # buy signals
                vol_increased = vol_mean_short_long_ratio >= self.min_vol_increase_to_buy
                ema_crossed = (ema_short[-1] > ema_mid[-1] > ema_long[-1]) \
                              and (ema_mid[-2] > ema_short[-2] > ema_long[-2])
                buy = vol_increased and ema_crossed

                if buy:
                    if not wallet.get_volume_of_stocks(tck):
                        # buy!
                        invest = wallet.total_value / self.max_positions
                        invest = max(invest, self.min_investment)
                        invest = min(invest, self.max_investment)
                        invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                        volume_to_buy = math.floor(invest / close_price)
                        buy_sort_keys[tck] = vol_mean_short_long_ratio
                        stocks_to_buy[tck] = (volume_to_buy, None)

                # sell signals
                sell = (ema_short[-1] < ema_long[-1]) and (ema_long[-2] < ema_short[-2])
                # vol_sell = (vol_mean_short_long_ratio >= self.min_vol_increase_to_sell) \
                #            and all((ema_short.tail(5)-ema_mid.tail(5)) > 0)
                # sell = sell or vol_sell

                if sell and (tck in wallet.list_stocks()):
                    stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

        stocks_to_sell.update(self.get_stocks_take_profit(wallet))
        stocks_to_sell.update(self.get_stocks_stop_loss(wallet))

        # sort stocks to buy
        sorted_items = sorted(stocks_to_buy.items(),
                              key=lambda item: buy_sort_keys[item[0]],
                              reverse=False)
        stocks_to_buy = dict(sorted_items)

        return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
