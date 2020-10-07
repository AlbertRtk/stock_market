import pandas as pd


def rsi(prices, alpha=1/14):
    """
    Clculates Relative Strength Index (RSI).

    :prices: pandas.DataFrame with 'Close' column containing closing prices of stock
    :alpha: smoothing factor, 0 < alpha <= 1
    :return: pandas.Series with calculated RSI
    """
    price_now = prices['Close']
    price_prev = prices['Close'].shift(periods=1, fill_value=0)  # assign to each day price from the previous day

    price_changes = pd.DataFrame(columns=['Up', 'Down'])
    price_changes['Up'] = price_now - price_prev  # upward changes
    price_changes['Down'] = price_prev - price_now  # downward changes
    price_changes[price_changes < 0] = 0

    smma = price_changes.ewm(alpha = alpha, adjust=False).mean()  # smoothed moving averages
    rs = smma['Up'] / smma['Down']

    output_rsi = -100 / (rs+1)
    output_rsi = output_rsi + 100
    
    output_rsi = output_rsi.rename('RSI')
    output_rsi = output_rsi.to_frame()

    return output_rsi
