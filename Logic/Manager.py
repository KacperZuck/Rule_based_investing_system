import json
import os
from time import sleep

from Indicators.INDICATOR import Indicator
from Logic.strategy import Strategy
from maps import *
import pandas as pd
import time

class Manager():
    def __init__(self, config, path):
        self.indicators = {}
        self.strategies = {}
        self.df_data = pd.DataFrame()
        self.df_signals = pd.DataFrame()

        if path and os.path.exists(path):
            self.load_config(config)
        if config:
            self.setup_fromInit(config)

    def setup_fromInit(self, config):
        for i in config:
            self.get_or_create_indicator(
                i.get("type"),
                i.get("params", []),
                i.get("columns", "CLOSE")
            )

    def get_or_create_indicator(self, type, params, columns):
        """sprawdza czy wskaznik o tych parametrach juz istnieje."""
        unique_name = f"{type}{params}"

        if unique_name not in self.indicators:
            i_class = INDICATOR_MAP[type]
            self.indicators[unique_name] = i_class(unique_name, params, columns)

        return self.indicators[unique_name]

    def calculate(self, df):
        data = [df]
        for name, i in self.indicators.items():
            print(f"{name}__:")
            data.append(i.count(df))
        self.df_data = pd.concat(data, axis=1)
        return self.df_data

    def calculate_signal(self, price_df):

        signals_data = pd.DataFrame(index=price_df.index)

        for name, strategy in self.strategies.items():
            for config in strategy.signal_configs:
                i_name = f"{config['type']}{config['params']}"
                i = self.indicators[i_name]
                i.add_signal(config['logic'], config['logic_params'], self.df_data)

                new_name = f"{i_name}_signal"
                signals_data[new_name] = i.results[new_name] #TODO IDK CZY DOBRZE

        final_signals = pd.DataFrame(index=price_df.index)
        temp_combined = pd.concat([self.df_data, signals_data], axis=1)

        for strat_name, strategy in self.strategies.items():
            final_signals[strategy.name] = strategy.run_voting(temp_combined)

        #TODO ZMIANA ABY FINAL VOTE BYL W INNEJ KOLUMNIE DLA STRATEGII, NIE ZLICZAL W SYGNALACH
        self.df_signals = pd.concat([signals_data, final_signals], axis=1)
        return self.df_signals

    def calculate_new_candle(self, df):
        data = [df]
        for name,i in self.indicators.items():
            print(f"    {name}__:")
            data.append(i.update(df))

        new_candle = pd.concat(data, axis=1)
        self.df_data = pd.concat([self.df_data, new_candle], axis=1)
        return new_candle

    def simulate_newdata_for_all(self, Simulation):
        index = 1
        for new_tick in range(len(Simulation)):
            print(f"Testing {index} new row__:")
            new_indicators_row = self.calculate_new_candle(Simulation.iloc[[new_tick]])
            current_state = pd.concat([Simulation.iloc[[new_tick]], new_indicators_row], axis=1)
            # signal = signal_generator.check(current_state)
            print(f"    {current_state.tail()}")
            time.sleep(1)
            index +=1


    def add_strategy(self, name, signals_config, th_buy, th_sell):
        """Dodaje strategię i rejestruje jej wymagane wskazniki."""

        new_strategy = Strategy(name, signals_config, th_buy, th_sell)
        self.strategies[name] = new_strategy

        for config in signals_config:
            self.get_or_create_indicator(
                config['type'],
                config['params'],
                config.get('columns', "CLOSE")
            )

    def load_config(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        for strategy in data.get("strategies", []):
            self.add_strategy(
                strategy['name'], strategy['signals_config'], strategy['th_buy', 1.0], strategy['th_sell',-1.0]
            )

    def save_config(self, path):
        config = {
            "strategies": [
                {
                    "name": strategy.name,
                    "signals_config": strategy.signals_config,
                    "th_buy": strategy.th_buy,
                    "th_sell": strategy.th_sell
                } for strategy in self.strategies.values()
            ]
        }
        with open(path, "w") as f:
            json.dump(config, f)