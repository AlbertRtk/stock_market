"""
Investment strategy based on analysis of volume and price change.

Buy the next day if:
* WIG increased
* Stock price decreased
* Stock volume increased compared to 90 day average
    * [volume on the day] / [average volume over last 90 days]  > 3.3
    * sorted ascending - first buy selected stocks with lower volume
      increase ratio

Sel the next day if:
* Stock is not on the list of stocks to buy and stock price decreases 5.5% in
  one day, i.e., (close - open) / open < -0.055
* Stock price drops below 97.5% of purchase price (Stop Loss 2.5%)
* Stock price increases above 190% of purchase price (Take Profit 90%)
"""

from marketools.wallet import calculate_investment_value
from marketools.analysis import mean_volume_on_date
from marketools.analysis import price_change
from datetime import date
import math


MIN_VOLUME_INCREASE_FACTOR_TO_BUY = 3.3
MAX_RELATIVE_PRICE_CHANGE_TO_BUY = 0
MIN_WIG_CHANGE_TO_BUY = 0
MAX_RELATIVE_PRICE_DROP_TO_KEEP = 0.055
TAKE_PROFIT = 0.9
STOP_LOSS = 0.02
MAX_POSITIONS = 5
MIN_INVESTMENT = 2500
MAX_INVESTMENT = 10000


def volume_strategy(day, wallet, traded_stocks, wig, *args, **kwargs):
    stocks_to_buy_volume_ratio = dict()
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    if str(date.today()) == day:
        wig_increased = (wig.last - wig.open) > MIN_WIG_CHANGE_TO_BUY
    else:
        wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > MIN_WIG_CHANGE_TO_BUY

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price:
            # calculate indicators
            mean_volume_long = mean_volume_on_date(tck_ohlc, day, window=90)
            day_volume = tck_ohlc.loc[day, 'Volume']
            day_price_change = price_change(tck_ohlc.tail(1), shift=0, relative=True)[day]

            # look for buy signals
            if wig_increased:
                price_change_buy = day_price_change < MAX_RELATIVE_PRICE_CHANGE_TO_BUY
                day_volume_increased = (day_volume/mean_volume_long) > MIN_VOLUME_INCREASE_FACTOR_TO_BUY

                if price_change_buy and day_volume_increased:
                    # buy!
                    invest = calculate_investment_value(wallet, MAX_POSITIONS)
                    invest = max(invest, MIN_INVESTMENT)
                    invest = min(invest, MAX_INVESTMENT)
                    invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                    volume_to_buy = math.floor(invest / close_price)
                    stocks_to_buy_volume_ratio[tck] = day_volume/mean_volume_long
                    stocks_to_buy[tck] = (volume_to_buy, None)

            # look for sell signals
            price_change_sell = day_price_change < -MAX_RELATIVE_PRICE_DROP_TO_KEEP

            if price_change_sell:
                if tck not in stocks_to_buy_volume_ratio:
                    # sell!
                    stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    for tck in wallet.list_stocks():
        # take profit the next day
        if wallet.change(tck) > TAKE_PROFIT:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
        # stop loss the next day - price below purchase price
        if wallet.change(tck) < -STOP_LOSS:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    # sort stocks to buy - lower volume increase first
    sorted_items = sorted(stocks_to_buy.items(),
                          key=lambda item: stocks_to_buy_volume_ratio[item[0]],
                          reverse=False)
    stocks_to_buy = dict(sorted_items)

    return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
