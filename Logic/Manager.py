import os
import yaml
from Logic.strategy import Strategy
from Logic.maps import get_source_cols
from Logic.indicator_map import INDICATOR_MAP
import pandas as pd
import time
import json

class Manager():
    def __init__(self, path=None, config=None):
        self.indicators = {}
        self.strategies = {}
        self.df_data = pd.DataFrame()
        self.df_signals = pd.DataFrame()
        self.df_strategy_results = pd.DataFrame()

        if path and os.path.exists(path):
            self.load_config(path)
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
            i_class = INDICATOR_MAP.get(type)
            columns = get_source_cols(columns)
            self.indicators[unique_name] = i_class(unique_name, params, columns)

        return self.indicators[unique_name]

    def calculate(self, df):
        data = [df]
        for name, i in self.indicators.items():
            print(f"{name}__:")
            data.append(i.count(df))
        self.df_data = pd.concat(data, axis=1)
        return self.df_data

    def calculate_signals(self, price_df):

        signals_data = pd.DataFrame(index=price_df.index)

        for name, strategy in self.strategies.items():

            for config in strategy.signal_configs:

                i_name = f"{config['type']}{config['params']}"

                i = self.indicators[i_name]

                i.add_signal(
                    config['logic'],
                    config['logic_params'],
                    self.df_data
                )

                sig_col_name = f"{i_name}_signal"

                if (
                        isinstance(i.results, pd.DataFrame)
                        and sig_col_name in i.results.columns
                ):

                    signals_data[sig_col_name] = i.results[sig_col_name]

                elif (
                        isinstance(i.results, pd.Series)
                        and i.results.name == sig_col_name
                ):

                    signals_data[sig_col_name] = i.results

                else:

                    print(
                        f"Ostrzeżenie: "
                        f"Format wyników dla {i_name} jest nietypowy."
                    )

                    signals_data[sig_col_name] = 0

        final_signals = pd.DataFrame(index=price_df.index)

        for name, strategy in self.strategies.items():
            final_signals[strategy.name] = (
                strategy.run_voting(signals_data)
            )

        self.df_signals = signals_data

        self.df_strategy_results = final_signals

        return self.df_strategy_results

    def calculate_new_candle(self, df):
        new_values = []

        for name, i in self.indicators.items():
            new_values.append(i.update(df))

        new_candle = pd.concat([df] + new_values, axis=1)

        self.df_data = pd.concat(
            [self.df_data, new_candle],axis=0
        ).sort_index()

        new_signals = pd.DataFrame(index=df.index)

        for strat_name, strategy in self.strategies.items():

            for config in strategy.signal_configs:
                i_name = f"{config['type']}{config['params']}"
                i = self.indicators[i_name]

                print(f"    {i.name}__:")
                signal_update = i.update_signal(
                    config['logic'],
                    config['logic_params'],
                    self.df_data
                )

                signal_name = f"{i_name}_signal"
                new_signals.at[
                    df.index[0],
                    signal_name
                ] = signal_update.iat[0, 0]

        self.df_signals = pd.concat(
            [self.df_signals, new_signals],
            axis=0
        )

        new_vote = pd.DataFrame(index=df.index)

        for strat_name, strategy in self.strategies.items():
            vote_result = strategy.run_voting(
                self.df_signals
            )

            new_vote[strategy.name] = vote_result.iloc[-1]

        self.df_strategy_results = pd.concat(
            [self.df_strategy_results, new_vote],
            axis=0
        )

        return new_vote

    def simulate_newdata_for_all(self, Simulation):
        for new_tick in range(len(Simulation)):
            print(f"Testing {new_tick} new candle__:")
            new_indicators_row = self.calculate_new_candle(Simulation.iloc[[new_tick]])
            current_state = pd.concat([Simulation.iloc[[new_tick]], new_indicators_row], axis=1)
            # signal = signal_generator.check(current_state)
            # print(f"    {current_state.tail()}")
            # time.sleep(0.4)


    def add_strategy(self, name, signals_config, th_buy, th_sell):
        """Dodaje strategię i rejestruje jej wymagane wskazniki."""

        new_strategy = Strategy(name, signals_config, th_buy, th_sell)
        self.strategies[name] = new_strategy

        for config in signals_config:
            self.get_or_create_indicator(
                config['type'],
                config['params'],
                config.get('source', "CLOSE")
            )

    def load_config(self, path):
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        for indicator_config in data.get('types_of_indicators', []):
            self.get_or_create_indicator(
                indicator_config['type'],
                indicator_config['params'],
                indicator_config.get('source', "CLOSE")
            )
        for strategy in data.get('basic_trading_strategies', []):
            self.add_strategy(
                strategy['name'],
                strategy['signals'],
                strategy['threshold_buy'],
                strategy['threshold_sell']
            )

    def save_config(self, path):
        config = {
            "strategies": [
                {
                    "name": strategy.name,
                    "signals_config": strategy.signals_config,
                    "threshold_buy": strategy.th_buy,
                    "threshold_sell": strategy.th_sell
                } for strategy in self.strategies.values()
            ]
        }
        with open(path, "w") as f:
            yaml.dump(config, f)
