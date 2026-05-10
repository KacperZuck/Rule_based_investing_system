import pandas as pd



#TODO PRZEKLEJONE Z CHATA __ TRZEBA POPRAWIC
class Strategy:
    def __init__(self, name, signal_configs, threshold=1.0):
        """
        :param name: Nazwa strategii (np. "Scalper_M1")
        :param signal_configs: Lista definicji sygnałów:
               [{"ind_type": "RSI", "ind_params": [14], "logic": "THRESHOLD", "logic_params": {...}}, ...]
        :param threshold: Próg głosowania (np. 0.7 dla 70%)
        """
        self.name = name
        self.signal_configs = signal_configs
        self.threshold = threshold
        self.results = pd.Series()

    def run_voting(self, manager_df):
        """Zbiera kolumny sygnałowe wygenerowane przez managera i wylicza wynik końcowy."""
        # Pobieramy nazwy kolumn sygnałowych należących do tej strategii
        sig_cols = [f"{conf['ind_type']}_{conf['ind_params']}_signal" for conf in self.signal_configs]

        votes = manager_df[sig_cols]
        buy_ratio = (votes == 1).sum(axis=1) / len(sig_cols)
        sell_ratio = (votes == -1).sum(axis=1) / len(sig_cols)

        self.results = pd.Series(0, index=manager_df.index)
        self.results[buy_ratio >= self.threshold] = 1
        self.results[sell_ratio >= self.threshold] = -1
        return self.results