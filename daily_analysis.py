from stocks.stock import Stock
from analysis.volume import mean_volume_on_date
from stocks.stock_index import wig20_2019, mwig40
from tqdm import tqdm
from datetime import date


# === CONFIG ===================================================================
DAY = date.today()
TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
MIN_VOLUME_INCREASE_FACTOR_TO_BUY = 3.3
MAX_PRICE_CHANGE_TO_BUY = 0
MIN_WIG_CHANGE_TO_BUY = 0
MAX_RELATIVE_PRICE_DROP_TO_KEEP = 0.055
# ==============================================================================

# temp update with Allegro
TRADED_TICKERS['ALE'] = 'Allegro'

print('Preparing data...')
stocks_data = dict()
wig = Stock('WIG')
for tck in tqdm(TRADED_TICKERS):
    stocks_data[tck] = Stock(tck)
print()


# === STRATEGY DEFINITION ======================================================

def my_strategy(wig, *args, **kwargs):
    day = kwargs['day']
    traded_stocks = kwargs['traded_stocks']
    selected_stock = dict()
    stocks_to_buy = []
    stocks_to_sell = []

    # --- look for buy signals ---

    wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > MIN_WIG_CHANGE_TO_BUY

    if wig_increased:

        for tck in traded_stocks:
            tck_ohlc = traded_stocks[tck].ohlc

            if tck_ohlc['Volume'].get(day, None):
                mean_volume = mean_volume_on_date(tck_ohlc, day)
                day_volume = tck_ohlc.loc[day, 'Volume']
                price_change = tck_ohlc.loc[day, 'Close'] - tck_ohlc.loc[day, 'Open']

                price_decreased = price_change < MAX_PRICE_CHANGE_TO_BUY
                volume_increased = (day_volume/mean_volume) > MIN_VOLUME_INCREASE_FACTOR_TO_BUY
                
                if price_decreased and volume_increased:
                    selected_stock[tck] = day_volume/mean_volume

    for tck, _ in sorted(selected_stock.items(), key=lambda item: item[1], reverse=False):
        stocks_to_buy.append(tck)

    # --- look for sell signals ---

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc

        if tck_ohlc['Close'].get(day, None):
            relativ_price_change = (tck_ohlc.loc[day, 'Close'] - tck_ohlc.loc[day, 'Open']) / tck_ohlc.loc[day, 'Open']
        else:
            relativ_price_change = 0

        if relativ_price_change < -MAX_RELATIVE_PRICE_DROP_TO_KEEP:
            if tck not in stocks_to_buy:
                stocks_to_sell.append(tck)

    return stocks_to_buy, stocks_to_sell


# ==============================================================================


# call startegy   
buy, sell = my_strategy(wig, traded_stocks=stocks_data, day=DAY)
print('Buy:  ', buy)
print('Sell: ', sell)
