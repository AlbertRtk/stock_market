"""

"""

from marketools.analysis import ema
import math

EMA_LONG_PERIOD = 100
EMA_MID_PERIOD = 15
EMA_SHORT_PERIOD = 5
MIN_LONG_EMA_TREND_LENGTH = 2
TAKE_PROFIT = 0.5
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 3000
MAX_INVESTMENT = 1000000


def set_ema_long_period(value):
    global EMA_LONG_PERIOD
    EMA_LONG_PERIOD = value


def set_ema_mid_period(value):
    global EMA_MID_PERIOD
    EMA_MID_PERIOD = value


def set_ema_short_period(value):
    global EMA_SHORT_PERIOD
    EMA_SHORT_PERIOD = value


def set_min_long_ema_trend_length(value):
    global MIN_LONG_EMA_TREND_LENGTH
    MIN_LONG_EMA_TREND_LENGTH = value


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

            # buy signals
            buy = (ema_short[-1] > ema_mid[-1]) and (ema_short[-2] < ema_mid[-2])
            buy = buy and all([ema_long[-i] > ema_long[-i-1] for i in range(1, MIN_LONG_EMA_TREND_LENGTH)])

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
            sell = ema_long[-1] < ema_long[-2]

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


if __name__ == '__main__':
    pass
