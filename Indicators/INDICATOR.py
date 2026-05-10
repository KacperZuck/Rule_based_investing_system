import numpy as np
import pandas as pd
from maps import *

class Indicator:
    def __init__(self,name,params,columns):
        self.name = name
        self.params = params
        self.columns = columns
        self.results = pd.DataFrame() # do przechowywania dancyh

    def count(self, df):
        raise NotImplementedError(f"Indicator {self.name} not implemented")

    def update(self, new_data):
        raise NotImplementedError(f"Indicator {self.name}, lacking update function")

    def add_signal(self, logic_type, logic_params, all_indicators_results=None):
        """
        logic_type: klucz z SIGNALS_MAP (np. "CROSSOVER")
        logic_params: parametry (np. {"target": "SMA50"})
        all_indicators_results: DataFrame ze wszystkimi wyliczonymi wskaźnikami
        """
        if logic_type not in SIGNALS_MAP:
            raise ValueError(f"Nieznany typ logiki: {logic_type}")

        # Pobieramy nazwę funkcji z mapy i wywołujemy ją
        logic_func_name = SIGNALS_MAP[logic_type]
        logic_func = getattr(self, logic_func_name)

        sig_col_name = f"{self.name}_signal"
        self.results[sig_col_name] = logic_func(logic_params, all_indicators_results)
        return self.results[[sig_col_name]]

    # --- PRYWATNE METODY LOGIKI ---

    def _logic_threshold(self, p, all_results):
        """Logika progowa: RSI < 30 itd."""
        series = self.results[self.name]
        low = p.get('low', -np.inf)
        high = p.get('high', np.inf)

        conds = [(series < low), (series > high)]
        return np.select(conds, [BUY, SELL], default=NEUTRAL)

    def _logic_crossover(self, p, all_results):
        """Logika przecięcia: Ten wskaźnik vs Inny wskaźnik"""
        line_a = self.results[self.name]
        target_name = p.get('target')  # np. "SMA50"

        # Szukamy wartości drugiego wskaźnika
        if all_results is not None and target_name in all_results.columns:
            line_b = all_results[target_name]
        else:
            # Jeśli nie podano all_results lub nie ma tam wskaźnika,
            # może to być wartość stała podana w parametrach
            line_b = p.get('value', 0)

        # Przecięcie: 1 gdy A przecina B od dołu, -1 gdy od góry
        prev_a = line_a.shift(1)
        prev_b = line_b.shift(1) if isinstance(line_b, pd.Series) else line_b

        conds = [
            (line_a > line_b) & (prev_a <= prev_b),
            (line_a < line_b) & (prev_a >= prev_b)
        ]
        return np.select(conds, [BUY, SELL], default=NEUTRAL)

    # def set_signal(self, type, signal_params):
    #     " type z SIGNAL_MAP, signal_params dla wybranych parametrow"
    #
    #     if self.results is None:
    #         return
    #
    #     data_col = self.results[self.name]
    #     signal_col = f"{self.name}_signal"
    #
    #     if type == "CROSSOVER":
    #         for signal in self.results.columns:
    #             cross = self.results[signal]
    #             self.results[signal_col] = np.where(data_col > cross)
    #     elif type == "THRESHOLD":
    #         maxline = signal_params.get("maxline", np.inf)
    #         minline = signal_params.get("minline", -np.inf)
    #         condition = [ (data_col > maxline), (data_col < minline) ]
    #         value = [-1,1]
    #         self.results[signal_col] = np.select(condition, value, default=0)
    #     return self.results