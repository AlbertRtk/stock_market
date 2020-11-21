from stocks.stock import Stock
from analysis.rsi import rsi,rsi_cross_signals
from analysis.volume import mean_volume_on_date
from stocks.stock_index import wig20_2019, mwig40
from wallet.wallet import Wallet
from simulator import simulator
from scipy import stats
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


# === CONFIG ===================================================================
START_DATE = '2011-01-01'
END_DATE = '2020-11-20'
TRAIDING_DAYS = Stock('WIG').ohlc[START_DATE:END_DATE].index
MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
MY_WALLET.money = 10000
MAX_POSITIONS = 5
TAKE_PROFIT = 0.15
STOP_LOSS = 0.03
ACTIVE_TRAIDING = False
TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
# ==============================================================================


print('Preparing data...')
stocks_data = dict()
rsi_tables = dict()
for tck in tqdm(TRADED_TICKERS):
    stocks_data[tck] = Stock(tck)
    rsi_tables[tck] = rsi(stocks_data[tck].ohlc)
    rsi_tables[tck]['Buy'] = rsi_cross_signals(rsi_tables[tck], 30 , 'onrise')
    rsi_tables[tck]['Sell'] = rsi_cross_signals(rsi_tables[tck], 70, 'onrise')
wig = Stock('WIG')
print()


# === STRATEGY DEFINITIONS =====================================================

@simulator(TRAIDING_DAYS, stocks_data, MY_WALLET, MAX_POSITIONS, TAKE_PROFIT, STOP_LOSS, ACTIVE_TRAIDING)
def my_strategy(wig, *args, **kwargs):
    day = kwargs['day']
    traded_stocks = kwargs['traded_stocks']
    selected_stock = dict()
    stocks_to_buy = []
    stocks_to_sell = []
    
    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc
        if tck_ohlc['Volume'].get(day, None):
            mean_volume = mean_volume_on_date(tck_ohlc, day)
            day_volume = tck_ohlc.loc[day, 'Volume']
            price_change = tck_ohlc.loc[day, 'Close'] - tck_ohlc.loc[day, 'Open']

            price_decreased =  price_change < 0
            volume_increased = (day_volume/mean_volume) > 3.3
            wig_increased = (wig.ohlc.loc[day, 'Close'] - wig.ohlc.loc[day, 'Open']) > 0

            if price_decreased and volume_increased and wig_increased:
                selected_stock[tck] = day_volume/mean_volume

    for tck, _ in sorted(selected_stock.items(), key=lambda item: item[1], reverse=False):
        stocks_to_buy.append(tck)
                
    return stocks_to_buy, stocks_to_sell

# ==============================================================================


# call startegy   
result = my_strategy(wig)
print('\n', result.tail(1))
plt.plot(result['Date'], result['Wallet state'])
plt.show()
