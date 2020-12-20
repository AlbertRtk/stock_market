"""


"""

from stock_market_insights.analysis.heikinashi import heikinashi
from marketools.analysis import ema
import math
from datetime import timedelta


MIN_VOLUME_INCREASE_FACTOR_TO_BUY = 3.3
MAX_RELATIVE_PRICE_CHANGE_TO_BUY = 0
MIN_WIG_CHANGE_TO_BUY = 0
MAX_RELATIVE_PRICE_DROP_TO_KEEP = 0.05
TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000


def heikinashi_strategy(day, wallet, traded_stocks, wig, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    day_before = day - timedelta(days=1)

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price:
            tck_ha = heikinashi(tck_ohlc)
            tck_ema = ema(tck_ha, window=5).tail(2)
            tck_ha_close = tck_ha['Close'].tail(2)

            day_ha = tck_ha_close[0]
            day_before_ha = tck_ha_close[1]
            day_ema = tck_ema[0]
            day_before_ema = tck_ema[1]

            if day_ha and day_before_ha and day_ema and day_before_ema:
                if (day_ha > day_ema) and (day_before_ha < day_before_ema):
                    if not wallet.get_volume_of_stocks(tck):
                        # buy!
                        invest = wallet.total_value / MAX_POSITIONS
                        invest = max(invest, MIN_INVESTMENT)
                        invest = min(invest, MAX_INVESTMENT)
                        invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                        volume_to_buy = math.floor(invest / close_price)
                        stocks_to_buy[tck] = (volume_to_buy, None)
                elif (day_ha < day_ema) and (day_before_ha > day_before_ema):
                    stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
                else:
                    pass

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
