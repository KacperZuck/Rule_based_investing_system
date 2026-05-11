import pandas as pd
from Indicators.INDICATOR import Indicator
from Indicators.SMA import SMA


class MACD(Indicator):
    def __init__(self, name, params, source):
        super().__init__(name, params, source)
        self.buffer = None
        self.last_close = None
        self.slow_ema = params[0]
        self.fast_ema = params[1]
        self.signal = params[2]

    def count(self, df):

        close = df[self.columns[1]]
        macd = SMA.calculate_sma(close, self.fast_ema) - SMA.calculate_sma(close, self.slow_ema)
        signal = SMA.calculate_sma(close, self.signal)

        self.results = pd.DataFrame(
            {self.name: macd,
             f"{self.name}_signal": signal,
             }, index=df.index
        )
        self.buffer = close
        return self.results

    def update(self, new_data):

        close = new_data[self.columns[1]]
        self.buffer = pd.concat([self.buffer, close], axis=1)

        macd = SMA.calculate_sma(self.buffer, self.fast_ema) - SMA.calculate_sma(self.buffer, self.slow_ema)
        signal = SMA.calculate_sma(self.buffer, self.signal)

        self.results = pd.DataFrame(
            {self.name: macd,
             f"{self.name}_signal": signal,
             }, index=new_data.index
        )
        self.buffer = close
        return self.results

