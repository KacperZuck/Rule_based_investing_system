import plotly.graph_objects as go
from plotly.subplots import make_subplots
from Logic.Static.maps import CANDLESTICK
from Logic.SideBar import *



class StrategyPlot:
    def __init__(self, strategy_name, manager):
        self.strategy_name = strategy_name
        self.manager = manager
        self.container = st.empty()

    def create(self):
        df_data = self.manager.df_data
        df_res = self.manager.df_strategy_results

        strategy_config = self.manager.strategies[self.strategy_name]
        signal = strategy_config.signal_configs[0]
        is_threshold = any(s['logic'] == 'THRESHOLD' for s in strategy_config.signal_configs)

        if is_threshold:
            fig = make_subplots(rows=1, cols=1)
            ind_name = f"{signal['type']}{signal['params']}"
            fig.add_trace(go.Scatter(
                x=df_data.index, y=df_data[ind_name], name=ind_name, line=dict(color='yellow')))

            low = signal['logic_params'].get('low')
            high = signal['logic_params'].get('high')
            if low is not None:
                fig.add_hline(y=low, line_dash="dash", line_color="green")
            if high is not None:
                fig.add_hline(y=high, line_dash="dash", line_color="red")
            self._render_signals(fig, df_data, df_res, y_axis_data=df_data[ind_name])
        else:
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Candlestick(
                x=df_data.index,
                open=df_data[CANDLESTICK["OPEN"]],
                high=df_data[CANDLESTICK["HIGH"]],
                low=df_data[CANDLESTICK["LOW"]],
                close=df_data[CANDLESTICK["CLOSE"]],
                name="Cena"
            ))

            self._render_signals(fig, df_data, df_res, y_axis_data=None)

        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        self.container.plotly_chart(fig)

    def _render_signals(self, fig, df_data, df_res, y_axis_data=None):
        current_res = df_res.loc[df_res.index.isin(df_data.index)]
        buy = df_res[current_res[self.strategy_name] == 1]
        sell = df_res[current_res[self.strategy_name] == -1]

        if y_axis_data is not None:
            y_buy = y_axis_data.loc[buy.index]
            y_sell = y_axis_data.loc[sell.index]
        else:
            y_buy = df_data.loc[buy.index, CANDLESTICK["CLOSE"]] * 0.98
            y_sell = df_data.loc[sell.index, CANDLESTICK["CLOSE"]] * 1.02

        if not buy.empty:
            fig.add_trace(go.Scatter(x=buy.index, y=y_buy,
                mode='markers', marker=dict(symbol='triangle-up', size=12, color='#00ff00'),name="Buy"))
        if not sell.empty:
            fig.add_trace(go.Scatter(x=sell.index, y=y_sell,
                mode='markers', marker=dict(symbol='triangle-down', size=12, color='#ff0000'),name="Sell"))
