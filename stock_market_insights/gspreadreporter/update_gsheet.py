from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    from marketools import Stock, store_data
    from marketools.analysis import simple_relative_price_change, \
        select_stocks_with_increased_volume
except ModuleNotFoundError:
    import sys
    sys.path.append("../marketools")
    from marketools import Stock, store_data
    from marketools.analysis import simple_relative_price_change, \
        select_stocks_with_increased_volume


store_data()


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

ACEL_UPDATE_TIME = 'B1'
ACOL_FIRST = 'A'
ACOL_LAST = 'R'

COL_TICKER = 0  # col A
COL_PRICE = 1
COL_PREVIOUS = 2
COL_CHANGE = 3
COL_CHANGE_PERC = 4
COL_DAILY = 5
COL_DAILY_PERC = 6
COL_OPEN = 7
COL_HIGH = 8
COL_LOW = 9
COL_VOL = 10
COL_AVG_VOL_SHORT = 11
COL_AVG_VOL_LONG = 12
COL_PBV = 13
COL_EPS = 14
COL_PE = 15
COL_DIV_YIELD = 16
COL_PLOT = 17

ROW_WIG = 4
ROW_WIG20 = 5
ROW_MWIG40 = 6
ROW_SWIG80 = 7
ROW_WIG20_TOP_INCS = 11
ROW_WIG20_TOP_DECS = 19
ROW_MWIG40_TOP_INCS = 27
ROW_MWIG40_TOP_DECS = 35
ROW_VOL_SELECTED_FIRST = 43
ROW_LAST = 1000


def clear_worksheet_range(worksheet, range_):
    cell_list = worksheet.range(range_)
    for cell in cell_list:
        cell.value = ''
    worksheet.update_cells(cell_list)


def fill_in_report_row(row, share, stock_index=False):
    row[COL_TICKER].value = share.ticker
    row[COL_PRICE].value = share.last_ohlc['Close']
    row[COL_PREVIOUS].value = share.ohlc.iloc[-2]['Close']
    row[COL_CHANGE].value = share.last_ohlc['Close'] - share.ohlc.iloc[-2]['Close']
    row[COL_DAILY].value = share.last_ohlc['Close'] - share.last_ohlc['Open']
    row[COL_OPEN].value = share.last_ohlc['Open']
    row[COL_HIGH].value = share.last_ohlc['High']
    row[COL_LOW].value = share.last_ohlc['Low']
    row[COL_VOL].value = share.volume
    row[COL_AVG_VOL_SHORT].value = round(share.mean_volume(5), 0)
    row[COL_AVG_VOL_LONG].value = round(share.mean_volume(90), 0)

    rel_change = simple_relative_price_change(share.last_ohlc['Close'], share.ohlc.iloc[-2]['Close']) * 100
    rel_change = round(rel_change, 2)
    row[COL_CHANGE_PERC].value = rel_change

    rel_change = simple_relative_price_change(share.last_ohlc['Close'], share.last_ohlc['Open']) * 100
    rel_change = round(rel_change, 2)
    row[COL_DAILY_PERC].value = rel_change

    if not stock_index:
        row[COL_PBV].value = share.pbv
        row[COL_EPS].value = share.eps
        row[COL_PE].value = share.pe
        row[COL_DIV_YIELD].value = share.dividend_yield
        row[COL_PLOT].value = share.stooq_plot_link


def update_report_row(report_wks, row_idx, share):
    cell_range = f'{ACOL_FIRST}{row_idx}:{ACOL_LAST}{row_idx}'
    row = report_wks.range(cell_range)
    is_stock_index = share.ticker.lower() in ('wig', 'wig20', 'mwig40', 'swig80')
    fill_in_report_row(row, share, is_stock_index)
    report_wks.update_cells(row)


def update_report(report_wks):
    print(f'Preparing analysis report...')
    str_today = datetime.now().strftime('%Y-%m-%d, %H:%M')
    report_wks.update_acell(ACEL_UPDATE_TIME, str_today)

    # Stock Market Indices
    print('Stock market indices summary...')
    update_report_row(report_wks, ROW_WIG, Stock('WIG'))
    update_report_row(report_wks, ROW_WIG20, Stock('WIG20'))
    update_report_row(report_wks, ROW_MWIG40, Stock('mWIG40'))
    update_report_row(report_wks, ROW_SWIG80, Stock('sWIG80'))

    sort_key = lambda item: simple_relative_price_change(item[1].last_ohlc['Close'],
                                                         item[1].ohlc.iloc[-2]['Close'])

    # WIG20
    wig20_stocks = {s: Stock(s) for s in WIG20}
    sorted_stocks = sorted(wig20_stocks.items(), key=sort_key, reverse=True)
    wig20_stocks = {k: v for k, v in sorted_stocks}

    # WIG20 top increases
    print('WIG20 top increases...')
    for i, tck in enumerate(wig20_stocks, ROW_WIG20_TOP_INCS):
        share = wig20_stocks[tck]
        update_report_row(report_wks, i, share)
        if i == ROW_WIG20_TOP_INCS + 4:
            break

    # WIG20 top decreases
    print('WIG20 top decreases...')
    for i, tck in enumerate(reversed(wig20_stocks), ROW_WIG20_TOP_DECS):
        share = wig20_stocks[tck]
        update_report_row(report_wks, i, share)
        if i == ROW_WIG20_TOP_DECS + 4:
            break

    # mWIG40
    mwig40_stocks = {s: Stock(s) for s in MWIG40}
    sorted_stocks = sorted(mwig40_stocks.items(), key=sort_key, reverse=True)
    mwig40_stocks = {k: v for k, v in sorted_stocks}

    # mWIG40 top increases
    print('mWIG40 top increases...')
    for i, tck in enumerate(mwig40_stocks, ROW_MWIG40_TOP_INCS):
        share = mwig40_stocks[tck]
        update_report_row(report_wks, i, share)
        if i == ROW_MWIG40_TOP_INCS + 4:
            break

    # mWIG40 top decreases
    print('mIG40 top decreases...')
    for i, tck in enumerate(reversed(mwig40_stocks), ROW_MWIG40_TOP_DECS):
        share = mwig40_stocks[tck]
        update_report_row(report_wks, i, share)
        if i == ROW_MWIG40_TOP_DECS + 4:
            break

    # Clear worksheet from old data
    cell_range = f'{ACOL_FIRST}{ROW_VOL_SELECTED_FIRST}:{ACOL_LAST}{ROW_LAST}'
    clear_worksheet_range(report_wks, cell_range)

    # update worksheet with increased volume stocks
    print('Selecting increased volume stocks for report...')
    stocks_to_analyse = {**wig20_stocks, **mwig40_stocks}
    selected_stocks = select_stocks_with_increased_volume(stocks_to_analyse)
    print(f'{len(selected_stocks)} stocks selected')

    for i, tck in enumerate(selected_stocks, ROW_VOL_SELECTED_FIRST):
        share = stocks_to_analyse[tck]
        update_report_row(report_wks, i, share)


if __name__ == '__main__':
    """ Get authorized connection """
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, SCOPE)
    client = gspread.authorize(creds)

    """ Open spreadsheet """
    sh = client.open_by_key(SPREADSHEET_ID)
    report = sh.worksheet(WS_REPORT)

    """ UPDATE ANALYSIS REPORT """
    update_report(report)
