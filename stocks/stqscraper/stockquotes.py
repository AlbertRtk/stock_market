from . import DATA_DIR
import pandas as pd
import numpy as np
from os import path
from urllib.request import urlretrieve
from datetime import datetime, timedelta


class StockQuotes():
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()
        return self._data  # TODO: consider using .copy() here

    @property
    def csv_file_path(self):
        return path.join(DATA_DIR, f'{self.ticker}_ohcl.csv')

    def download_ohlc_csv_from_stooq(self):
        url = f'http://stooq.com/q/d/l/?i=d&s={self.ticker}'
        file_path, _ = urlretrieve(url, self.csv_file_path)
        return file_path

    def read_csv_file(self):
        output = pd.read_csv(self.csv_file_path, 
                             index_col='Date',
                             parse_dates=['Date'],
                             date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
        output['Volume'] = output['Volume'].astype(np.float64)
        return output

    def _get_data(self):
        update_required = True  # assuming that update will be required

        """ time info """
        time_now = datetime.now()
        weekday_now = datetime.weekday(time_now)
        is_weekend = True if weekday_now in (5, 6) else False

        """ calculate expected date for last OHLC data, consider only weekdays from Mo-Fr,
            assume that last update was one day earlier """
        delta_days = (weekday_now - 4) if is_weekend else 0
        expected_ohlc_time = time_now - timedelta(days=delta_days)
        last_ohlc_time = expected_ohlc_time - timedelta(days=1)

        """ File with data for ticker exists """
        if path.exists(self.csv_file_path):
            timestamp_now = datetime.timestamp(time_now)
            timestamp_up = path.getatime(self.csv_file_path)  # CSV file modification time

            """ CSV updated within last 24 hours or it is weekend (no new data) """
            if (timestamp_now - timestamp_up < 24 * 3600) or is_weekend:
                output = self.read_csv_file()
                last_ohlc_time = output.iloc[-1].name

                if last_ohlc_time.date() == expected_ohlc_time.date() or (time_now.hour < 20 and not is_weekend):
                    update_required = False

        if update_required:
            """ update CSV file and read data """
            self.download_ohlc_csv_from_stooq()
            output = self.read_csv_file()
    
        output.sort_index(ascending=True, inplace=True)
        
        return output


if __name__ == '__main__':
    pass
