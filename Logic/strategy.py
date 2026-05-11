import pandas as pd



#TODO PRZEKLEJONE Z CHATA __ TRZEBA POPRAWIC
class Strategy:
    def __init__(self, name, signal_configs, threshold_buy=1.0, threshold_sell=1.0):
        """
        :param name: Nazwa strategii (np. "Scalper_M1")
        :param signal_configs: Lista definicji sygnałów:
               [{"ind_type": "RSI", "ind_params": [14], "logic": "THRESHOLD", "logic_params": {...}}, ...]
        :param threshold: Próg głosowania (np. 0.7 dla 70%)
        """
        self.name = name
        self.signal_configs = signal_configs
        self.threshold_sell = threshold_sell
        self.threshold_buy = threshold_buy
        self.results = pd.Series()

    def run_voting(self, manager_df):
        """Zbiera kolumny sygnałowe wygenerowane przez managera i wylicza wynik końcowy."""
        sig_cols = [f"{conf['type']}{conf['params']}_signal" for conf in self.signal_configs]

        existing_cols = [col for col in sig_cols if col in manager_df.columns]
        if not existing_cols:
            return pd.Series(0, index=manager_df.index)

        signals_count = len(sig_cols)
        votes = manager_df[existing_cols]

        buy_sum = (votes == 1).sum(axis=1)
        sell_sum = (votes == -1).sum(axis=1)
        results = pd.Series(0, index=manager_df.index)

        results[((buy_sum/signals_count) >= self.threshold_buy) & (buy_sum > 0)] = 1
        results[((sell_sum/signals_count) >= self.threshold_sell) & (sell_sum > 0)] = -1

        self.results = results
        return self.results