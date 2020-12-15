from marketools import Stock
from marketools.analysis import mean_volume_on_date
from marketools.analysis import relative_price_change, price_change
from stock_index import wig20_2019, mwig40
from tqdm import tqdm
from datetime import date


# === STRATEGY DEFINITION ======================================================

MIN_VOLUME_INCREASE_FACTOR_TO_BUY = 3.3
MAX_RELATIVE_PRICE_CHANGE_TO_BUY = 0
MIN_WIG_CHANGE_TO_BUY = 0
MAX_RELATIVE_PRICE_DROP_TO_KEEP = 0.055


def my_strategy(wig, *args, **kwargs):
    day = str(kwargs['day'])
    traded_stocks = kwargs['traded_stocks']
    selected_stocks = dict()
    stocks_to_buy = []
    stocks_to_sell = []

    if str(date.today()) == day:
        wig_increased = (wig.last - wig.open) > MIN_WIG_CHANGE_TO_BUY
    else:
        wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > MIN_WIG_CHANGE_TO_BUY

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc
        data_exists = tck_ohlc['Close'].get(day, None)

        if data_exists:
            # calculate indicators
            mean_volume_long = mean_volume_on_date(tck_ohlc, day, window=90)
            day_volume = tck_ohlc.loc[day, 'Volume']
            day_price_change = relative_price_change(tck_ohlc.loc[day, 'Close'], tck_ohlc.loc[day, 'Open'])

            # look for buy signals
            if wig_increased and data_exists:
                price_change_to_buy_ok = day_price_change < MAX_RELATIVE_PRICE_CHANGE_TO_BUY
                day_volume_increased = (day_volume/mean_volume_long) > MIN_VOLUME_INCREASE_FACTOR_TO_BUY

                if price_change_to_buy_ok and day_volume_increased:
                    # buy!
                    selected_stocks[tck] = day_volume/mean_volume_long

            # look for sell signals
            if day_price_change < -MAX_RELATIVE_PRICE_DROP_TO_KEEP:
                if tck not in selected_stocks:
                    # sell!
                    stocks_to_sell.append(tck)

    # sort stocks to buy - lower volume increase first
    for tck, _ in sorted(selected_stocks.items(), key=lambda item: item[1], reverse=False):
        stocks_to_buy.append(tck)

    return stocks_to_buy, stocks_to_sell


# ==============================================================================

if __name__ == '__main__':
    DAY = date.today()
    TRADED_TICKERS = wig20_2019
    TRADED_TICKERS.update(mwig40)

    # temp update with Allegro
    TRADED_TICKERS['ALE'] = 'Allegro'

    print('Preparing data...')
    stocks_data = dict()
    wig = Stock('WIG')
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()
    
    # call startegy   
    buy, sell = my_strategy(wig, traded_stocks=stocks_data, day=DAY)
    print('Buy:  ', buy)
    print('Sell: ', sell)
