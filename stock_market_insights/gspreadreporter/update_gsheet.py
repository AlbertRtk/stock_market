import sys
sys.path.append("../marketools")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from marketools import Stock, store_data
from report_sheet import update_report


SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
GOOGLE_CREDS = r'/home/albi/projects/stock_market_insights/stock_market_insights/gspreadreporter/secret/credentials.json'
SPREADSHEET_ID = '1FwrZ30o_JZEKN7ANwwnuc7ZiUxxdjWQ6pfEbcamlaZ4'
WS_REPORT = 'WSE report'


WIG20 = [
    'ALE', 'ALR', 'CCC', 'CDR', 'CPS', 'DNP', 'JSW', 'KGH', 'LPP', 'LTS',
    'OPL', 'PEO', 'PGE', 'PGN', 'PKN', 'PKO', 'PLY', 'PZU', 'SPL', 'TPE'
]
MWIG40 = [
    '11B', 'ACP', 'AMC', 'ASE', 'ATT', 'BDX', 'BFT', 'BHW', 'BNP', 'CAR',
    'CIE', 'CLN', 'CMR', 'DOM', 'DVL', 'EAT', 'ECH', 'ENA', 'ENG', 'EUR',
    'FMF', 'FTE', 'GPW', 'GTC', 'GTN', 'ING', 'KER', 'KRU', 'KTY', 'LVC',
    'LWB', 'MAB', 'MIL', 'NEU', 'PKP', 'PLW', 'STP', 'TEN', 'VRG', 'WPL'
]
MY_TICKERS = WIG20 + MWIG40

store_data()


if __name__ == '__main__':
    """ Get authorized connection """
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, SCOPE)
    client = gspread.authorize(creds)

    """ Open spreadsheet """
    sh = client.open_by_key(SPREADSHEET_ID)

    """ Update spreadsheet """
    report = sh.worksheet(WS_REPORT)
    stocks_to_analyse = {s: Stock(s) for s in MY_TICKERS}

    """ UPDATE ANALYSIS REPORT """
    update_report(report, stocks_to_analyse)
