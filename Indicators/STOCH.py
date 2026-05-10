import numpy as np
import pandas as pd
from Indicators.SMA import SMA
from Indicators.INDICATOR import Indicator


class STOCH(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.high_buffer = None
        self.low_buffer = None
        self.K_buffer = None
        self.K = params[0]
        self.D = params[1]
        self.smooth = params[2]
    def count( self, df):

        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]

        low_min = low.rolling(window=self.K).min()
        high_max = high.rolling(window=self.K).max()

        denominator = high_max - low_min
        stoch_k_raw = 100 * (close - low_min) / denominator
        stoch_k_raw = stoch_k_raw.replace([np.inf, -np.inf], 50).fillna(50)

        k_smoothed_stoch = SMA.calculate_sma(stoch_k_raw, self.smooth).fillna(50)
        d_line_stoch = SMA.calculate_sma(stoch_k_raw, self.D)

        self.high_buffer = high.tail(self.K)
        self.low_buffer = low.tail(self.K)
        self.K_buffer = k_smoothed_stoch.tail(self.D)

        self.results = pd.DataFrame({
            f"{self.name}_K": k_smoothed_stoch,
            f"{self.name}_D": d_line_stoch
        }, index=df.index)

        return self.results

    def update(self, df):
        h = df[self.columns[1]].iloc[0]
        l = df[self.columns[2]].iloc[0]
        c = df[self.columns[3]].iloc[0]

        self.high_buffer = pd.concat([self.high_buffer, pd.Series([h])]).tail(self.K)
        self.low_buffer = pd.concat([self.low_buffer, pd.Series([l])]).tail(self.K)

        h_max = self.high_buffer.max()
        l_min = self.low_buffer.min()

        denominator = h_max - l_min
        raw_k = 100 * (c - l_min) / denominator if denominator != 0 else 50

        self.K_buffer = pd.concat([self.K_buffer, pd.Series([raw_k])]).tail(self.D)

        current_k = raw_k
        current_d = self.K_buffer.mean()

        new_result = pd.DataFrame({
            f"{self.name}_K": [current_k],
            f"{self.name}_D": [current_d]
        }, index=df.index)
        self.results = pd.concat([self.results, new_result])
        return new_result