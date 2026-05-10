import pandas as pd
import numpy as np
from Indicators.SMA import SMA
from Indicators.INDICATOR import Indicator


class ADX(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.N = params[0]
        self.last_row = None
    def count(self, df):
        # open = df[self.columns[0]]
        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]
        adx = df.copy()

        tr1 = high - low
        tr1.iloc[0] = np.nan
        tr2 = abs(close.shift(1) - high)
        tr3 = abs(close.shift(1) - low)

        adx["tr"] = pd.concat( [tr1, tr2, tr3],axis=1 ).max(axis=1)

        adx["min_dm"] = low-low.shift(1)
        adx["pl_dm"] = high-high.shift(1)

        adx["pl_dm"] = np.where( adx["pl_dm"] > 0, adx["pl_dm"], 0)
        adx["min_dm"] = np.where( adx["min_dm"] > 0, adx["min_dm"], 0)

        adx["pl_dm"] = np.where( adx["pl_dm"] > adx["min_dm"], adx["pl_dm"], 0)
        adx["min_dm"] = np.where( adx["min_dm"] > adx["pl_dm"], adx["min_dm"], 0)

        adx["min_dm"] = SMA.calculate_sma(adx["min_dm"], self.N)
        adx["pl_dm"] = SMA.calculate_sma(adx["pl_dm"],self.N)

        adx["pl_di"] = 100 * adx["pl_dm"] / adx["tr"]
        adx["min_di"] = 100 * adx["min_dm"] / adx["tr"]

        adx["dx"] = 100* abs(adx["pl_di"]-adx["min_di"])/ abs(adx["pl_di"]+adx["min_di"])

        adx["adx"] = SMA.calculate_sma(adx["dx"], self.N)

        self.last_row = df.iloc[-1]
        self.tr_buffer = adx["tr"].tail(self.N)
        self.pl_dm_buffer = pd.Series(adx["pl_dm"], index=df.index).tail(self.N)
        self.min_dm_buffer = pd.Series(adx["min_dm"], index=df.index).tail(self.N)
        self.dx_buffer = adx["dx"].tail(self.N)
        self.results = pd.DataFrame({self.name: adx["adx"]}, index=df.index)
        return self.results

    def update(self, new_df):
        if self.last_row is None:
            return pd.DataFrame({self.name: [np.nan]}, index=new_df.index)
        h_new = new_df[self.columns[1]].iloc[0]
        l_new = new_df[self.columns[2]].iloc[0]
        c_new = new_df[self.columns[3]].iloc[0]


        tr_today = max(h_new - l_new,
                       abs(h_new - self.last_row[self.columns[2]]),
                       abs(l_new - self.last_row[self.columns[2]]))

        up_move = h_new - self.last_row[self.columns[0]]
        down_move = self.last_row[self.columns[1]] - l_new

        pl_dm_today = up_move if (up_move > down_move and up_move > 0) else 0
        min_dm_today = down_move if (down_move > up_move and down_move > 0) else 0

        self.tr_buffer = pd.concat([self.tr_buffer, pd.Series([tr_today])]).tail(self.N)
        self.pl_dm_buffer = pd.concat([self.pl_dm_buffer, pd.Series([pl_dm_today])]).tail(self.N)
        self.min_dm_buffer = pd.concat([self.min_dm_buffer, pd.Series([min_dm_today])]).tail(self.N)

        s_tr = self.tr_buffer.mean()
        s_pl_dm = self.pl_dm_buffer.mean()
        s_min_dm = self.min_dm_buffer.mean()

        pl_di = 100 * s_pl_dm / s_tr
        min_di = 100 * s_min_dm / s_tr
        dx = 100 * abs(pl_di - min_di) / (pl_di + min_di)

        self.dx_buffer = pd.concat([self.dx_buffer, pd.Series([dx])]).tail(self.N)
        adx = self.dx_buffer.mean()

        new_result = pd.DataFrame({self.name: [adx]}, index=new_df.index)
        self.results = pd.concat([self.results, new_result])
        self.last_row = new_df.iloc[0]

        return new_result