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
START_DATE = '2014-01-01'
END_DATE = '2020-10-31'
TRAIDING_DAYS = Stock('WIG').ohlc[START_DATE:END_DATE].index
MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
MY_WALLET.money = 10000
MAX_POSITIONS = 3
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
print()


# === STRATEGY DEFINITIONS =====================================================

@simulator(TRAIDING_DAYS, stocks_data, MY_WALLET, MAX_POSITIONS, TAKE_PROFIT, STOP_LOSS, ACTIVE_TRAIDING)
def rsi_growing_trend_strategy(rsi_tables, *args, **kwargs):
    day = kwargs['day']
    traded_stocks = kwargs['traded_stocks']
    stocks_to_buy = []
    stocks_to_sell = []
    
    for tck in rsi_tables:
    
        if rsi_tables[tck]['Buy'].get(day, None):
            ohlc_before = traded_stocks[tck].ohlc[:day].tail(180).reset_index()
            trend, *_ = stats.linregress(ohlc_before.index, ohlc_before['Close'])
            if trend > 0.2:
                stocks_to_buy.append(tck)
    
        if rsi_tables[tck]['Sell'].get(day, None):
            stocks_to_sell.append(tck)
    
    return stocks_to_buy, stocks_to_sell


@simulator(TRAIDING_DAYS, stocks_data, MY_WALLET, MAX_POSITIONS, TAKE_PROFIT, STOP_LOSS, ACTIVE_TRAIDING)
def high_volume_strategy(*args, **kwargs):
    day = kwargs['day']
    traded_stocks = kwargs['traded_stocks']
    stocks_to_buy = []
    stocks_to_sell = []
    
    for tck in traded_stocks:
        if traded_stocks[tck].ohlc['Volume'].get(day, None):
            mean_volume = mean_volume_on_date(traded_stocks[tck].ohlc, day)
            day_volume = traded_stocks[tck].ohlc.loc[day, 'Volume']
            
            if (day_volume/mean_volume) > 4:
                stocks_to_buy.append(tck)
    
    return stocks_to_buy, stocks_to_sell

# ==============================================================================


# call startegy
result = high_volume_strategy()

print('\n', result.tail(1))
plt.plot(result['Date'], result['Wallet state'])
plt.show()
