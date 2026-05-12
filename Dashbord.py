import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from Logic.Managers.UserManager import UserManager
from Logic.maps import CANDLESTICK
from Logic.SideBar import *

Data_Range = 200
Simulation_Range = 50

st.set_page_config(page_title="RBIS", layout="wide")
# TODO __ INICJALIZACJA SESJI
if 'user_manager' not in st.session_state:
    default_config_path = "Logic/config.yaml"
    default_asset_path = "Data/ndaq_us.csv"

    try:
        #TODO __ DO PRZYSZLEJ POPRAWY __ NARAZIE ZMAPOWANE POD SIMULATION
        full_df = pd.read_csv(default_asset_path, sep=None, engine='python').tail(Data_Range)
        st.session_state.asset_data = full_df.head(Data_Range-Simulation_Range)
        st.session_state.simulation_step = 0
    except Exception as e:
        st.error(f"Błąd ładowania danych CSV: {e}")
        st.stop()

    starting_user = UserManager(default_config_path, default_asset_path)
    starting_user.calculate_init(Data_Range)

    st.session_state.user_manager = starting_user

if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False


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


# TODO __ PETLA
selected_strat, time_speed = main_sidebar()

if not st.session_state.simulation_running:
    if st.sidebar.button("Uruchom symualcje", key="btn_start"):
        st.session_state.simulation_running = True
        st.rerun()
else:
    if st.sidebar.button("Zatrzymaj symulacje", key="btn_stop"):
        st.session_state.simulation_running = False
        st.rerun()

if selected_strat:
    plotter = StrategyPlot(selected_strat, st.session_state.user_manager)

    if st.session_state.simulation_running:
        u_manager = st.session_state.user_manager
        df = pd.read_csv("Data/ndaq_us.csv").tail(Data_Range)

        new_tick = Data_Range + st.session_state.simulation_step - Simulation_Range
        print(f"df len __ {len(df)}")
        print(f"New tick __ {new_tick}")

        for i in range(new_tick, Data_Range):
            if not st.session_state.simulation_running:
                break;
            new_candle = df.iloc[[i]]
            u_manager.calculate_new_candle(new_candle)
            st.session_state.simulation_step += 1
            # plotter = StrategyPlot(selected_strat, u_manager)
            plotter.create()
            if time_speed > 0:
                time.sleep(time_speed)
    else:
        plotter.create()

else:
    st.warning("Brak wyboru strategii")

st.write("### Debug Info")
st.write(f"Liczba wskaźników: {len(st.session_state.user_manager.indicators)}")
st.write(f"Dostępne strategie: {list(st.session_state.user_manager.strategies.keys())}")

# --- DEBUG SECTION ---
# with st.expander("🔍 System Debugger - Stan wskaźników i strategii"):
#     u_manager = st.session_state.user_manager
#
#     col1, col2 = st.columns(2)
#     with col1:
#         st.write("**Aktywne Wskaźniki:**")
#         for name, ind_obj in u_manager.indicators.items():
#             # Pokazuje nazwę i ostatnią obliczoną wartość
#             last_val = ind_obj.results.iloc[-1].to_dict() if not ind_obj.results.empty else "Brak danych"
#             st.text(f"• {name}: {last_val}")
#
#     with col2:
#         st.write("**Aktywne Strategie:**")
#         for name, strat_obj in u_manager.strategies.items():
#             st.text(f"• {name} (Sygnały: {len(strat_obj.signal_configs)})")
#
#     st.write("**Ostatnie wyniki strategii (df_strategy_results):**")
#     if not u_manager.df_strategy_results.empty:
#         st.dataframe(u_manager.df_strategy_results.tail(5))
#     else:
#         st.warning("Brak wygenerowanych sygnałów w df_strategy_results")