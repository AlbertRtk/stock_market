"""

"""

from marketools.analysis import ema
import math

EMA_LONG_PERIOD = 50
EMA_MID_PERIOD = 15
EMA_SHORT_PERIOD = 5
PRICE_OSCILLATIONS_MIN_PERIOD = 21
TAKE_PROFIT = 0.9
STOP_LOSS = 0.025
MAX_POSITIONS = 5
MIN_INVESTMENT = 1000
MAX_INVESTMENT = 1000000


def ema_strategy(day, wallet, traded_stocks, *args, **kwargs):
    stocks_to_buy = dict()
    stocks_to_sell = dict()

    for tck in traded_stocks:
        tck_ohlc = traded_stocks[tck].ohlc[:day]
        close_price = tck_ohlc['Close'].get(day, None)

        if close_price and (tck_ohlc.shape[0] >= EMA_LONG_PERIOD):
            # calculate EMAs
            ema_long = ema(ohlc=tck_ohlc, window=EMA_LONG_PERIOD)
            ema_mid = ema(ohlc=tck_ohlc, window=EMA_MID_PERIOD)
            ema_short = ema(ohlc=tck_ohlc, window=EMA_SHORT_PERIOD)

            short_gt_long = ema_short > ema_long
            short_gt_mid = ema_short > ema_mid
            mid_gt_long = ema_mid > ema_long

            recent_price_oscillations = short_gt_long.tail(PRICE_OSCILLATIONS_MIN_PERIOD+1)
            recent_price_oscillations = recent_price_oscillations.head(PRICE_OSCILLATIONS_MIN_PERIOD)
            no_price_oscillations = not any(recent_price_oscillations)

            # buy signals
            #   - short crosses long from bottom, or
            buy = short_gt_long[-1] and not short_gt_long[-2]
            # buy = buy and
            #   - short crosses mid from bottom and mid greater than long
            # TODO

            if buy and no_price_oscillations:
                if not wallet.get_volume_of_stocks(tck):
                    # buy!
                    invest = wallet.total_value / MAX_POSITIONS
                    invest = max(invest, MIN_INVESTMENT)
                    invest = min(invest, MAX_INVESTMENT)
                    invest = invest / (1 + wallet.rate)  # needs some money to pay commission
                    volume_to_buy = math.floor(invest / close_price)
                    stocks_to_buy[tck] = (volume_to_buy, None)

            # sell signals - short crosses mid from top
            sell = short_gt_mid[-2] and not short_gt_mid[-1]

            if sell and (tck in wallet.list_stocks()):
                stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    for tck in wallet.list_stocks():
        # take profit the next day
        if wallet.change(tck) > TAKE_PROFIT:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)
        # stop loss the next day - price below purchase price
        if wallet.change(tck) < -STOP_LOSS:
            stocks_to_sell[tck] = (wallet.get_volume_of_stocks(tck), None)

    return stocks_to_buy, stocks_to_sell


if __name__ == '__main__':
    pass
