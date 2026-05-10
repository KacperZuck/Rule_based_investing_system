import numpy as np
import pandas as pd
from Indicators import EMA
from Indicators.INDICATOR import Indicator


class TRIX(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.N = params[0]
        self.alpha = 2/(self.N+1)
        self.last_ema3 = None
        self.ema3_state = None
        self.ema2_state = None
        self.ema1_state = None
    def count(self, df):
        col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        data = df[col_name]

        ema1 = data.ewm(alpha=self.alpha, adjust=False).mean()
        ema2 = ema1.ewm(alpha=self.alpha, adjust=False).mean()
        ema3 = ema2.ewm(alpha=self.alpha, adjust=False).mean()
        trix_series = ema3.pct_change(1) * 100

        self.ema1_state = ema1.iloc[-1]
        self.ema2_state = ema2.iloc[-1]
        self.ema3_state = ema3.iloc[-1]
        self.last_ema3 = ema3.iloc[-1]

        self.results = pd.DataFrame({self.name: trix_series}, index=df.index)
        return self.results

    def update(self, df):
        col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        price = df[col_name].iloc[0]

        if self.ema1_state is None:
            return pd.DataFrame({self.name: [np.nan]}, index=df.index)

        new_ema1 = (price * self.alpha) + (self.ema1_state * (1 - self.alpha))
        new_ema2 = (new_ema1 * self.alpha) + (self.ema2_state * (1 - self.alpha))
        new_ema3 = (new_ema2 * self.alpha) + (self.ema3_state * (1 - self.alpha))

        if self.last_ema3 != 0:
            new_trix = ((new_ema3 - self.last_ema3) / self.last_ema3) * 100
        else:
            new_trix = 0

        self.ema1_state = new_ema1
        self.ema2_state = new_ema2
        self.ema3_state = new_ema3
        self.last_ema3 = new_ema3  # To jest potrzebne w następnym kroku

        result = pd.DataFrame({self.name: [new_trix]}, index=df.index)
        self.results = pd.concat([self.results, result])

        return result