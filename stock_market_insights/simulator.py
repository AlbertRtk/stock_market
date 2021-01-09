import sys; sys.path.insert(0, 'marketools')
import pandas as pd
import matplotlib.pyplot as plt
from marketools import Wallet


def print_red(skk):
    print("\033[91m{}\033[00m" .format(skk))


def print_green(skk):
    print("\033[92m{}\033[00m" .format(skk))


def determine_print_color_from_prices(change):
    print_color = print_green if change > 0 else print_red
    return print_color


def info_str(day, action, ticker, volume, price, change=None):
    output = f'{day}: {action:<{2}} {ticker} \t {volume:>{4}} \t for {round(price, 2):<{7}}'
    if change:
        output += f' \t {round(100*change, 1):>{5}}%'
    return output


class Simulator:
    """
    Simulator for stock market strategies.

    Attributes
    ----------
    time_range : pandas.DatetimeIndex
        an array with trading days only (no Saturdays, Sundays, holidays)
    traded_stocks_data : dict
        a dictionary with stocks.stock.Stock instances
    wallet : marketools.Wallet
        Wallet for trading
    auto_trading : boolean
        if True selling immediately when stop loss / take profit is reached is
        simulated
    take_profit : float
        if the price of a stock increases by this fraction, it will be sold
    stop_loss : float
        if the price of a stock decreases by this fraction (comparing to the
        purchase price), it will be sold
    show_plot : boolean
        if True, shows animated plot with wallet total value over time during
        simulation (default False)
    """

    def __init__(self,
                 time_range: pd.DatetimeIndex,
                 traded_stocks_data: dict,
                 wallet: Wallet,
                 auto_trading: bool = False,
                 take_profit: float = 0.0,
                 stop_loss: float = 0.0,
                 show_plot: bool = False):

        self.time_range = time_range
        self.traded_stocks_data = traded_stocks_data
        self.wallet = wallet
        self.wallet_init_value = wallet.total_value
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.auto_trading = auto_trading
        self.wallet_history = pd.DataFrame(columns=['Date', 'Wallet state'])
        self.show_plot = show_plot
        self.__plot_ref_lines = dict()
        self.__simulated_year_now = None

    def reset(self) -> None:
        """
        Resets the value of wallet to initial value, and removes all stocks from
        the wallet and its history.
        """
        self.wallet = Wallet(self.wallet.rate, self.wallet.minimum)
        self.wallet.money = self.wallet_init_value
        self.wallet_history = pd.DataFrame(columns=['Date', 'Wallet state'])

    def run(self, strategy_function, *args, **kwargs) -> pd.DataFrame:
        """
        Runs the simulation for given strategy and returns DataFrame with
        wallet value for each day in given time range.

        Parameters
        ----------
        strategy_function : func
            Function with investment strategy. Must take dictionary with traded
            stocks data (self.traded_stocks_data) and date as inputs. Must
            return set of lists (stocks_to_buy, stocks_to_sell).
        kwargs
            Other inputs to investment strategy (strategy_function).

        Returns
        -------
        pandas.DataFrame
        """

        stocks_to_buy = dict()
        stocks_to_sell = dict()

        for day in self.time_range:

            # save reference wallet values for plot hlines
            if self.show_plot and (self.__simulated_year_now != day.year):
                self.__simulated_year_now = day.year
                self.__plot_ref_lines[day] = self.wallet.total_value

            # Buy selected day before. Loop over list, order can be important
            # here. Strategy can sort relevant stocks - high priority first.
            self.__buy_selected_stocks(day, stocks_to_buy)

            # Sell selected day before. List to set, we don't care here about
            # the order. Set will remove duplicates.
            self.__sell_selected_stocks(day, stocks_to_sell)

            # if auto trading is active, check if price of any stock in the
            # wallet crossed take profit or stop loss price; if yes then sell it
            # immediately
            if self.auto_trading:
                self.__auto_trading_tp_sl(day)

            # update the price to the close price
            self.__update_wallet_stock_prices_to_close(day)

            # save history of the wallet
            self.wallet_history = self.wallet_history.append(
                {'Date': day, 'Wallet state': self.wallet.total_value},
                ignore_index=True)

            # call strategy function
            stocks_to_buy, stocks_to_sell = strategy_function(
                day=day,
                wallet=self.wallet,
                traded_stocks=self.traded_stocks_data,
                *args, **kwargs)

            # show animated plot
            if self.show_plot:
                self.__plot_wallet_total_value()

        if self.show_plot:
            plt.show()

        return self.wallet_history

    def __buy_selected_stocks(self, day, stocks_to_buy):
        """
        Buys stocks from the list.

        Parameters
        ----------
        day : datetime.date
            date
        stocks_to_buy : dict
            dict with tickers of stocks to buy; keys - tickers, values - sets
            (volume_to_buy, price_limit), if price_limit is None the stock will
            be purchased with open price

        Returns
        -------
        None
        """
        for tck, buy in stocks_to_buy.items():
            open_price = self.traded_stocks_data[tck].ohlc['Open'].get(day, None)
            low_price = self.traded_stocks_data[tck].ohlc['Low'].get(day, None)

            volume = buy[0]
            price_limit = buy[1]

            if price_limit:
                use_open_price = open_price < price_limit
            else:
                # no price_limit - buy for any price
                use_open_price = True

            if open_price and use_open_price:
                price = open_price
            elif low_price and (low_price < price_limit):
                price = price_limit
            else:
                price = None

            if price and (volume > 0):
                value = price * volume
                value += self.wallet.commission(value)
                if self.wallet.money > value:
                    print(info_str(day.strftime('%Y-%m-%d'), 'B', tck, volume, price))
                    self.wallet.buy(tck, volume, price)

    def __sell_selected_stocks(self, day, stocks_to_sell):
        """
        Sells stocks from the list.

        Parameters
        ----------
        day : datetime.date
            date
        stocks_to_sell : dict
            dict with tickers of stocks to sell; keys - tickers, values - sets
            (volume_to_sell, price_limit), if price_limit is None the stock will
            be sold with open price

        Returns
        -------
        None
        """
        for tck, sell in stocks_to_sell.items():
            if self.wallet.get_volume_of_stocks(tck):
                open_price = self.traded_stocks_data[tck].ohlc['Open'].get(day, None)
                high_price = self.traded_stocks_data[tck].ohlc['Open'].get(day, None)

                volume = sell[0]
                price_limit = sell[1]

                if price_limit:
                    use_open_price = open_price > price_limit
                else:
                    # no price_limit - sell for any price
                    use_open_price = True

                if open_price and use_open_price:
                    price = open_price
                elif high_price and (high_price > price_limit):
                    price = price_limit
                else:
                    price = None

                if price and (volume > 0):
                    print_color = determine_print_color_from_prices(
                        self.wallet.change(tck))
                    print_color(info_str(day.strftime('%Y-%m-%d'),
                                         'S',
                                         tck,
                                         volume,
                                         price,
                                         self.wallet.change(tck)))
                    self.wallet.sell(tck, volume, price)

    def __update_wallet_stock_prices_to_close(self, day):
        """
        Updates prices of stocks in the wallet to close price from given day.

        Parameters
        ----------
        day : str
            string with date (yyyy-mm-dd)

        Returns
        -------
        None
        """
        for tck in self.wallet.list_stocks():
            ohlc = self.traded_stocks_data[tck].ohlc
            price = ohlc['Close'].get(day, None)
            if price:
                self.wallet.update_price(tck, price)

    def __plot_wallet_total_value(self):
        """
        Shows animated plot of wallet total value over time during simulation.
        """
        plt.clf()
        for day, ref in self.__plot_ref_lines.items():
            plt.hlines(ref,
                       day,
                       self.time_range[-1],
                       colors='r')
        plt.plot(self.wallet_history['Date'], self.wallet_history['Wallet state'])
        plt.xlim([self.time_range[0], self.time_range[-1]])
        plt.title(f'Wallet total value: {round(self.wallet.total_value, 2)}')
        plt.grid()
        plt.pause(1e-15)

    def __auto_trading_tp_sl(self, day):
        """
        Take profit and stop loss.

        Parameters
        ----------
        day : datetime.date
            date

        Returns
        -------
        None
        """
        for tck in self.wallet.list_stocks().copy():
            price_max = self.traded_stocks_data[tck].ohlc['High'] \
                .get(day, None)

            if price_max:
                self.wallet.update_price(tck, price_max)

            if self.wallet.change(tck) > self.take_profit:
                # selling it immediately
                price = self.wallet.get_purchase_price_of_stocks(tck) \
                        * (1 + self.take_profit)
                price = round(price, 2)
                volume = self.wallet.sell_all(tck, price)
                print_green(info_str(day.strftime('%Y-%m-%d'), 'TP', tck, volume, price))
                continue

            price_min = self.traded_stocks_data[tck].ohlc['Low'] \
                .get(day, None)

            if price_min:
                self.wallet.update_price(tck, price_min)

            if self.wallet.change(tck) < -self.stop_loss:
                # selling it immediately
                price = self.wallet.get_purchase_price_of_stocks(tck) \
                        * (1 - self.stop_loss)
                price = round(price, 2)
                volume = self.wallet.sell_all(tck, price)
                print_red(info_str(day.strftime('%Y-%m-%d'), 'SL', tck, volume, price))


if __name__ == '__main__':
    pass
