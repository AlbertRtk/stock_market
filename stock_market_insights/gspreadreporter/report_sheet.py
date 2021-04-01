from datetime import datetime
from marketools.analysis import simple_relative_price_change


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

ROW_VOL_SELECTED_FIRST = 43
ROW_LAST = 1000


def clear_worksheet_range(worksheet, range_):
    cell_list = worksheet.range(range_)
    for cell in cell_list:
        cell.value = ''
    worksheet.update_cells(cell_list)


def fill_in_report_row(row, share):
    row[COL_TICKER].value = share.ticker
    row[COL_PRICE].value = share.last_ohlc['Close']
    row[COL_PREVIOUS].value = None
    row[COL_CHANGE].value = None
    row[COL_CHANGE_PERC].value = None
    row[COL_DAILY].value = share.last_ohlc['Close'] - share.last_ohlc['Open']
    row[COL_DAILY_PERC].value = simple_relative_price_change(share.last_ohlc['Close'], share.last_ohlc['Open'])
    row[COL_OPEN].value = share.last_ohlc['Open']
    row[COL_HIGH].value = share.last_ohlc['High']
    row[COL_LOW].value = share.last_ohlc['Low']
    row[COL_VOL].value = share.volume
    row[COL_AVG_VOL_SHORT].value = round(share.mean_volume(5), 0)
    row[COL_AVG_VOL_LONG].value = round(share.mean_volume(90), 0)
    row[COL_PBV].value = share.pbv
    row[COL_EPS].value = share.eps
    row[COL_PE].value = share.pe
    row[COL_DIV_YIELD].value = share.dividend_yield
    row[COL_PLOT].value = share.stooq_plot_link


def update_report_row(report_wks, row_idx, share):
    cell_range = f'{ACOL_FIRST}{row_idx}:{ACOL_LAST}{row_idx}'
    row = report_wks.range(cell_range)
    fill_in_report_row(row, share)
    report_wks.update_cells(row)


def update_report(report_wks, stocks: dict):
    print(f'\nPreparing analysis report for {len(stocks)} stocks:')
    str_today = datetime.now().strftime('%Y-%m-%d, %H:%M')
    report_wks.update_acell(ACEL_UPDATE_TIME, str_today)

    """ Clear worksheet from old data """
    cell_range = f'{ACOL_FIRST}{ROW_VOL_SELECTED_FIRST}:{ACOL_LAST}{ROW_LAST}'
    clear_worksheet_range(report_wks, cell_range)

    """ Update worksheet """
    for i, tck in enumerate(stocks, ROW_VOL_SELECTED_FIRST):
        share = stocks[tck]
        update_report_row(report_wks, i, share)
