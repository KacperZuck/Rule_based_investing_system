import pandas as pd
from Indicators.INDICATOR import Indicator


class SMA(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.price_buffer = None
        self.N = params[0]

    def count( self, df):
        data = df[self.columns[0]]
        self.results = pd.DataFrame({
            self.name: data.rolling(self.N).mean()
        }, index=df.index)
        self.price_buffer = data.tail(self.N)
        return self.results

    def update(self, new_df):
        # col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        price = new_df[self.columns[0]]

        self.price_buffer = pd.concat([self.price_buffer, price]).tail(self.N)
        new_avg = self.price_buffer.mean()

        new_result = pd.DataFrame(
            {self.name: new_avg}, index=new_df.index)
        self.results = pd.concat([self.results, new_result])
        return new_result

    @staticmethod
    def calculate_sma(df, n):
        return df.rolling(window=n).mean()