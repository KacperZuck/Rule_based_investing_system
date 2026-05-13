import numpy as np
import pandas as pd
from Logic.Static.maps import SIGNALS_MAP, BUY, SELL, NEUTRAL

class Indicator:
    def __init__(self,name,params,columns):
        self.name = name
        self.params = params
        self.columns = columns
        self.results = pd.DataFrame() # do przechowywania dancyh
        self.last_signal = NEUTRAL

    def count(self, df):
        raise NotImplementedError(f"Indicator {self.name} not implemented")

    def update(self, new_data):
        raise NotImplementedError(f"Indicator {self.name}, lacking update function")

    def add_signal(self, logic_type, logic_params, all_results):
        logic_func = getattr(self, SIGNALS_MAP[logic_type])
        sig_col = f"{self.name}_signal"

        # 1. Pobieramy surowy stan (bloki 1, -1, 0)
        raw_state = logic_func(logic_params, all_results)

        # 2. Toggle historyczny (Filtrowanie duplikatów stanu)
        final_signals = pd.Series(NEUTRAL, index=raw_state.index)
        current_state = NEUTRAL

        # Iterujemy, aby wyłapać tylko faktyczne zmiany trendu (1 -> 0 -> 1 traktujemy jako powtórkę)
        # Jeśli chcesz, aby powrót do 0 resetował możliwość wystawienia 1, użyj poprzedniej wersji.
        # Ta wersja wymusza: 1 -> 0 -> 0 -> -1 (tylko zmiana kierunku generuje sygnał)
        for idx, val in raw_state.items():
            if val != NEUTRAL and val != current_state:
                final_signals.loc[idx] = val
                current_state = val
            elif val == -current_state:  # Obsługa natychmiastowego odwrócenia
                final_signals.loc[idx] = val
                current_state = val

        # 3. Synchronizacja stanu Live
        self.last_signal = current_state

        # 4. Zapis
        self.results = pd.DataFrame({
            self.name: all_results[self.name],
            sig_col: final_signals.astype(int)
        }, index=all_results.index)

        return self.results[[sig_col]]

    def update_signal(self, logic_type, logic_params, all_results):
        sig_col = f"{self.name}_signal"
        logic_func = getattr(self, SIGNALS_MAP[logic_type])

        # Pobierz surowy stan (obecna strefa)
        raw_val = logic_func(logic_params, all_results).iloc[-1]

        # Logika Toggle Live: Emituj tylko przy zmianie na inny NIEZEROWY sygnał
        final_val = NEUTRAL
        if raw_val != NEUTRAL and raw_val != self.last_signal:
            final_val = raw_val
            self.last_signal = raw_val
        # Opcjonalnie: jeśli chcesz resetować last_signal po powrocie do strefy neutralnej,
        # odkomentuj poniższą linię (wtedy 1 -> 0 -> 1 znowu da sygnał):
        # elif raw_val == NEUTRAL: self.last_signal = NEUTRAL

        last_idx = all_results.index[-1]
        if self.results is None or self.results.empty:
            self.results = pd.DataFrame({self.name: [all_results[self.name].iloc[-1]], sig_col: [final_val]},
                                        index=[last_idx])
        else:
            self.results.loc[last_idx, [self.name, sig_col]] = [all_results[self.name].iloc[-1], final_val]

        return self.results[[sig_col]].iloc[[-1]]

    def logic_threshold(self, p, all_results):
        s = all_results[self.name]
        cond_buy = s < p.get('low', -np.inf)
        cond_sell = s > p.get('high', np.inf)
        return pd.Series(np.select([cond_buy, cond_sell], [BUY, SELL], default=NEUTRAL), index=all_results.index)

    def logic_crossover(self, p, all_results):
        a = all_results[self.name]
        target = p.get('target')
        b = all_results[target] if target in all_results.columns else p.get('value', 0)

        if isinstance(b, pd.Series): b = b.reindex(a.index)

        # Crossover z definicji jest impulsem (opiera się na zmianie relacji a/b)
        buy = (a > b) & (a.shift(1) <= b.shift(1) if isinstance(b, pd.Series) else b)
        sell = (a < b) & (a.shift(1) >= b.shift(1) if isinstance(b, pd.Series) else b)

        return pd.Series(np.select([buy, sell], [BUY, SELL], default=NEUTRAL), index=all_results.index)