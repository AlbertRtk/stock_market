from stocks.stock import Stock
from analysis.rsi import rsi,rsi_cross_signals
from stocks.stock_index import wig20_2019, mwig40
from wallet.wallet import Wallet
from simulator import simulator
from scipy import stats
from tqdm import tqdm


# === CONFIG ===================================================================
START_DATE = '2019-01-01'
END_DATE = '2020-10-31'
TRAIDING_DAYS = Stock('WIG').ohlc[START_DATE:END_DATE].index
MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
MY_WALLET.money = 10000
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
    rsi_tables[tck]['Buy'] = rsi_cross_signals(rsi_tables[tck], 40 , 'onrise')
    rsi_tables[tck]['Sell'] = rsi_cross_signals(rsi_tables[tck], 60, 'onrise')
print()


# === STRATEGY DEFINITION ======================================================
@simulator(TRAIDING_DAYS, stocks_data, MY_WALLET, TAKE_PROFIT, STOP_LOSS, ACTIVE_TRAIDING)
def strategy(rsi_tables, *args, **kwargs):
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


result = strategy(rsi_tables)
print('\n', result)
