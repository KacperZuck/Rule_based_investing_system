import pandas as pd

class Strategy:
    def __init__(self, name, signal_configs, threshold_buy=1.0, threshold_sell=1.0):

        self.name = name
        self.signal_configs = signal_configs
        self.threshold_sell = threshold_sell
        self.threshold_buy = threshold_buy
        self.results = pd.Series()
        self.owned_assets = 0

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
        result = pd.Series(0, index=manager_df.index)

        result[((buy_sum/signals_count) >= self.threshold_buy) & (buy_sum > 0)] = 1
        result[((sell_sum/signals_count) >= self.threshold_sell) & (sell_sum > 0)] = -1

        self.results = result
        if result is not None:
            if result.iloc[-1] == 1:
                self.buy_assets()
            elif result.iloc[-1] == -1:
                self.sell_assets()
        return self.results

    def sell_assets(self):
        return
    def buy_assets(self):
        return