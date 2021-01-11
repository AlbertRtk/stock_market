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


def test_for_years(strategy, traded_stock, start_year, end_year, step_year):
    gains = []

    for y in range(start_year, end_year, step_year):
        start_date = f'{y}-01-01'
        end_date = f'{y}-12-31'
        trading_days = Stock('WIG').ohlc[start_date:end_date].index
        wallet = Wallet(commission_rate=0.0038, min_commission=3.0)
        wallet.money = 10000

        my_simulator = Simulator(trading_days, traded_stock, wallet)

        result = my_simulator.run(strategy)
        result = result.tail(1)['Wallet state']
        result = float(result)

        gains.append(result-10000)

    save_test_results(gains)


def save_test_results(results):
    summary = ''
    for g in results:
        summary += f'{g}\t'
    summary += f'{sum(results)}\n'

    with open('EMAVolStrategy_optimization_SL.txt', 'a') as f:
        f.write(summary)


if __name__ == '__main__':
    print('Preparing data...')
    stocks_data = dict()
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()

    my_strategy = EmaVolStrategy()

    for sl_ in range(26, 36, 1):
        sl = sl_ / 1000
        my_strategy.stop_loss = sl

        with open('EMAVolStrategy_optimization_SL.txt', 'a') as f:
            f.write(f'{sl}\t')

        test_for_years(my_strategy, stocks_data, 2015, 2020, 1)
