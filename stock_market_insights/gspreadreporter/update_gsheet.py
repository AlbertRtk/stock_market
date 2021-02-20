import sys
sys.path.append("/home/albi/projects/stock_market_insights/stock_market_insights/marketools")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from marketools import Stock, store_data
from report_sheet import update_report
from wallet_sheet import update_wallet
from config import *


store_data()


def select_increased_volume_stocks_by_factor(stocks_dict: dict, long=90, factor=3.3) -> dict:
    """TODO: This function should not be part of this file."""
    selected = dict()

    for tck in stocks_dict.keys():
        stock = stocks_dict[tck]
        long_mean = stock.mean_volume(long)
        volume = stock.volume
        if (volume/long_mean) > factor:
            selected[tck] = stock

    return selected


def update_stocks_spreadsheet(spreadsheet):
    wallet = spreadsheet.worksheet(WS_WALLET)
    report = spreadsheet.worksheet(WS_REPORT)
    watched = spreadsheet.worksheet(WS_WATCHED)

    """ UPDATE WALLET WORKSHEET """
    update_wallet(wallet)

    """ GET INCREASED VOLUME STOCKS """
    stocks_to_analyse = {s: Stock(s) for s in MY_TICKERS}
    print('\nSelecting stocks for report...')
    selected_stocks = select_increased_volume_stocks_by_factor(stocks_to_analyse)
    print(f'{len(selected_stocks)} stocks selected')

    """ UPDATE ANALYSIS REPORT """
    print('Adding watched stocks...')
    watched_stocks = watched.col_values(TICKERS_COL)[FIRST_DATA_ROW - 1::]
    report_stocks = {s: Stock(s) for s in watched_stocks}
    report_stocks.update(selected_stocks)
    update_report(report, report_stocks)


if __name__ == '__main__':
    """ Get authorized connection """
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, SCOPE)
    client = gspread.authorize(creds)

    """ Open spreadsheet """
    sh = client.open_by_key(SPREADSHEET_ID)

    """ Update spreadsheet """
    update_stocks_spreadsheet(sh)
