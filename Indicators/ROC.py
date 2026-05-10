import numpy as np
import pandas as pd
from narwhals import new_series

from Indicators.INDICATOR import Indicator


class ROC(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.buffer = None
        self.N = params[0]

    def count(self, df):
        data = df[self.columns[0]]
        shift = data.shift(self.N)
        roc = 100 *( data - shift)/ shift
        self.buffer = data.tail(self.N + 1)
        self.results =  pd.DataFrame({
            self.name: roc
        }, index=df.index)
        return self.results

    def update(self, df):
        price = df[self.columns[0]]
        self.buffer = pd.concat([self.buffer, price]).tail(self.N + 1)

        if len(self.buffer) > self.N:
            price_n_ago = self.buffer.iloc[0]
            if price_n_ago != 0:
                new_roc = 100 * (price - price_n_ago) / price_n_ago
            else:
                new_roc = 0
        else:
            new_roc = np.nan

        result = pd.DataFrame(
            {self.name: new_roc}, index=df.index)
        self.results = pd.concat([self.results, result])
        return result