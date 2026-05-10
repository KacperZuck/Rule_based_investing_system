import pandas as pd
from Indicators import SMA
from Indicators.INDICATOR import Indicator


class BB(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.N = params[0]
        self.K = params[1]

    def count(self,df):

        data = df[self.columns].squeeze()
        BB_MID = data.rolling(window=self.N).mean()
        std_dev = data.rolling(window=self.N).std()

        BB_UP = BB_MID + (self.K * std_dev)
        BB_LOW = BB_MID - (self.K * std_dev)

        self.results = pd.DataFrame({
            f"{self.name}_LOW": BB_LOW,
            f"{self.name}_UP": BB_UP,
            f"{self.name}_MID": BB_MID,
        }, index = df.index)
        self.buffer = data.tail(self.N)
        return self.results

    def update(self, df):
        col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        data = pd.concat([self.buffer, df[col_name]]).tail(self.N)

        BB_MID = data.mean()
        std_dev = data.std()

        BB_UP = BB_MID + (self.K * std_dev)
        BB_LOW = BB_MID - (self.K * std_dev)

        new_row = pd.DataFrame({
            f"{self.name}_LOW": [BB_LOW],
            f"{self.name}_UP": [BB_UP],
            f"{self.name}_MID": [BB_MID],
        }, index=df.index)

        self.results = pd.concat([self.results, new_row])
        self.buffer = data
        return new_row

