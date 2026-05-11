import pandas as pd
from Logic.Manager import Manager
# import yfinance as yf # DANE DO POBRANIA

Range = 200
Simulation = 50
Config_path = "Logic/config.yaml"

def main():
    # with open("Logic/config.yaml", "r") as f:
    #     config = yaml.safe_load(f)
    df_export = pd.read_csv("Data/ndaq_us.csv").tail(Range)

    print("\nInicjacja menagera__:")
    manager = Manager(Config_path)

    print("\nObliczanie wskaźników__:")
    df = manager.calculate(df_export.head(Range-Simulation))

    print("\nObliczanie sygnalow__:")
    df_strategy = manager.calculate_signals(df_export.head(Range-Simulation))

    print("\nWyswietlenie strategi__:")
    print(df_strategy.tail(Range-Simulation), "\n", df)
    # plot_data(df_final)
    # irl
    print("\nWyswietlanie symulacji live data__:")
    data_simulation = df_export.tail(Simulation)
    manager.simulate_newdata_for_all( data_simulation)

    manager.save_config(Config_path)

if __name__ == "__main__":
    main()

    # for new_tick in Simulation:
    # #     new_candle = get_new_candle_from_exchange()
    #     new_indicators_row = manager.calculate_new_candle(new_tick)
    #
    #     current_state = pd.concat([new_tick, new_indicators_row], axis=1)

        # signal = signal_generator.check(current_state)


# for i in range(10):
#     new_candle = get_new_candle_from_exchange()  # pobiera 1 wiersz
#
#     new_data_row = manager.calculate_new_candle(new_candle)
#
#     df_final = pd.concat([full_df, new_data_row])
#
#     # Przykład: czy SMA20 przecina SMA50
#     df_final['Signal'] = SignalGenerator.sma_crossover(full_df, 'SMA20', 'SMA50')
#
#     latest_signal = full_df['Signal'].iloc[-1]
#     if latest_signal == 1:
#         print("Mamy sygnał KUPNA! Wyślij zlecenie...")
#     elif latest_signal == -1:
#         print("Mamy sygnał SPRZEDAŻY! Zamknij pozycję...")


# MonteCarlo.count(df)

# df_signals = pd.DataFrame({"Price":df["Zamkniecie"]})

# df.to_csv("wyniki.csv")
# print(df.info)
# print(df.head(Range))