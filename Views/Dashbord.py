import streamlit as st
import pandas as pd
import time
from Logic.Managers.UserManager import UserManager
from Logic.Plots import *
from Data.Database import *
from Data.Market import *
Data_Range = 200
Simulation_Range = 50

st.set_page_config(page_title="RBIS", layout="wide")

# TODO __ INICJALIZACJA SESJI

if 'db' not in st.session_state:
    st.session_state.db = Database()
    st.session_state.market_repo = MarketRepository(st.session_state.db)

if 'user_manager' not in st.session_state:
    #TODO __ POZNIEJSZE PRZEPIECIE LOGIGI Z BAZY
    default_config_path = "../Logic/Static/config.yaml"
    # default_asset_path = "Data/HistoricValues/ndaq_us.csv"
    ticker = "NDAQ"

    try:
        #TODO __ DO PRZYSZLEJ POPRAWY __ NARAZIE ZMAPOWANE POD SIMULATION
        market_repo = st.session_state.market_repo
        full_df = market_repo.get_candles(ticker).tail(Data_Range)

        if full_df.empty:
            st.error("pusty ticker")
            st.stop()

        # full_df = pd.read_csv(default_asset_path, sep=None, engine='python').tail(Data_Range)

        st.session_state.full_df = full_df
        st.session_state.asset_data = full_df.head(Data_Range-Simulation_Range)
        st.session_state.simulation_step = 0
    except Exception as e:
        st.error(f"Błąd ładowania danych z bazy: {e}")
        st.stop()

    starting_user = UserManager(default_config_path, asset_data=st.session_state.asset_data)
    starting_user.calculate_init(Data_Range)

    st.session_state.user_manager = starting_user

if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False

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
        df = st.session_state.full_df

        new_tick = Data_Range + st.session_state.simulation_step - Simulation_Range
        print(f"df len __ {len(df)}")
        print(f"New tick __ {new_tick}")

        if new_tick < len(df):
            for i in range(new_tick, Data_Range):
                if not st.session_state.simulation_running:
                    break

                new_candle = df.iloc[[i]]
                u_manager.calculate_new_candle(new_candle)
                st.session_state.simulation_step += 1

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