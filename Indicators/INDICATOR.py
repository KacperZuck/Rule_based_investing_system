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
        self.last_signal = NEUTRAL

    def count(self, df):
        raise NotImplementedError(f"Indicator {self.name} not implemented")

    def update(self, new_data):
        raise NotImplementedError(f"Indicator {self.name}, lacking update function")

    def add_signal(self, logic_type, logic_params, all_results):
        if logic_type not in SIGNALS_MAP:
            raise ValueError(f"Nieznany typ logiki: {logic_type}")

        logic_func = getattr(self, SIGNALS_MAP[logic_type])
        sig_col = f"{self.name}_signal"

        # 1. Oblicz surową historię stanu (np. RSI ciągle < 30 -> -1)
        # Przekazujemy all_results, gdzie Manager trzyma historię cen
        raw_signals_state = logic_func(logic_params, all_results)

        # 2. OSTATECZNY TOGGLE HISTORYCZNY (Usunięcie bloków)
        # Tworzymy maskę zmian: sygnał jest inny niż poprzedni.
        # fillna(True) na shift gwarantuje, że pierwszy wiersz zawsze zostanie.
        mask = raw_signals_state != raw_signals_state.shift(1).fillna(NEUTRAL)

        # Gdzie zmiana, zostaw surowy. Gdzie brak zmiany, wstaw 0 (NEUTRAL).
        # Używamy np.where, bo bywa szybsze niż .where() w Pandas przy dużych danych
        clean_signals_array = np.where(mask, raw_signals_state, NEUTRAL)

        # Tworzymy czystą Series z poprawnym indeksem
        final_history_signals = pd.Series(clean_signals_array, index=raw_signals_state.index, name=sig_col)

        # 3. Ustawienie stanu dla Live Trading
        # Pobieramy ostatni NIEZEROWY sygnał z czystej historii
        non_zero = final_history_signals[final_history_signals != NEUTRAL]
        self.last_signal = non_zero.iloc[-1] if not non_zero.empty else NEUTRAL

        # 4. Zapis wyników do wskaźnika
        # Używamy nazwy wskaźnika (np. 'RSI') i nazwy sygnału (np. 'RSI_signal')
        self.results = pd.DataFrame({
            self.name: all_results[self.name],
            sig_col: final_history_signals
        }, index=all_results.index)

        # Upewniamy się, że typy są poprawne (int dla sygnałów)
        self.results[sig_col] = self.results[sig_col].astype(int)

        return self.results[[sig_col]]

    def update_signal(self, logic_type, logic_params, all_results):
        sig_col = f"{self.name}_signal"
        logic_func = getattr(self, SIGNALS_MAP[logic_type])

        # Pobierz surowy stan dla najnowszej świecy (iloc[-1])
        raw_val = logic_func(logic_params, all_results).iloc[-1]

        # Toggle Live: emituj tylko jeśli stan surowy różni się od OSTATNIEGO WYSTAWIONEGO stanu
        final_val = NEUTRAL
        if raw_val != self.last_signal:
            final_val = raw_val
            # Aktualizujemy pamięć stanu live
            self.last_signal = raw_val

        # Zapisz do historii wewnętrznej (używając .loc)
        last_idx = all_results.index[-1]

        # Inicjalizuj results, jeśli Manager tego nie zrobił w add_signal
        if self.results is None or self.results.empty:
            self.results = pd.DataFrame({self.name: [all_results[self.name].iloc[-1]], sig_col: [final_val]},
                                        index=[last_idx])
        else:
            self.results.loc[last_idx, [self.name, sig_col]] = [all_results[self.name].iloc[-1], final_val]

        # Upewnij się, że kolumna sygnału to int
        self.results[sig_col] = self.results[sig_col].astype(int)

        return self.results[[sig_col]].iloc[[-1]]

    # --- PRYWATNE METODY LOGIKI ---

    def logic_threshold(self, p, all_results):
        # Ta funkcja ZAWSZE zwraca STAN (czyli bloki 1 lub -1)
        s = all_results[self.name]

        # Proste warunki bez maskowania shift
        cond_buy = s < p.get('low', -np.inf)
        cond_sell = s > p.get('high', np.inf)

        # numpy.select z default=0 generuje bloki danych (stan)
        return pd.Series(np.select([cond_buy, cond_sell], [BUY, SELL], default=NEUTRAL), index=all_results.index)

    def logic_crossover(self, p, all_results):
        # Crossover naturalnie generuje импульсы, bo porównuje z poprzednią świecą
        a = all_results[self.name]
        target = p.get('target')
        b = all_results[target] if target in all_results.columns else p.get('value', 0)

        # Jeśli B to Series, synchronizujemy
        if isinstance(b, pd.Series): b = b.reindex(a.index)

        prev_a = a.shift(1)
        prev_b = b.shift(1) if isinstance(b, pd.Series) else b

        buy = (a > b) & (prev_a <= prev_b)
        sell = (a < b) & (prev_a >= prev_b)

        # Upewniamy się, że nie ma sygnału, gdy dane są niepełne (np. pierwsza świeca)
        non_na_mask = a.notna() & prev_a.notna()
        if isinstance(b, pd.Series): non_na_mask &= b.notna() & prev_b.notna()

        return pd.Series(np.select([buy & non_na_mask, sell & non_na_mask], [BUY, SELL], default=NEUTRAL),
                         index=all_results.index)