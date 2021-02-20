WS_WALLET = 'Portfel'
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

TICKERS_COL = 1     # col A, valid for all worksheets
FIRST_DATA_ROW = 3  # valid for all worksheets
UPDATE_TIME_ACELL = 'B1'

WALLET_PRICES_COL = 5      # col E
WALLET_PBV_COL = 11
WALLET_EPS_COL = 12
WALLET_PE_COL = 13
WALLET_DIVIDEND_YIELD_COL = 14
WALLET_VOLUME_MEAN_LONG = 15  # long time (e.g., last 90 sessions)
WALLET_VOLUME_MEAN_SHORT = 16  # short time (e.g., last 5 sessions)
WALLET_VOLUME = 17  # last session volume
WALLET_PLOT_LINK_COL = 18

WALLET_INVESTED_ACELL = 'F1'

REPORT_PRICES_COL = 2
REPORT_PBV_COL = 3
REPORT_EPS_COL = 4
REPORT_PE_COL = 5
REPORT_DIVIDEND_YIELD_COL = 6
REPORT_VOLUME_MEAN_LONG = 7  # long time (e.g., last 90 sessions)
REPORT_VOLUME_MEAN_SHORT = 8  # short time (e.g., last 5 sessions)
REPORT_VOLUME = 9  # last session
REPORT_PLOT_LINK_COL = 10
REPORT_SHORT_LONG_RATIO = 11
REPORT_VOLUME_LONG_RATIO = 12

REPORT_FIRST_ACOL = 'A'
REPORT_LAST_ACOL = 'L'

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
GOOGLE_CREDS = r'secret/credentials.json'
SPREADSHEET_ID = '1FwrZ30o_JZEKN7ANwwnuc7ZiUxxdjWQ6pfEbcamlaZ4'
