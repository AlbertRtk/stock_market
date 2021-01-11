from simulator import Simulator
from marketools import Stock, Wallet, store_data, StockQuotes
from stock_index import wig20_2019, mwig40
from tqdm import tqdm

from strategies import EmaVolStrategy


StockQuotes.check_for_update = False
store_data()

# === SIMULATOR CONFIG =========================================================
TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
# ==============================================================================


if __name__ == '__main__':
    print('Preparing data...')
    stocks_data = dict()
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()

    gain_in_year = []

    for y in range(2015, 2020, 1):
        start_date = f'{y}-01-01'
        end_date = f'{y}-12-31'
        trading_days = Stock('WIG').ohlc[start_date:end_date].index
        wallet = Wallet(commission_rate=0.0038, min_commission=3.0)
        wallet.money = 10000

        my_simulator = Simulator(trading_days, stocks_data, wallet)
        my_strategy = EmaVolStrategy()

        my_simulator.reset()
        result = my_simulator.run(my_strategy)
        result = result.tail(1)['Wallet state']
        result = float(result)

        gain_in_year.append(result-10000)

    summary = ''
    for g in gain_in_year:
        summary += f'{g}\t'
    summary += f'{sum(gain_in_year)}'

    with open('strategy_optimization.txt', 'a') as f:
        f.write(summary)
