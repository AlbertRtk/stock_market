"""


"""

from stock_market_insights.analysis.heikinashi import heikinashi
from marketools.analysis import ema, rsi, rsi_cross_signals
import math


TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000


HA_HEIKINASHI = dict()
HA_EMA = dict()


def ha_init(traded_stocks):
    global HA_HEIKINASHI
    if not HA_HEIKINASHI:
        for tck in traded_stocks:
            HA_HEIKINASHI[tck] = heikinashi(traded_stocks[tck].ohlc)

    global HA_EMA
    if not HA_EMA:
        for tck in traded_stocks:
            HA_EMA[tck] = ema(HA_HEIKINASHI[tck], window=5)


def heikinashi_strategy(day, wallet, traded_stocks, wig, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    ha_init(traded_stocks)

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price:
            tck_ha = HA_HEIKINASHI[tck][:day].tail(3)
            tck_ema = HA_EMA[tck][:day].tail(3)

            if tck_ha['Open'].get(day, None):

                long_positive_candle = (tck_ha['Open'].get(day) == tck_ha['Low'].get(day)) \
                    and (tck_ha['Close'].get(day) >= 1.07*tck_ha['Open'].get(day))

                close_above_ema = tck_ha['Close'].get(day) > tck_ema.get(day)

                before_close_below_ema = any((tck_ha['Close'] - tck_ema) < 0)

                negative_candles = all((tck_ha['Close'] - tck_ha['Open']) < 0)


                if long_positive_candle and close_above_ema and before_close_below_ema:
                    if not wallet.get_volume_of_stocks(tck):
                        # buy!
                        invest = wallet.total_value / MAX_POSITIONS
                        invest = max(invest, MIN_INVESTMENT)
                        invest = min(invest, MAX_INVESTMENT)
                        invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                        volume_to_buy = math.floor(invest / close_price)
                        stocks_to_buy[tck] = (volume_to_buy, None)
                elif negative_candles:
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
