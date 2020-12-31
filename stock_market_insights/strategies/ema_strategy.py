"""

"""

from marketools.wallet import calculate_investment_value
from marketools.analysis import mean_volume_on_date
from marketools.analysis import price_change
from datetime import date
import math


TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000


def volume_strategy(day, wallet, traded_stocks, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    for tck in traded_stocks:
        pass
        # calculate EMAs

        # buy signals

        # sell signals

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
