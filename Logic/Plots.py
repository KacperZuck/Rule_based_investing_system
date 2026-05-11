import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs.layout.map.layer import symbol
from plotly.subplots import make_subplots
import pandas as pd
import time
from Logic.maps import CANDLESTICK

st.set_page_config(page_title="Strategy Live - TEST", layout="wide")
st.title("Panel Strategii Transakcyjnych")

class StrategyPlot:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.container = st.empty()

    def update(self, df_data, df_strategy_results):

        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.03)
        fig.add_trace(go.Scatter(x=df_data.index,
            open=df_data[CANDLESTICK["OPEN"]],
            high=df_data[CANDLESTICK["HIGH"]],
            low=df_data[CANDLESTICK["LOW"]],
            close=df_data[CANDLESTICK["CLOSE"]],
            name="Cena"))

        buy = df_strategy_results[df_strategy_results[self.strategy_name] == 1]
        if not buy.empty:
            fig.add_trace(go.Scatter(x=buy.index,
                y=df_data.loc[buy.index, CANDLESTICK["LOW"]]*0.99,
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='blue', line=dict(color='white', width=2)),
                name="Buy"
            ))

        sells = df_strategy_results[df_strategy_results[self.strategy_name] == -1]
        if not sells.empty:
            fig.add_trace(go.Scatter(
                x=sells.index,
                y=df_data.loc[sells.index, 'high'] * 1.01,
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='#ff0000', line=dict(width=2, color='white')),
                name='SPRZEDAŻ'
            ))

        fig.update_layout(
            title=f"Strategia: {self.strategy_name}",
            xaxis_rangeslider_visible=False,
            height=600,
            template="plotly_dark",
            margin=dict(l=10, r=10, t=40, b=10)
        )
        self.container.plotly_chart(fig, use_container_width=True)

        # Dodanie linii wskaźnika (jeśli istnieje w df_data)
        # if self.strategy_name in df_data.columns:
        #     fig.add_trace(go.Scatter(
        #         x=df_data.index,
        #         y=df_data[self.strategy_name],
        #         line=dict(color='yellow', width=1.5),
        #         name=self.strategy_name
        #     ))


    #TODO -- DOCELOWO  dashboard.py:
