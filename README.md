# Stock Market

The project focusing on the analysis of the stock market and the automation of the decision process for financial investing.

## Disclaimer

This is an educational project created by a hobbyist, programming, and data science enthusiast. The tool should not be used for making decisions while investing in a stock market. Investing in a stock market is always connected with a risk of loss of money and resources. The author of the project takes no responsibility for anyone's decisions, investments, and possible financial loss.

<br />

# Documentation

## stocks.stock.Stock

```class stocks.stock.Stock(ticker=None)```

Contains information about the stock with the given ticker. Utilized ```stocks.sqtscraper``` to scrap data from [stooq.com](stooq.com).

* ### stocks.stock.Stock.ohlc
    Returns pandas.DataFrame with OHLC prices.

* ### stocks.stock.Stock.last_ohlc
    Returns OHLC prices from the day of the last closed session.

* ### stocks.stock.Stock.date
    Returns the date of the last closed session.

* ### stocks.stock.Stock.price
    Returns the close price from the last closed session.

* ### stocks.stock.Stock.volume
    Returns the volume from the last closed session.

* ### stocks.stock.Stock.mean_volume(over_last=None)
    Returns mean volume from a given number of the most recent session.

* ### stocks.stock.Stock.fundamentals
    Returns the dictionary with fundamental information.

* ### stocks.stock.Stock.eps
    Returns EPS.

* ### stocks.stock.Stock.pe
    Returns P/E.

* ### stocks.stock.Stock.pbv
    Returns PBV.

* ### stocks.stock.Stock.dividend_yield
    Returns dividend yield

* ### stocks.stock.Stock.stooq_plot_link
    Returns the link to the OHLC candlestick plot on [stooq.com](stooq.com).

<br />

## stocks.stqscraper.fundamentals.Fundamentals

```class stocks.fundamentals.Fundamentals(ticker=None)```

<br />

## stocks.stqscraper.stockquotes.StockQuotes

```class stocks.stockquotes.StockQuotes(ticker=None)```

<br />
