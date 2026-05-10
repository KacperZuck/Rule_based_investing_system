import pandas as pd
from Indicators.INDICATOR import Indicator


class William_pR(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.N = params[0]
        self.LL_buffer = None
        self.HH_buffer = None
    def count(self, df):

        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]

        LL = low.rolling(window=self.N).min()
        HH = high.rolling(window=self.N).max()

        denominator = HH - LL
        result = (-100) * (HH - close) / denominator

        self.results = pd.DataFrame({
            self.name: result
        }, index=df.index)

        self.LL_buffer = LL.tail(self.N)
        self.HH_buffer = HH.tail(self.N)
        return self.results

    def update(self, df):

        high = df[self.columns[1]].iloc[0]
        low = df[self.columns[2]].iloc[0]
        close = df[self.columns[3]].iloc[0]

        self.HH_buffer = pd.concat([self.HH_buffer, pd.Series([high])]).tail(self.N)
        self.LL_buffer = pd.concat([self.LL_buffer, pd.Series([low])]).tail(self.N)

        HH = self.HH_buffer.max()
        LL = self.LL_buffer.min()

        denominator = HH  - LL
        if denominator != 0:
            val = (-100) * (HH - close) / denominator
        else:
            val = -50 #przypadku braku ruchu

        result = pd.DataFrame({self.name: [val]}, index=df.index)

        self.results = pd.concat([self.results, result])
        return result