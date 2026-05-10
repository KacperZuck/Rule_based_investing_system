import pandas as pd



#TODO PRZEKLEJONE Z CHATA __ TRZEBA POPRAWIC
class Strategy:
    def __init__(self, name, signal_configs, threshold_buy=1.0, threshold_sell=-1.0):
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
        # Pobieramy nazwy kolumn sygnałowych należących do tej strategii
        sig_cols = [f"{conf['ind_type']}{conf['ind_params']}_signal" for conf in self.signal_configs]

        # Pobieramy tylko istniejące kolumny
        existing_cols = [col for col in sig_cols if col in manager_df.columns]
        if not existing_cols:
            return pd.Series(0, index=manager_df.index)

        votes = manager_df[existing_cols]
        buy = (votes == 1).sum(axis=1) / len(sig_cols)
        sell = (votes == -1).sum(axis=1) / len(sig_cols)

        self.results = pd.Series(0, index=manager_df.index)
        self.results[buy >= self.threshold_buy] = 1
        self.results[sell >= self.threshold_sell] = -1
        return self.results