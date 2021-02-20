from marketools import Stock
from config import *
from datetime import datetime


def update_wallet_row(wallet_wks, row_idx, share):
    wallet_wks.update_cell(row_idx, WALLET_PRICES_COL, share.last_ohlc['Close'])
    wallet_wks.update_cell(row_idx, WALLET_PBV_COL, share.pbv)
    wallet_wks.update_cell(row_idx, WALLET_EPS_COL, share.eps)
    wallet_wks.update_cell(row_idx, WALLET_PE_COL, share.pe)
    wallet_wks.update_cell(row_idx, WALLET_DIVIDEND_YIELD_COL, share.dividend_yield)
    wallet_wks.update_cell(row_idx, WALLET_VOLUME_MEAN_LONG, round(share.mean_volume(90), 1))
    wallet_wks.update_cell(row_idx, WALLET_VOLUME_MEAN_SHORT, round(share.mean_volume(5), 1))
    wallet_wks.update_cell(row_idx, WALLET_VOLUME, share.volume)
    wallet_wks.update_cell(row_idx, WALLET_PLOT_LINK_COL, share.stooq_plot_link)


def update_wallet(wallet_wks):
    """ Updates prices and info for shares in wallet. """
    """ Get wallet content """
    wallet_tickers_list = wallet_wks.col_values(TICKERS_COL)[FIRST_DATA_ROW - 1::]
    wallet_shares = {s: Stock(s) for s in wallet_tickers_list}

    """ UPDATE WALLET WORKSHEET """
    print('\nPrices of shares in wallet:')
    time_now = datetime.now()
    str_today = time_now.strftime('%Y-%m-%d')
    wallet_wks.update_acell(UPDATE_TIME_ACELL, time_now.strftime('%Y-%m-%d, %H:%M'))
    for i, tck in enumerate(wallet_tickers_list, FIRST_DATA_ROW):
        share = wallet_shares[tck]
        price_date = share.last_ohlc.name.strftime('%Y-%m-%d')
        message = f'{tck}:\t\t{share.last_ohlc["Close"]} PLN'
        if price_date != str_today:
            message += f'\t\tWARNING! Today is {str_today}, last price from {price_date}.'
        print(message)
        update_wallet_row(wallet_wks, i, share)
