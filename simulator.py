from stocks.stock import Stock
from analysis.rsi import rsi,rsi_cross_signals
from stocks.stock_index import wig20_2019, mwig40
from wallet.wallet import Wallet
import pandas as pd



"""
TODO:
- this is only an ugly working template
- make a wrapper to simulate a strategy defined in function
- think where to keep simulation settings/config
- plot strategy performance 
"""



def calculate_investment_value(wallet, max_fraction):
    output = 0
    min_value = wallet.minimal_recommended_investment()
    if wallet.money > min_value:
        max_value = wallet.total_value / max_fraction
        output = max(max_value, min_value)
        output = min(output, wallet.money)
    return output


start_date = '2018-01-01'
end_date = '2019-12-31'
time_range = pd.date_range(start_date, end_date)

my_wallet = Wallet(commission_rate=0.0038, min_commission=3.0)
my_wallet.money = 10000

take_profit = 0.15
stop_loss = 0.01

performance = pd.DataFrame(columns=['Date', 'Wallet state'])

traded_tickers = wig20_2019
traded_tickers.update(mwig40)
stocks_data = dict()
rsi_tables = dict()

for tck in traded_tickers:
    stocks_data[tck] = Stock(tck)
    rsi_tables[tck] = rsi(stocks_data[tck].ohlc)
    rsi_tables[tck]['Buy'] = rsi_cross_signals(rsi_tables[tck], 30 , 'onrise')
    rsi_tables[tck]['Sell'] = rsi_cross_signals(rsi_tables[tck], 70, 'onrise')


stocks_to_buy = set()
stocks_to_sell = set()


for day in time_range:

    for tck in traded_tickers:
        
        if day in stocks_data[tck].ohlc.index:

            # buy selected
            if tck in stocks_to_buy:
                if not my_wallet.get_volume_of_stocks(tck):
                    price = stocks_data[tck].ohlc.loc[day, 'Open']
                    total = calculate_investment_value(my_wallet, 5)
                    volume = round(total/price)
                    if volume:
                        my_wallet.buy(tck, volume, price)
                        print(f'{day}: Buy {volume} x {tck} for {price}')
                stocks_to_buy.remove(tck)


            # sell selected
            if tck in stocks_to_sell:
                if my_wallet.get_volume_of_stocks(tck):
                    price = stocks_data[tck].ohlc.loc[day, 'Open']
                    volume = my_wallet.sell_all(tck, price)
                    print(f'{day}: Sell {volume} x {tck} for {price}')
                stocks_to_sell.remove(tck)

        
            # select stocks to buy the next day
            if rsi_tables[tck]['Buy'].get(day, None):
                stocks_to_buy.add(tck)
    
            # select stocks to sell the next day
            if rsi_tables[tck]['Sell'].get(day, None):
                stocks_to_sell.add(tck)
                # print(day, tck, 'Sell')
                # print('==========================================================')


    for tck in my_wallet.list_stocks():
        if day in stocks_data[tck].ohlc.index:
            # update prices of stocks in wallet 
            price = stocks_data[tck].ohlc.loc[day, 'Close']
            my_wallet.update_price(tck, price)

            """ take profit """
            if take_profit and my_wallet.change(tck) > take_profit:
                stocks_to_sell.add(tck)

            """ stop loss """
            if stop_loss and my_wallet.change(tck) < -stop_loss:
                stocks_to_sell.add(tck)

    performance = performance.append(
        {'Date': day, 'Wallet state': my_wallet.total_value},
        ignore_index=True
        )


print(performance)