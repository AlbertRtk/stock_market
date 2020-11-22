from stocks.stock import Stock
from analysis.volume import mean_volume_on_date
from stocks.stock_index import wig20_2019, mwig40
from tqdm import tqdm
from datetime import date


# === CONFIG ===================================================================
DAY = date.today()
TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
VOLUME_INCREASE_FACTOR = 3.3
MAX_PRICE_CHANGE = 0
MIN_WIG_CHANGE = 0
# ==============================================================================


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
    
    wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > MIN_WIG_CHANGE

    if wig_increased:

        for tck in traded_stocks:
            tck_ohlc = traded_stocks[tck].ohlc

            if tck_ohlc['Volume'].get(day, None):
                mean_volume = mean_volume_on_date(tck_ohlc, day)
                day_volume = tck_ohlc.loc[day, 'Volume']
                price_change = tck_ohlc.loc[day, 'Close'] - tck_ohlc.loc[day, 'Open']

                price_decreased = price_change < MAX_PRICE_CHANGE
                volume_increased = (day_volume/mean_volume) > VOLUME_INCREASE_FACTOR
                
                if price_decreased and volume_increased:
                    selected_stock[tck] = day_volume/mean_volume

    for tck, _ in sorted(selected_stock.items(), key=lambda item: item[1], reverse=False):
        stocks_to_buy.append(tck)
                
    return stocks_to_buy, stocks_to_sell

# ==============================================================================


# call startegy   
buy, sell = my_strategy(wig, traded_stocks=stocks_data, day=DAY)
print('Buy:', buy)
