import pandas as pd
#import seaborn as sns
#import matplotlib as mpl
import yaml

from Logic.manager import Manager

Range = 200
Simulation = 100

if __name__ == "__main__":
    with open("Logic/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    df_export = pd.read_csv("Data/ndaq_us.csv").tail(Range)


    print("\nInicjacja menagera__:")
    manager = Manager(config["types_of_indicators"])

    print("\nObliczanie wskaźników__:")
    df_final = manager.calculate(df_export.head(Range-Simulation))

    print("\nWyswietlenie obliczen__:")
    print(df_final.tail())

    # plot_data(df_final)
    # irl
    print("Real data simulation__:")
    data_simulation = df_export.tail(Simulation)
    manager.simulate_newdata_for_all( data_simulation)

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