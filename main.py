from turtle import st

import pandas as pd
from Logic.Manager import Manager
# import yfinance as yf # DANE DO POBRANIA
from Logic.Plots import StrategyPlot
import time

Data_Range = 200
Simulation_Range = 50
Config_path = "Logic/config.yaml"

def run_app(manager):
    st.sidebar.header("Ustawienia")
    selected_strategy = st.sidebar.selectbox("Wybierz strategię",
                                             list(manager.strategies.keys()))

    speed = st.sidebar.slider("Prędkość symulacji (s)", 0.0, 0.5, 1.0, 2.0)

    viz = StrategyPlot(selected_strategy)
    if st.sidebar.button("Uruchom Symulację"):

        # print("\nWyswietlanie symulacji live data__:")
        # data_simulation = df_export.tail()
        df_export = pd.read_csv("Data/ndaq_us.csv").tail(Simulation_Range)
        for new_tick in range(len(Simulation_Range)):
            manager.calculate_new_candle(df_export.iloc[[new_tick]])

            viz.update(manager.df_data, manager.df_strategy_results)
            time.sleep(speed)

def init():
    df_export = pd.read_csv("Data/ndaq_us.csv").tail(Data_Range)

    print("\nInicjacja menagera__:")
    manager = Manager(Config_path)

    print("\nObliczanie wskaźników__:")
    manager.calculate(df_export.head(Data_Range-Simulation_Range))

    print("\nObliczanie sygnalow__:")
    manager.calculate_signals(df_export.head(Data_Range-Simulation_Range))

    # print("\nWyswietlenie strategi__:")
    # print(df_strategy.tail(Data_Range-Simulation_Range), "\n", df)

    # manager.simulate_live(data_simulation)
    manager.save_config(Config_path)
    return manager

if __name__ == "__main__":
    manager = init()
    run_app(manager)

# streamlit run Plots.py