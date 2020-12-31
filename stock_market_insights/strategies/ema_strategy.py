"""

"""

from marketools.analysis import ema
from datetime import date
import math

EMA_LONG_PERIOD = 50
EMA_MID_PERIOD = 15
EMA_SHORT_PERIOD = 5
TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000


def volume_strategy(day, wallet, traded_stocks, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price:
            # calculate EMAs
            ema_long = ema(ohlc=tck_ohlc, window=EMA_LONG_PERIOD)
            ema_mid = ema(ohlc=tck_ohlc, window=EMA_MID_PERIOD)
            ema_short = ema(ohlc=tck_ohlc, window=EMA_SHORT_PERIOD)

            # buy signals
            #   - short crosses long, or
            #   - short crosses mid and mid greater than long

            # sell signals - short crosses mid

    for tck in wallet.list_stocks():
        # take profit the next day
        if wallet.change(tck) > TAKE_PROFIT:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
        # stop loss the next day - price below purchase price
        if wallet.change(tck) < -STOP_LOSS:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
