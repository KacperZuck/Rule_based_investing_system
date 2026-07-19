import os

import pandas as pd
import yaml

from Logic.Managers.Manager import Manager


class UserManager(Manager):
    def __init__(self, strategy_repo, asset_data: pd.DataFrame = None, ticker: str = None):
        # super().__init__(config_path)
        # self.user_id = "admin"
        self.df = asset_data
        self.ticker = ticker
        self.strategy_repo = strategy_repo

        self.strategies = {}
        self.indicators = {}
        self.config_db = {}

    def load_config(self):

        df_strategies = self.strategy_repo.get_strategies()

        #TODO __ wybranie tych public oraz już zapisanych z id użytkownka

    def calculate_init(self,range):

        #TODO NARAZIE Z TAIL
        # df = pd.read_csv(self.asset).tail(range)
        df = self.asset.head(range-50)
        print(f"Wielkosc danych przed calc {len(df)}")
        self.calculate(df)
        self.calculate_signals(df)

    #def load_user_data(self, path_save):

    def save_user_data(self, path_save):

        config = self.get_strategies_config()
        user_config = {
            "user_id": getattr(self, "user_id", "Guest"),
            "path_asset": self.asset,
            "config": config
        }

        directory = os.path.dirname(path_save)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(path_save, "w") as f:
            yaml.dump(user_config, f)