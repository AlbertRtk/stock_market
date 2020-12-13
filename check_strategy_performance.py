from marketools import Stock
from marketools.wallet import Wallet
from marketools import simulator

from stock_index import wig20_2019, mwig40
from daily_analysis import my_strategy
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


# === SIMULATOR CONFIG =========================================================
START_DATE = '2014-01-01'
END_DATE = '2020-10-31'
TRADING_DAYS = Stock('WIG').ohlc[START_DATE:END_DATE].index

MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
MY_WALLET.money = 10000

MAX_POSITIONS = 5
TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
ACTIVE_TRADING = False

TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
# ==============================================================================


print('Preparing data...')
stocks_data = dict()
wig = Stock('WIG')
for tck in tqdm(TRADED_TICKERS):
    stocks_data[tck] = Stock(tck)
print()


# === STRATEGY DEFINITION ======================================================

@simulator(TRADING_DAYS, stocks_data, MY_WALLET, MAX_POSITIONS, TAKE_PROFIT, STOP_LOSS, ACTIVE_TRADING)
def strategy(wig, *args, **kwargs):
    return my_strategy(wig, *args, **kwargs)

# ==============================================================================


# call startegy   
result = strategy(wig)
print('\n', result.tail(1))
plt.plot(result['Date'], result['Wallet state'])
plt.show()
