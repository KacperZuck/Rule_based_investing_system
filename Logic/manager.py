from time import sleep

from Indicators.INDICATOR import Indicator
from maps import *
import pandas as pd
import time

class Manager():
    def __init__(self, config):
        self.indicators = []
        self.setup(config)


    def setup(self, config):

        for i in config:
            ind_class = INDICATOR_MAP.get(i["type"])
            if ind_class:
                params = i.get("params", []) # jesli nie ma
                sources = i.get("source", "CLOSE")

                if sources == "CUSTOM":
                    try:
                        cols = i.get("colums", [])
                    except:
                        raise Exception(f"Invalid source {i['colums']}")
                else:
                    cols = get_source_cols(sources)
                # DEBUG
                print(f"Tworzę {i['type']}. Źródło: {sources}, Kolumny: {cols}")

                name = f"{i['type']}_{params[0] if params else ''}"
                instance = ind_class(name, params, cols)
                self.indicators.append(instance)

    def calculate(self, df):
        data = [df]

        for i in self.indicators:
            print(f"{i.name}__:")
            data.append(i.count(df))
        return pd.concat(data, axis=1)

    def calculate_new_candle(self, df):
        data = [df]
        for i in self.indicators:
            # print(f"    {i.name}__:")
            data.append(i.update(df))

        return pd.concat(data, axis=1)

    def simulate_newdata_for_all(self, Simulation):
        index = 1
        for new_tick in range(len(Simulation)):
            print(f"Testing {index} new row__:")
            new_indicators_row = self.calculate_new_candle(Simulation.iloc[[new_tick]])
            current_state = pd.concat([Simulation.iloc[[new_tick]], new_indicators_row], axis=1)
            # signal = signal_generator.check(current_state)
            print(f"    {current_state.tail()}")
            time.sleep(1)
            index +=1