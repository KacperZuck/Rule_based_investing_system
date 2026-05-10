import numpy as np
import pandas as pd
from Logic.maps import SIGNALS_MAP, BUY, SELL, NEUTRAL

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

    def logic_threshold(self, p, all_results):
        """Logika progowa: RSI < 30 itd."""
        if isinstance(self.results, pd.DataFrame):
            series = self.results[self.name]
        else:
            series = self.results
        low = p.get('low', -np.inf)
        high = p.get('high', np.inf)

        conds = [(series < low), (series > high)]
        return np.select(conds, [BUY, SELL], default=NEUTRAL)

    def logic_crossover(self, p, all_results):
        """Logika przecięcia: Ten wskaźnik vs Inny wskaźnik"""
        if isinstance(self.results, pd.DataFrame):
            line_a = self.results[self.name].squeeze()
        else:
            line_a = self.results.squeeze()
        target_name = p.get('target')  # np. "SMA50"

        if all_results is not None and target_name in all_results.columns:
            line_b = all_results[target_name]
        else:
            line_b = p.get('value', 0)
        if isinstance(line_b, pd.Series):
            line_b = line_b.reindex(line_a.index)

        prev_a = line_a.shift(1)
        prev_b = line_b.shift(1) if isinstance(line_b, pd.Series) else line_b

        valid_mask = line_a.notna() & (line_b.notna() if isinstance(line_b, pd.Series) else True)

        cond_buy = (line_a > line_b) & (prev_a <= prev_b) & valid_mask
        cond_sell = (line_a < line_b) & (prev_a >= prev_b) & valid_mask

        res_array = np.select([cond_buy, cond_sell], [BUY, SELL], default=NEUTRAL)
        return pd.Series(res_array, index=line_a.index)