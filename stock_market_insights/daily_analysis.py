import sys; sys.path.insert(0, 'marketools')
from marketools import Stock, Wallet, store_data
from stock_index import wig20_2019, mwig40
from strategies import ema_strategy
from tqdm import tqdm
from datetime import date

store_data()

if __name__ == '__main__':
    MY_WALLET = Wallet(commission_rate=0.0038, min_commission=3.0)
    MY_WALLET.money = 8500

    TRADED_TICKERS = wig20_2019
    TRADED_TICKERS.update(mwig40)
    # temp update with Allegro
    TRADED_TICKERS['ALE'] = 'Allegro'

    print('Preparing data...')
    wig_ = Stock('WIG')
    stocks_data = dict()
    for tck in tqdm(TRADED_TICKERS):
        stocks_data[tck] = Stock(tck)
    print()

    buy, sell = ema_strategy(
        day=date.today(),
        wallet=MY_WALLET,
        traded_stocks=stocks_data,
        wig=wig_)
    print('Buy:  ', buy)
    print('Sell: ', sell)
