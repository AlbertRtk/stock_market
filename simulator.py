import pandas as pd


def __calculate_investment_value(wallet, max_fraction):
    output = 0
    min_value = wallet.minimal_recommended_investment()
    if wallet.money > min_value:
        max_value = wallet.total_value / max_fraction
        output = max(max_value, min_value)
        output = min(output, wallet.money)
    return output


def simulator(time_range, traded_stocks, wallet, take_profit, stop_loss):
    """
    This function returns decorator for a stock market strategy.

    :param time_range:
    :param traded_stocks:
    :param wallet:
    :param take_profit:
    :param stop_loss:
    :return: 
    """

    def strategy_wrapper(func):

        def simulation(*args, **kwargs):
            wallet_history = pd.DataFrame(columns=['Date', 'Wallet state'])
            stocks_to_buy = []
            stocks_to_sell = []

            for day in time_range:
                # Buy selected. Loop over list, order can be important here.
                # Strategy can sort relevant stocks - high priority first.
                for tck in stocks_to_buy:
                    if not wallet.get_volume_of_stocks(tck):
                        price = traded_stocks[tck].ohlc.loc[day, 'Open']
                        total = __calculate_investment_value(wallet, 5)
                        volume = round(total/price)
                        if volume:
                            wallet.buy(tck, volume, price)
                            print(f'{day}: Buy {volume} {tck} for {price}')

                # Sell selected. List to set, we dont care here about the order.
                # Set will remove duplcates.
                for tck in set(stocks_to_sell):
                    if wallet.get_volume_of_stocks(tck):
                        price = traded_stocks[tck].ohlc.loc[day, 'Open']
                        volume = wallet.sell_all(tck, price)
                        print(f'{day}: Sell {volume} {tck} for {price}')

                # call decorated function - strategy function
                stocks_to_buy, stocks_to_sell = func(day=day, *args, **kwargs)
            
                # update prices of stocks in wallet and take profit / stop loss
                for tck in wallet.list_stocks():
                    price = traded_stocks[tck].ohlc.loc[day, 'Close']
                    wallet.update_price(tck, price)

                    """ take profit """
                    if take_profit and wallet.change(tck) > take_profit:
                        stocks_to_sell.append(tck)

                    """ stop loss """
                    if stop_loss and wallet.change(tck) < -stop_loss:
                        stocks_to_sell.append(tck)

                # save history of the wallet
                wallet_history = wallet_history.append(
                    {'Date': day, 'Wallet state': wallet.total_value},
                    ignore_index=True
                    )
            
            return wallet_history

        return simulation

    return strategy_wrapper


if None:
    """
    This code should not be called - this is just a template function for tested strategy.
    """
    @simulator(TRAIDING_DAYS, stocks_data, MY_WALLET, TAKE_PROFIT, STOP_LOSS)
    def __strategy_template(arguments, *args, **kwargs):
        """
        :param arguments: any arguments needed for the strategy can be passed
        """
        day = kwargs['day']  # argument passed by decorator
        stocks_to_buy = set()
        stocks_to_sell = set()

        """
        place for code that will fill in stocks_to_buy and stocks_to_sell sets with tickers
        """

        return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
