import pandas as pd
from Indicators.INDICATOR import Indicator
from Indicators.SMA import SMA


class MACD(Indicator):
    def __init__(self, name, params, source):
        super().__init__(name, params, source)
        self.buffer = None
        self.last_close = None
        self.N = params[0]

    def count(self, df):

        return pd.DataFrame({
            f"MACD": df["EMA 12"] - df["EMA 26"]
        })

