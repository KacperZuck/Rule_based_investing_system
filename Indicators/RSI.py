import numpy as np
import pandas as pd

from Indicators.INDICATOR import Indicator


class RSI(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.last_price = None
        self.gain_buffer = None
        self.loss_buffer = None
        self.N = params[0]
    def count(self, df):

        col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        data = df[col_name]
        delta = data.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=self.N).mean()
        avg_loss = loss.rolling(window=self.N).mean()

        rs = avg_gain / avg_loss
        series = 100 - (100/(1+rs))
        self.last_price = data.iloc[-1]
        self.gain_buffer = gain.tail(self.N)
        self.loss_buffer = loss.tail(self.N)
        self.results = pd.DataFrame({self.name: series}, index=df.index)
        return self.results

    def update(self, df):
        col_name = self.columns[0] if isinstance(self.columns, list) else self.columns
        current_price = df[col_name].iloc[0]

        if self.last_price is None:
            self.last_price = current_price
            new_rsi = np.nan
        else:
            delta = current_price - self.last_price
            gain_today = max(delta, 0)
            loss_today = max(-delta, 0)

            self.gain_buffer = pd.concat([self.gain_buffer, pd.Series([gain_today])]).tail(self.N)
            self.loss_buffer = pd.concat([self.loss_buffer, pd.Series([loss_today])]).tail(self.N)

            avg_gain = self.gain_buffer.mean()
            avg_loss = self.loss_buffer.mean()

            if avg_loss is not None == 0:
                new_rsi = 100 if avg_gain > 0 else 50
            else:
                rs = avg_gain / avg_loss
                new_rsi = 100 - (100 / (1 + rs))
        result = pd.DataFrame({self.name: new_rsi}, index=df.index)
        self.results = pd.concat([self.results, result])
        self.last_price = current_price
        return result