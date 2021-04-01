import sys
sys.path.append("../marketools")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from marketools import Stock, store_data
from marketools.analysis import select_stocks_with_increased_volume
from report_sheet import update_report


SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
GOOGLE_CREDS = r'/home/albi/projects/stock_market_insights/stock_market_insights/gspreadreporter/secret/credentials.json'
SPREADSHEET_ID = '1FwrZ30o_JZEKN7ANwwnuc7ZiUxxdjWQ6pfEbcamlaZ4'

WS_REPORT = 'Raport'
WS_WATCHED = 'Obserwowane'

WIG20 = [
    'ALE', 'ALR', 'CCC', 'CDR', 'CPS',
    'DNP', 'JSW', 'KGH', 'LPP', 'LTS',
    'OPL', 'PEO', 'PGE', 'PGN', 'PKN',
    'PKO', 'PLY', 'PZU', 'SPL', 'TPE'
]

MWIG40 = [
    '11B', 'ACP', 'AMC', 'ASE', 'ATT', 'BDX', 'BFT', 'BHW', 'BNP', 'CAR',
    'CIE', 'CLN', 'CMR', 'DOM', 'DVL', 'EAT', 'ECH', 'ENA', 'ENG', 'EUR',
    'FMF', 'FTE', 'GPW', 'GTC', 'GTN', 'ING', 'KER', 'KRU', 'KTY', 'LVC',
    'LWB', 'MAB', 'MIL', 'NEU', 'PKP', 'PLW', 'STP', 'TEN', 'VRG', 'WPL'
]

MY_TICKERS = WIG20 + MWIG40


store_data()


def update_stocks_spreadsheet(spreadsheet):
    report = spreadsheet.worksheet(WS_REPORT)

    """ GET INCREASED VOLUME STOCKS """
    stocks_to_analyse = {s: Stock(s) for s in MY_TICKERS}
    print('\nSelecting stocks for report...')
    selected_stocks = select_stocks_with_increased_volume(stocks_to_analyse)
    print(f'{len(selected_stocks)} stocks selected')

    """ UPDATE ANALYSIS REPORT """
    update_report(report, selected_stocks)


if __name__ == '__main__':
    """ Get authorized connection """
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, SCOPE)
    client = gspread.authorize(creds)

    """ Open spreadsheet """
    sh = client.open_by_key(SPREADSHEET_ID)

    """ Update spreadsheet """
    update_stocks_spreadsheet(sh)
