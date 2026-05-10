import pandas as pd

class Signal:
    def __init__(self, name, indicators, params):
        self.name = name
        self.indicators = indicators
        self.params = params
        self.results = pd.Series()

    def generate(self, df):
        "wektorowe obliczanie sygnalow"
        raise NotImplementedError("Klasa nie posiada implementacji")

    def update(self, new_df):
        "obliczenie na podstawie nowej swiecy"
        raise NotImplementedError("Klasa nie posiada update")
