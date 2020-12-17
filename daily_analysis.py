from marketools import Stock
from marketools.analysis import mean_volume_on_date, price_change
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
    selected_stocks_to_buy = dict()
    stocks_to_buy = []
    stocks_to_sell = []

    if str(date.today()) == day:
        wig_increased = (wig.last - wig.open) > MIN_WIG_CHANGE_TO_BUY
    else:
        wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > MIN_WIG_CHANGE_TO_BUY

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        data_exists = tck_ohlc['Close'].get(day, None)

        if data_exists:
            # calculate indicators
            mean_volume_long = mean_volume_on_date(tck_ohlc, day, window=90)
            day_volume = tck_ohlc.loc[day, 'Volume']
            day_price_change = price_change(tck_ohlc.tail(1), shift=0, relative=True)[day]
            # mid_price_change = price_change(tck_ohlc.tail(6), shift=5, relative=True)[day]

            # look for buy signals
            if wig_increased:
                price_change_buy = day_price_change < MAX_RELATIVE_PRICE_CHANGE_TO_BUY
                day_volume_increased = (day_volume/mean_volume_long) > MIN_VOLUME_INCREASE_FACTOR_TO_BUY

                if price_change_buy and day_volume_increased:
                    # buy!
                    selected_stocks_to_buy[tck] = day_volume/mean_volume_long

            # look for sell signals
            price_change_sell = day_price_change < -MAX_RELATIVE_PRICE_DROP_TO_KEEP

            if price_change_sell:
                if tck not in selected_stocks_to_buy:
                    # sell!
                    stocks_to_sell.append(tck)

    # sort stocks to buy - lower volume increase first
    for tck, _ in sorted(selected_stocks_to_buy.items(), key=lambda item: item[1], reverse=False):
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
