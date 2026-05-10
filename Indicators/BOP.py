import numpy as np
import pandas as pd
from Indicators.SMA import SMA
from Indicators.INDICATOR import Indicator


class BOP(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.N = params[0]
        self.buffer = None
    def count (self, df):

        open = df[self.columns[0]]
        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]

        denominator = high - low
        result = ((close - open) / denominator)
        result = result.replace([np.inf, -np.inf], 0).fillna(0)

        result = SMA.calculate_sma(result, self.N)
        self.buffer = result.tail(self.N)
        self.results = pd.DataFrame({ self.name: result}, index=df.index)
        return self.results

    def update(self, df):
        open = df[self.columns[0]]
        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]

        denominator = high - low
        bop = (close - open) / denominator

        result = pd.DataFrame({ self.name: bop}, index=df.index)
        self.buffer = pd.concat([self.buffer, result]).tail(self.N)

        final_bop = self.buffer.mean()
        new_result = pd.DataFrame({self.name: [final_bop]}, index=df.index)
        self.results = pd.concat([self.results, new_result])
        return new_result