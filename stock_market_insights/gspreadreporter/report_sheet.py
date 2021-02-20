from config import *
from datetime import datetime


def clear_worksheet_range(worksheet, range_):
    cell_list = worksheet.range(range_)
    for cell in cell_list:
        cell.value = ''
    worksheet.update_cells(cell_list)


def fill_in_report_row(row, share):
    long_mean = share.mean_volume(90)
    short_mean = share.mean_volume(5)
    row[TICKERS_COL - 1].value = share.ticker
    row[REPORT_PRICES_COL - 1].value = share.price
    row[REPORT_PBV_COL - 1].value = share.pbv
    row[REPORT_EPS_COL - 1].value = share.eps
    row[REPORT_PE_COL - 1].value = share.pe
    row[REPORT_DIVIDEND_YIELD_COL - 1].value = share.dividend_yield
    row[REPORT_VOLUME_MEAN_LONG - 1].value = round(long_mean, 0)
    row[REPORT_VOLUME_MEAN_SHORT - 1].value = round(short_mean, 0)
    row[REPORT_VOLUME - 1].value = share.volume
    row[REPORT_PLOT_LINK_COL - 1].value = share.stooq_plot_link
    row[REPORT_SHORT_LONG_RATIO - 1].value = round(short_mean/long_mean, 2)
    row[REPORT_VOLUME_LONG_RATIO - 1].value = round(share.volume/long_mean, 2)


def update_report_row(report_wks, row_idx, share):
    cell_range = f'{REPORT_FIRST_ACOL}{row_idx}:{REPORT_LAST_ACOL}{row_idx}'
    row = report_wks.range(cell_range)
    fill_in_report_row(row, share)
    report_wks.update_cells(row)


def update_report(report_wks, stocks: dict):
    print(f'\nPreparing analysis report for {len(stocks)} stocks:')
    str_today = datetime.now().strftime('%Y-%m-%d')
    report_wks.update_acell(UPDATE_TIME_ACELL, str_today)

    """ Clear worksheet from old data """
    last_filled_row = len(report_wks.col_values(TICKERS_COL))
    cell_range = f'{REPORT_FIRST_ACOL}{FIRST_DATA_ROW}:{REPORT_LAST_ACOL}{last_filled_row}'
    clear_worksheet_range(report_wks, cell_range)

    """ Update worksheet """
    for i, tck in enumerate(stocks, FIRST_DATA_ROW):
        share = stocks[tck]
        print(f'{1+i-FIRST_DATA_ROW}\t{tck}\t Data from: {share.date}')
        update_report_row(report_wks, i, share)
