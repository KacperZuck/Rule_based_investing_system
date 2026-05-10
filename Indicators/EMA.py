import pandas as pd
from numpy import mean

from Indicators.INDICATOR import Indicator


class EMA(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.last_ema = None
        self.N = params[0]
        self.alpha=2/(self.N+1)

    def count( self, df):
        data = df[self.columns[0]]
        self.results = data.ewm(alpha=self.alpha, adjust=False).mean()
        if not self.results.empty:
            self.last_ema = self.results.iloc[-1]
        return pd.DataFrame({self.name: self.results}, index=df.index)

    def update(self, new_df):
        price = new_df[self.columns[0]]

        if self.last_ema is None:
            new_ema = price
        else:
            new_ema = (price * self.alpha) + (self.last_ema * (1 - self.alpha))

        self.last_ema = new_ema
        new_result = pd.DataFrame({self.name: new_ema}, index=new_df.index)
        self.results = pd.concat([self.results, pd.Series([new_ema], index=new_df.index)])

        return new_result