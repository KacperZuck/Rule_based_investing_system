import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from Logic.UserManager import UserManager
from Logic.maps import CANDLESTICK, SIGNALS_MAP


Data_Range = 200
Simulation_Range = 50

st.set_page_config(page_title="RBIS", layout="wide")
# --- INICJALIZACJA SESJI ---
if 'user_manager' not in st.session_state:
    default_config_path = "Logic/config.yaml"
    default_asset_path = "Data/ndaq_us.csv"

    try:
        # Automatyczne wykrywanie separatora naprawia błąd "Expected 1 fields"
        full_df = pd.read_csv(default_asset_path, sep=None, engine='python')
        st.session_state.asset_data = full_df
        st.session_state.simulation_step = 0
    except Exception as e:
        st.error(f"Błąd ładowania danych CSV: {e}")
        st.stop()

    starting_user = UserManager(default_config_path, default_asset_path)
    starting_user.calculate_init(Data_Range)

    st.session_state.user_manager = starting_user

if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False


# --- SIDEBAR (Zarządzanie) ---
def render_sidebar():
    st.sidebar.header("Zarządzanie sesją")
    u_manager = st.session_state.user_manager

    # TODO -- STWORZ WLASNA
    # available_strats = list(u_manager.strategies.keys())
    # selected = st.sidebar.selectbox("Stwórz własną strategie", available_strats)
    #
    # st.sidebar.divider()

    available_strats = list(u_manager.strategies.keys())
    if not available_strats:
        st.sidebar.warning("Brak strategii")
        st.stop()
    selected = st.sidebar.selectbox("Wybierz dostepne strategie", available_strats)

    st.sidebar.divider()

    st.sidebar.subheader("Symulacja")
    speed = st.sidebar.slider("Prędkość [s]", 0.0, 4.0, 1.0)
    # st.sidebar.button("Uruchom symulacje")
    st.sidebar.divider()

    # Zapisywanie stanu
    if st.sidebar.button("Zapisz stan sesji"):
        save_file = f"Configs/config_{u_manager.user_id}.yaml"
        u_manager.save_user_data(save_file)
        st.sidebar.success(f"Sesja zapisana: {save_file}")

    return selected, speed

# --- LOGIKA RYSOWANIA ---
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
        buy = df_res[df_res[self.strategy_name] == 1]
        sell = df_res[df_res[self.strategy_name] == -1]

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
selected_strat, time_speed = render_sidebar()

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
        df = st.session_state.asset_data

        new_tick = Data_Range + st.session_state.simulation_step
        for i in range(new_tick, len(df)):
            if not st.session_state.simulation_running:
                break;
            new_candle = df.iloc[[new_tick]].copy()
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
