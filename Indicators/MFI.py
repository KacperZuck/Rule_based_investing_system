import pandas as pd
import numpy as np
from Indicators.INDICATOR import Indicator


class MFI(Indicator):
    def __init__(self, name, params, columns):
        super().__init__( name, params, columns)
        self.last_tp = None
        self.N = params[0]
        self.surplus_flow_buffer = None
        self.negative_flow_buffer = None

    def count(self, df):

        high = df[self.columns[1]]
        low = df[self.columns[2]]
        close = df[self.columns[3]]
        volume = df[self.columns[4]]

        tp = ( close + low + high)/3
        rmf = tp * volume # raw money flow

        surplus_flow = pd.Series(np.where( rmf > rmf.shift(1),rmf, 0), index=df.index)
        negative_flow = pd.Series(np.where( rmf < rmf.shift(1),rmf, 0), index=df.index)

        mr = (surplus_flow.rolling(window=self.N).sum() /
                    negative_flow.rolling(window=self.N).sum())

        result = 100 - (100/ (1+mr))
        self.results = pd.DataFrame({
            self.name: result
        }, index=df.index)

        self.last_tp = tp.iloc[-1]
        self.surplus_flow_buffer = pd.Series(surplus_flow, index=df.index).tail(self.N)
        self.negative_flow_buffer = pd.Series(negative_flow, index=df.index).tail(self.N)

        return self.results

    def update(self, df):
        high = df[self.columns[1]].iloc[0]
        low = df[self.columns[2]].iloc[0]
        close = df[self.columns[3]].iloc[0]
        volume = df[self.columns[4]].iloc[0]

        tp = (close + low + high) / 3
        rmf = tp * volume

        if self.last_tp is None:
            surplus_flow = 0
            negative_flow = 0
        else:
            if tp > self.last_tp:
                surplus_flow = rmf
                negative_flow = 0
            elif tp < self.last_tp:
                surplus_flow = 0
                negative_flow = rmf
            else:
                surplus_flow = 0
                negative_flow = 0


        self.surplus_flow_buffer = pd.concat([self.surplus_flow_buffer, pd.Series([surplus_flow])]).tail(self.N)
        self.negative_flow_buffer = pd.concat([self.negative_flow_buffer, pd.Series([negative_flow])]).tail(self.N)

        sum_surplus = self.surplus_flow_buffer.sum()
        sum_negative = self.negative_flow_buffer.sum()

        if sum_negative == 0:
            mfi =0
        else:
            mr = sum_surplus / sum_negative
            mfi = 100 - (100/ (1+mr))

        result = pd.DataFrame({
            self.name: mfi
        }, index=df.index)

        self.results = pd.concat([self.results, result])
        self.last_tp = tp

        return result