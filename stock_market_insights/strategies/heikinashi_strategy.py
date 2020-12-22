"""


"""

import math
from datetime import timedelta


TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000

LONG_BULL_CANDLE_CLOSE_OPEN_RATIO = 1.05
LONG_BEAR_CANDLE_OPEN_CLOSE_RATIO = 1.03
BEAR_CANDLE_OPEN_CLOSE_RATIO = 1.02
MAX_CHANGE_SHORT_CANDLE = 0.02
MAX_CHANGE_DOJI = 0.005
MIN_DOJI_LEG_BODY_RATIO = 3


HA_HEIKINASHI = dict()


def ha_init(traded_stocks):
    global HA_HEIKINASHI
    if not HA_HEIKINASHI:
        for tck in traded_stocks:
            print(f'Heikin-Ashi for {tck}')
            HA_HEIKINASHI[tck] = traded_stocks[tck].heikinashi()


def is_long_bullish_candle(ohlc, day):
    if day in ohlc.index:
        output = ohlc['Open'].get(day) == ohlc['Low'].get(day)
        output = output and (ohlc['Close'].get(day) >= LONG_BULL_CANDLE_CLOSE_OPEN_RATIO * ohlc['Open'].get(day))
    else:
        output = False
    return output


def is_long_bearish_candle(ohlc, day):
    if day in ohlc.index:
        output = ohlc['Open'].get(day) == ohlc['High'].get(day)
        output = output and ohlc['Open'].get(day) >= LONG_BEAR_CANDLE_OPEN_CLOSE_RATIO * ohlc['Close'].get(day)
    else:
        output = False
    return output


def is_bearish_candle(ohlc, day):
    if day in ohlc.index:
        output = ohlc['Open'].get(day) >= BEAR_CANDLE_OPEN_CLOSE_RATIO * ohlc['Close'].get(day)
    else:
        output = False
    return output


def is_close_increasing_last_three_days(ohlc, day):
    if day in ohlc.index:
        _ohlc = ohlc[:day].tail(3)
        output = _ohlc['Close'][0] < _ohlc['Close'][1] < _ohlc['Close'][2]
    else:
        output = False
    return output


def is_short_candle(ohlc, day):
    if day in ohlc.index:
        change = ohlc['Close'].get(day) - ohlc['Open'].get(day)
        change = change / ohlc['Open'].get(day)
        change = abs(change)
        output = change <= MAX_CHANGE_SHORT_CANDLE
    else:
        output = False
    return output


def is_doji_day_before(ohlc, day):
    if day in ohlc.index:
        _ohlc = ohlc[:day].tail(2)
        body_change = _ohlc['Close'][0] - _ohlc['Open'][0]
        body_change = abs(body_change)
        bottom_leg = min(_ohlc['Open'][0], _ohlc['Close'][0]) - _ohlc['Low'][0]
        top_leg = _ohlc['High'][0] - max(_ohlc['Open'][0], _ohlc['Close'][0])
        change = body_change / _ohlc['Open'][0]

        long_legs = (bottom_leg >= MIN_DOJI_LEG_BODY_RATIO * body_change) \
            and top_leg >= MIN_DOJI_LEG_BODY_RATIO * body_change

        output = long_legs and (change <= MAX_CHANGE_DOJI)
    else:
        output = False
    return output


def heikinashi_strategy(day, wallet, traded_stocks, wig, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    ha_init(traded_stocks)

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price:
            tck_ha = HA_HEIKINASHI[tck][:day]

            if tck_ha['Open'].get(day, None):

                buy_signal = \
                    is_long_bullish_candle(tck_ha, day) \
                    and is_short_candle(tck_ha, day-timedelta(days=1)) \
                    and is_long_bearish_candle(tck_ha, day-timedelta(days=2)) \
                    and is_close_increasing_last_three_days(tck_ha, day)

                sell_signal = \
                    is_bearish_candle(tck_ha, day) \
                    and is_doji_day_before(tck_ha, day)

                if buy_signal:
                    if not wallet.get_volume_of_stocks(tck):
                        # buy!
                        invest = wallet.total_value / MAX_POSITIONS
                        invest = max(invest, MIN_INVESTMENT)
                        invest = min(invest, MAX_INVESTMENT)
                        invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                        volume_to_buy = math.floor(invest / close_price)
                        stocks_to_buy[tck] = (volume_to_buy, None)
                elif sell_signal:
                    if tck in wallet.list_stocks():
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
