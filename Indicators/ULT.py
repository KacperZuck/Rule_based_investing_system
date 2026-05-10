import pandas as pd
import numpy as np

from Indicators.INDICATOR import Indicator


class ULT(Indicator):
    def __init__(self, name, params, columns):
        super().__init__(name, params, columns)
        self.p1 = params[0]
        self.p2 = params[1]
        self.p3 = params[2]
        self.last_close = None
        self.tr_buff = None
        self.buffer = None

    def count(self, df, period1=7, period2=14,period3=28):
        
        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]
        
        tr2 = abs(close.shift(1) - high)
        tr = pd.concat( [close.shift(1), high],axis=1).max(axis=1)
        bp = pd.concat( [close.shift(1), low], axis=1).min(axis=1)
        tr -= bp

        #adx["tr"] = pd.concat( [tr1, tr2, tr3],axis=1 ).max(axis=1)
        # Buing presure
        bp = close - pd.concat( [close.shift(1), low], axis=1).min(axis=1)

        avg1 = (bp.rolling(window=period1, min_periods=period1).sum()
                      /tr.rolling(window=period1, min_periods=period1).sum())
        avg2 = (bp.rolling(window=period2, min_periods=period2).sum()
                      /tr.rolling(window=period2, min_periods=period2).sum())
        avg3 = (bp.rolling(window=period3, min_periods=period3).sum()
                      /tr.rolling(window=period3, min_periods=period3).sum())

        self.last_close = close.iloc[-1]
        self.bp_buffer = bp.tail(self.p3)
        self.tr_buffer = tr.tail(self.p3)

        result = 100/7 * (4*avg1 + 2*avg2 + avg3)
        self.results = pd.DataFrame({
            self.name: result 
        }, index=df.index)
        return self.results

    def update(self, new_df):
        if self.last_close is None:
            return pd.DataFrame({self.name: [np.nan]}, index=new_df.index)

        high = new_df[self.columns[1]].iloc[0]
        low = new_df[self.columns[2]].iloc[0]
        close = new_df[self.columns[3]].iloc[0]

        min_l_pc = min(low, self.last_close)
        max_h_pc = max(high, self.last_close)

        bp_today = close - min_l_pc
        tr_today = max_h_pc - min_l_pc

        self.buffer = pd.concat([self.buffer, pd.Series([bp_today])]).tail(self.p3)
        self.tr_buff = pd.concat([self.tr_buff, pd.Series([tr_today])]).tail(self.p3)

        def get_current_avg(p):
            sum_bp = self.buffer.tail(p).sum()
            sum_tr = self.tr_buff.tail(p).sum()
            return sum_bp / sum_tr if sum_tr != 0 else 0

        avg1 = get_current_avg(self.p1)
        avg2 = get_current_avg(self.p2)
        avg3 = get_current_avg(self.p3)

        new_ult = 100 / 7 * (4 * avg1 + 2 * avg2 + avg3)

        result = pd.DataFrame({self.name: [new_ult]}, index=new_df.index)
        self.results = pd.concat([self.results, result])
        self.last_close = close

        return result