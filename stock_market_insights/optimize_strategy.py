from simulator import Simulator
from marketools import Stock, Wallet, store_data, StockQuotes
from stock_index import wig20_2019, mwig40
from tqdm import tqdm

from strategies import EmaVolStrategy


StockQuotes.check_for_update = False
store_data()

# === SIMULATOR CONFIG =========================================================
START_DATE = '2015-01-01'  # '2015-01-01'
END_DATE = '2019-12-31'  # '2019-12-31'
TRADING_DAYS = Stock('WIG').ohlc[START_DATE:END_DATE].index
MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
MY_WALLET.money = 10000
TRADED_TICKERS = wig20_2019
TRADED_TICKERS.update(mwig40)
# ==============================================================================


if __name__ == '__main__':
    print('Preparing data...')
    # wig = Stock('WIG')
    stocks_data = dict()
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()

    my_simulator = Simulator(TRADING_DAYS, stocks_data, MY_WALLET, show_plot=False)
    my_strategy = EmaVolStrategy()

    for l_win in range(70, 91, 5):

        for _vol_inc in range(13, 21):
            vol_inc = _vol_inc / 10

            my_strategy.vol_mean_long_window = l_win
            my_strategy.min_vol_increase_to_buy = vol_inc

            my_simulator.reset()
            result = my_simulator.run(my_strategy).tail(1)['Wallet state']
            result = float(result)
            summary = f'{l_win}\t{vol_inc}\t{result}\n'

            with open('strategy_optimization.txt', 'a') as f:
                f.write(summary)
