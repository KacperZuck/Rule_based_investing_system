import pandas as pd

from Logic.Manager import Manager


class UserManager(Manager):
    def __init__(self, config, user_strategies_config):
        super().__init__(config)
        self.user_strategies = []
        self.user_indicators = {}
        self.setup_strategies(user_strategies_config)

    def setup_strategies(self, strategies_config):
        "tworzy instancje strategii pobierajac z main"
        for strategy in strategies_config:
            for signal in strategy.get('signals', []):
                name = f"{signal['type']}{signal['params']}"
                if name not in self.indicators:
                    new_indicator = self.add_indicator_from_config(signal)
                    if new_indicator is not None:
                        self.user_indicators[name] = new_indicator

    def calculate(self, df):
        # z menagera
        base = super().calculate(df) #TODO __ NIE POTRZEBNIE OBLICZANE NA WSZYSTKICH WSKA

        user_result = []
        for name, i in self.user_indicators.items():
            user_result.append(i.count(df))

        if user_result:
            self.df_data = pd.concat([base] + user_result, axis=1)
        else:
            self.df_data = base
        return self.df_data