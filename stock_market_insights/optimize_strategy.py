from simulator import Simulator
from marketools import Stock, Wallet, store_data
from stock_market_insights.stock_index import wig20_2019, mwig40
from tqdm import tqdm


from stock_market_insights.strategies import ema_strategy as my_strategy
from stock_market_insights.strategies.ema_strategy import *

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
    store_data()
    print('Preparing data...')
    wig = Stock('WIG')
    stocks_data = dict()
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()

    my_simulator = Simulator(TRADING_DAYS, stocks_data, MY_WALLET, show_plot=False)

    for i_mid in range(12, 15, 1):
        set_ema_mid_period(i_mid)

        for i_short in range(5, 8, 1):
            set_ema_short_period(i_short)

            my_simulator.reset()
            result = my_simulator.run(my_strategy).tail(1)['Wallet state']
            result = float(result)
            summary = f'180\t{i_mid}\t{i_short}\t{result}\n'

            with open('strategy_optimization.txt', 'a') as f:
                f.write(summary)
