import os
import yaml
from Logic.maps import get_source_cols
from Logic.indicator_map import INDICATOR_MAP
from Logic.Managers.Strategy import Strategy
import pandas as pd


class Manager():
    def __init__(self, path=None, config=None):
        self.indicators = {}
        self.strategies = {}
        self.df_data = pd.DataFrame()
        self.df_signals = pd.DataFrame()
        self.df_strategy_results = pd.DataFrame()
        self.asset_path = path

        if path and os.path.exists(path):
            self.load_config(path)
        if config:
            self.setup_fromInit(config)

    def setup_fromInit(self, config):
        for i in config:
            source = i.get("source") or i.get("columns") or "CLOSE"
            self.get_or_create_indicator(
                i.get("type"),
                i.get("params", []),
                source
            )

    def get_or_create_indicator(self, type, params, columns="CLOSE"):
        """sprawdza czy wskaznik o tych parametrach juz istnieje."""
        if not isinstance(params, list):
            params = [params]

        unique_name = f"{type}{params}"

        if unique_name not in self.indicators:
            # 1. Pobieramy metadane z mapy
            indicator_meta = INDICATOR_MAP.get(type)

            # 2. To tutaj rzucało Twój błąd - upewnij się, że klucz istnieje
            if not indicator_meta:
                raise ValueError(f"Wskaznik {type} nie istnieje w INDICATOR_MAP. "
                                 f"Dostępne klucze: {list(INDICATOR_MAP.keys())}")

            # 3. Pobieramy KLASĘ z metadanych
            i_class = indicator_meta.get('class')

            if not i_class:
                raise TypeError(f"Błąd konfiguracji: {type} nie ma przypisanej klasy w mapie.")

            # 4. Przygotowanie źródła i inicjalizacja
            source_cols = get_source_cols(columns)
            self.indicators[unique_name] = i_class(unique_name, params, source_cols)

        return self.indicators[unique_name]

    def add_custom_strategy(self, name, signal_configs):
        """
        Tworzy strategię na podstawie listy konfiguracji sygnałów z GUI.
        signal_configs to lista słowników: {"type", "params", "logic", "logic_params"}
        """  # Import lokalny by uniknąć circular import

        # 1. Najpierw upewnij się, że wszystkie potrzebne wskaźniki istnieją
        for cfg in signal_configs:
            # Główny wskaźnik
            self.get_or_create_indicator(cfg['type'], cfg['params'])

            # Jeśli to CROSSOVER, musimy stworzyć też wskaźnik docelowy (target)
            if cfg['logic'] == "CROSSOVER":
                target = cfg['logic_params'].get('target')
                # Sprawdzamy czy target to wskaźnik (np. "SMA"), a nie "CLOSE"
                if target in INDICATOR_MAP:
                    t_params = cfg['logic_params'].get('target_params', [])
                    self.get_or_create_indicator(target, t_params)

        # 2. Tworzymy obiekt strategii (przekazujemy nazwę i konfigurację sygnałów)
        new_strategy = Strategy(name, signal_configs)
        self.strategies[name] = new_strategy

        # 3. Inicjalizujemy wyniki dla nowej strategii w DataFrame
        self.df_strategy_results[name] = 0
        return True

    def calculate(self, df):
        data = [df]
        for name, i in self.indicators.items():
            print(f"{name}__:")
            data.append(i.count(df))
        self.df_data = pd.concat(data, axis=1)
        # return self.df_data

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

        # return self.df_strategy_results

    def calculate_new_candle(self, df):
        active_indicator_names = set()
        for strategy in self.strategies.values():
            for config in strategy.signal_configs:
                i_name = f"{config['type']}{config['params']}"
                active_indicator_names.add(i_name)

        new_values = []
        for name in active_indicator_names:
            if name in self.indicators:
                new_values.append(self.indicators[name].update(df))

        new_candle = pd.concat([df] + new_values, axis=1)

        self.df_data = pd.concat(
            [self.df_data, new_candle],axis=0
        ).sort_index()

        new_signals = pd.DataFrame(index=df.index)

        for strat_name, strategy in self.strategies.items():

            for config in strategy.signal_configs:
                i_name = f"{config['type']}{config['params']}"
                i = self.indicators[i_name]

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
                print(f"    {signal_name}__:")

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
            axis=0)

        print(f"        {self.df_signals}")
        print(f"        {self.df_strategy_results}")
        return new_vote

    # def simulate_live(self, Simulation):
    #     for new_tick in range(len(Simulation)):
    #         print(f"Testing {new_tick} new candle__:")
    #         new_indicators_row = self.calculate_new_candle(Simulation.iloc[[new_tick]])
    #         # print(f"    {current_state.tail()}")
    #         time.sleep(0.5)


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
            raw_params = indicator_config.get('params', [])
            params = raw_params if isinstance(raw_params, list) else [raw_params]

            self.get_or_create_indicator(
                indicator_config['type'],
                params,
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
        config = {"strategies": self.get_strategies_config()}
        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    def get_strategies_config(self):
        """Generuje słownik parametrów wszystkich strategii bez zapisywania do pliku."""
        return [
            {
                "name": strategy.name,
                "signals": strategy.signal_configs,  # Zawiera parametry wskaźników
                "threshold_buy": strategy.threshold_buy,
                "threshold_sell": strategy.threshold_sell
            } for strategy in self.strategies.values()
        ]