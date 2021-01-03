"""

"""

from marketools.analysis import ema
import math
from scipy.stats import linregress


EMA_LONG_PERIOD = 180
EMA_MID_PERIOD = 14
EMA_SHORT_PERIOD = 5
TAKE_PROFIT = 1.1
STOP_LOSS = 0.015
MAX_POSITIONS = 3
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000

EMA_LONG_TREND_PERIOD = 20
MIN_EMA_LONG_RELATIVE_SLOPE = 0.001


def ema_strategy(day, wallet, traded_stocks, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price and (tck_ohlc.shape[0] >= EMA_LONG_PERIOD):
            # calculate EMAs
            ema_long = ema(ohlc=tck_ohlc, window=EMA_LONG_PERIOD)
            ema_mid = ema(ohlc=tck_ohlc, window=EMA_MID_PERIOD)
            ema_short = ema(ohlc=tck_ohlc, window=EMA_SHORT_PERIOD)

            slope, *_ = linregress(ema_long.values[-EMA_LONG_TREND_PERIOD:],
                                   list(range(EMA_LONG_TREND_PERIOD)))
            slope_rel = slope / ema_long[-EMA_LONG_TREND_PERIOD]

            # buy signals
            buy = (ema_short[-1] > ema_mid[-1] > ema_long[-1]) and (ema_mid[-2] > ema_short[-2] > ema_long[-2])
            buy = buy and (slope_rel >= MIN_EMA_LONG_RELATIVE_SLOPE)

            if buy:
                if not wallet.get_volume_of_stocks(tck):
                    # buy!
                    invest = wallet.total_value / MAX_POSITIONS
                    invest = max(invest, MIN_INVESTMENT)
                    invest = min(invest, MAX_INVESTMENT)
                    invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                    volume_to_buy = math.floor(invest / close_price)
                    stocks_to_buy[tck] = (volume_to_buy, None)

            # sell signals
            sell = (ema_short[-1] < ema_long[-1]) and (ema_long[-2] < ema_short[-2])

            if sell and (tck in wallet.list_stocks()):
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    for tck in wallet.list_stocks():
        # take profit the next day
        if wallet.change(tck) > TAKE_PROFIT:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
        # stop loss the next day - price below purchase price
        if wallet.change(tck) < -STOP_LOSS:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    return stocks_to_buy, stocks_to_sell


def set_ema_long_period(value):
    global EMA_LONG_PERIOD
    EMA_LONG_PERIOD = value


def set_ema_mid_period(value):
    global EMA_MID_PERIOD
    EMA_MID_PERIOD = value


def set_ema_short_period(value):
    global EMA_SHORT_PERIOD
    EMA_SHORT_PERIOD = value


def set_take_profit(value):
    global TAKE_PROFIT
    TAKE_PROFIT = value


def set_stop_loss(value):
    global STOP_LOSS
    STOP_LOSS = value


def set_max_positions(value):
    global MAX_POSITIONS
    MAX_POSITIONS = value


def set_min_investment(value):
    global MIN_INVESTMENT
    MIN_INVESTMENT = value


def set_max_investment(value):
    global MAX_INVESTMENT
    MAX_INVESTMENT = value


def set_ema_long_trend_period(value):
    global EMA_LONG_TREND_PERIOD
    EMA_LONG_TREND_PERIOD = value


def set_min_ema_long_relative_slope(value):
    global MIN_EMA_LONG_RELATIVE_SLOPE
    MIN_EMA_LONG_RELATIVE_SLOPE = value


if __name__ == '__main__':
    pass
