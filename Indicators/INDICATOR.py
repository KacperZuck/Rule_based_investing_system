from logging import lastResort

import numpy as np
import pandas as pd
from Logic.maps import SIGNALS_MAP, BUY, SELL, NEUTRAL

class Indicator:
    def __init__(self,name,params,columns):
        self.name = name
        self.params = params
        self.columns = columns
        self.results = pd.DataFrame() # do przechowywania dancyh
        self.last_signal = 0

    def count(self, df):
        raise NotImplementedError(f"Indicator {self.name} not implemented")

    def update(self, new_data):
        raise NotImplementedError(f"Indicator {self.name}, lacking update function")

    def add_signal(self, logic_type, logic_params, all_results=None):
        """
        logic_type: klucz z SIGNALS_MAP (np. "CROSSOVER")
        logic_params: parametry (np. {"target": "SMA50"})
        all_indicators_results: DataFrame ze wszystkimi wyliczonymi wskaźnikami
        """
        if logic_type not in SIGNALS_MAP:
            raise ValueError(f"Nieznany typ logiki: {logic_type}")

        logic_func = getattr(self, SIGNALS_MAP[logic_type])
        sig_col = f"{self.name}_signal"

        raw = logic_func(logic_params, all_results)

        filtered = []
        last_nonzero = 0

        for val in raw:
            if val == 0:
                filtered.append(0)

            elif val == last_nonzero:
                filtered.append(0)

            else:
                filtered.append(val)
                last_nonzero = val

        final_history = pd.Series(filtered, index=raw.index, dtype=int)

        # 3. Ustawienie stanu dla przyszłej symulacji LIVE
        # Szukamy ostatniego sygnału różnego od zera w całej historii
        actual_signals = final_history[final_history != 0]
        self.last_signal = actual_signals.iloc[-1] if not actual_signals.empty else 0

        # 4. Zapis wyników
        self.results = pd.DataFrame(
            {self.name: all_results[self.name],
             sig_col: final_history},index=all_results.index)
        return self.results[[sig_col]]

    def update_signal(self, logic_type, logic_params, all_results):

        sig_col = f"{self.name}_signal"

        logic_func = getattr(self, SIGNALS_MAP[logic_type])

        raw_val = logic_func(
            logic_params,
            all_results
        ).iloc[-1]

        final_val = 0

        if pd.isna(raw_val):
            raw_val = 0
            self.last_signal = final_val

        last_idx = all_results.index[-1]

        new_row = pd.DataFrame(
            {
                self.name: [all_results[self.name].iloc[-1]],
                sig_col: [final_val]
            },
            index=[last_idx]
        )
        self.results = pd.concat(
            [self.results, new_row],
            axis=0
        )

        return new_row[[sig_col]]

    # TODO __ PRYWATNE METODY

    def logic_threshold(self, p, all_results):
        s = all_results[self.name]
        # Proste warunki: Kupuj gdy poniżej low, Sprzedaj gdy powyżej high
        conds = [s < p.get('low', -np.inf), s > p.get('high', np.inf)]
        return pd.Series(np.select(conds, [1, -1], 0), index=all_results.index)

    def logic_crossover(self, p, all_results):

        a = all_results[self.name]
        target = p.get('target')

        b = all_results[target] if target in all_results.columns else p.get('value', 0)

        if len(a) < 2:
            return pd.Series([0], index=all_results.index)

        a_prev, a_now = a.iloc[-2], a.iloc[-1]

        if isinstance(b, pd.Series):
            b_prev, b_now = b.iloc[-2], b.iloc[-1]
        else:
            b_prev = b_now = b

        buy = (a_now > b_now) and (a_prev <= b_prev)
        sell = (a_now < b_now) and (a_prev >= b_prev)

        val = 1 if buy else -1 if sell else 0
        return pd.Series([val])