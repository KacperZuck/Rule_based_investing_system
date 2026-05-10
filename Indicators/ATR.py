import pandas as pd
import numpy as np
from Indicators.SMA import SMA
from Indicators.INDICATOR import Indicator


class ATR(Indicator):
    def __init__(self, name, params, source):
        super().__init__(name, params, source)
        self.buffer = None
        self.last_close = None
        self.N = params[0]
    def count(self, df):

        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]

        tr1 = high - low
        tr1.iloc[0] = np.nan
        tr2 = abs(close - high)
        tr3 = abs(close - low)

        result = pd.concat( [tr1, tr2, tr3],axis=1 ).max(axis=1)
        self.buffer = result.tail(self.N)
        result = SMA.calculate_sma(result, self.N)

        self.last_close = close.iloc[-1]
        self.results = pd.DataFrame({self.name: result}, index=df.index)

        return self.results

    def update(self, new_df):

        high = new_df[self.columns[1]]
        low = new_df[self.columns[2]]
        close = new_df[self.columns[3]]

        result = high - low
        if self.last_close is not None:
            tr2 = abs(close - high)
            tr3 = abs(close - low)
            result = pd.concat( [result, tr2, tr3],axis=1 ).max(axis=1)

        self.buffer = pd.concat([self.buffer, result]).tail(self.N)
        result = SMA.calculate_sma(self.buffer, self.N)
        self.last_close = close

        result = pd.DataFrame(
            {self.name: result}, index=new_df.index)
        self.results = pd.concat([self.results, result])
        return result