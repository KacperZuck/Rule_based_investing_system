import warnings

import pandas as pd
from streamlit import cursor

from Data.Database import *
import pyodbc
from datetime import datetime



class StrategiesRepository():
    def __init__(self, db: Database):
        self.db = db

    def add_strategy(self, name: str, public: bool, thresholdBuy: float, thresholdSell: float):
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """
                INSERT INTO Strategy([name], [public], thresholdBuy, thresholdSell) \
                VALUES (?, ?, ?, ?) \
                """

        try:
            cursor.execute(query, (name, 1 if public else 0, thresholdBuy, thresholdSell))
            cont.commit()
            return cursor.execute("SELECT id_strategy FROM Strategy WHERE [name]=?", name).fetchone()[0]
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas dodawania strategii do bazy: {e}")
            cont.rollback()
        return False

    def get_all_strategy(self) -> pd.DataFrame:
        cont = self.db.connect()

        query = """
            SELECT * FROM Strategy ORDER BY id_strategy ASC 
            """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
            data = pd.read_sql(query, cont)
            if not data.empty:
                return data
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas zapytania o wszstkie strategie: {e}")
        return pd.DataFrame()

    def get_signals_config(self, id_strategy: int) -> pd.DataFrame:
        """
        Pobiera kompletną architekturę logiczną sygnałów dla bota:
        Zwraca informacje o głównym wskaźniku, typie logiki oraz celach porównań (klucze obce).
        """
        cont = self.db.connect()
        query = """
                SELECT sc.id_signalconfig, \
                       sc.id_indicator AS main_indicator_id, \
                       l.[type]        AS logic_type, \
                       sc.thresholdLow, \
                       sc.thresholdHigh, \
                       sc.targetIndicatorId
                FROM SignalConfig sc JOIN Logic l ON sc.id_logic = l.id_logic
                WHERE sc.id_strategy = ? \
                """
        return pd.read_sql(query, cont, params=[id_strategy])

    def save_signal_config(self, id_strategy: int, id_indicator: int, id_logic: int,
                          threshold_low: float = None, threshold_high: float = None,
                          target_indicator_id: int = None) -> bool:
        """
        Zapisuje nową, modułową konfigurację sygnału dla danej strategii.
        Obsługuje dynamicznie oba typy logiki (THRESHOLD / CROSSOVER).
        """
        conn = self.db.connect()
        query = """
                INSERT INTO SignalConfig (id_strategy, id_indicator, id_logic, \
                                          thresholdLow, thresholdHigh, \
                                          targetIndicatorId)
                VALUES (?, ?, ?, ?, ?, ?) \
                """
        try:
            cursor = conn.cursor()
            # Przekazujemy parametry - jeśli są None, pyodbc automatycznie wstawi NULL do bazy
            cursor.execute(query, (
                id_strategy, id_indicator, id_logic,
                threshold_low, threshold_high,
                target_indicator_id
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas dodawania SignalConfig: {e}")
            conn.rollback()
            return False

    def save_strategy_signal(self, id_strategy:int, id_indicator:int, val:int): # sell 0, buy 1

        cont = self.db.connect()
        cursor = cont.cursor()

        # query = """ INSERT INTO StrategySignal(id_strategy, id_instrument, [timestamp], [value]) VALUES (?, ?, ?, ?)"""

        query = """
                    MERGE StrategySignal AS target
                    USING (SELECT ? AS id_strategy, ? AS id_instrument, ? AS [timestamp], ? AS [value]) AS source
                    ON (target.id_strategy = source.id_strategy AND target.id_instrument = source.id_instrument)

                    WHEN MATCHED THEN 
                        UPDATE SET [timestamp] = source.[timestamp], [value] = source.[value]

                    WHEN NOT MATCHED THEN 
                        INSERT (id_strategy, id_instrument, [timestamp], [value])
                        VALUES (source.id_strategy, source.id_instrument, source.[timestamp], source.[value]);
                """

        try:
            cursor.execute(query, (id_strategy, id_indicator, datetime.now(),val))
            cont.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} przy próbie zapisu sygnału strategi (id={id_strategy}): {e}: ")
            cont.rollback()
        return False

    def get_all_indicators(self):
        cont = self.db.connect()
        query = """SELECT * FROM Indicator ORDER BY id_indicator ASC """

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                data = pd.read_sql(query, cont)
            if not data.empty:
                return data
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} przy odczytywaniu wszystkich indykatorow")
        return pd.DataFrame()

    def get_indicators_main_page(self) -> pd.DataFrame:
        cont = self.db.connect()
        cursor = cont.cursor()
        query = """SELECT c.[code], c.[name], s.[type]
                   FROM Indicator i AND [Source] s WHERE i.id_source = s.id_source 
                   AND [Code] c WHERE i.id_code = c.id_code
                   ORDER BY id_indicator ASC """

        try:
            cursor.execute(query)
            data = cursor.fetchone()

            if not data:
                print(f"{RED}[ERROR]{RESET}: Nie znaleziono danych")
                return pd.DataFrame()
            return {"code": data[0], "name": data[1], "type": data[2]}

        except Exception as e:
            print(f"{RED}[ERROR]{RESET} przy odczytywaniu wszystkich indykatorow")
        return pd.DataFrame()

    def get_strategies_main_page(self) -> pd.DataFrame:
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """ SELECT s.id_strategy, s.id_indicator,s.[name] s.threshold_low, s.threshold_high, COUNT(sig.id_strategy) AS signals
            FROM Strategy s AND SignalConfig sig WHERE s.id_source = sig.id_source AND s.public = 1
            ORDER BY s.id_strategy ASC
        """
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            if not data:
                print(f"{RED}[ERROR]{RESET}: Nie znaleziono danych dla strategi")
                return pd.DataFrame()
            return {"id_strategy": data[0], "id_indicator": data[1], "name": data[2],
                    "threshold_low": data[3], "threshold_high": data[4], "signals": data[5]}

        except Exception as e:
            print(f"{RED}[ERROR]{RESET} przy odczytywaniu wszystkich strategii main page")
        return pd.DataFrame()

    def get_indicator_parameters(self, id_indicator: int) -> dict:
        """Pobiera parametry wejściowe (np. okres N=14) dla konkretnego instancji wskaźnika."""
        cont = self.db.connect()
        query = "SELECT [name], [value] FROM IndicatorParameter WHERE id_indicator = ?"
        try:
            cursor = cont.cursor()
            cursor.execute(query, (id_indicator,))
            return {data[0]: data[1] for data in cursor.fetchall()}
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} pobierania parametrów wskaźnika {id_indicator}: {e}")
        return {}

# Przykład wywołania zapisu nowego SignalConfig w kodzie:
# Jeśli chcesz dodać strategię RSI (id=1), która ma sprawdzać wskaźnik RSI (id=3) z logiką THRESHOLD (id=1, np. bariery 30 i 70):
#
# strategy_repo = StrategyRepository(db)
# # Logika THRESHOLD
# strategy_repo.add_signal_config(
#     id_strategy=1,
#     id_indicator=3,
#     id_logic=1,
#     threshold_low=30.0,
#     threshold_high=70.0
# )
#
# # Logika CROSSOVER (np. strategia 2, wskaźnik EMA 9 id=2 przecina SMA 20 id=1)
# strategy_repo.add_signal_config(
#     id_strategy=2,
#     id_indicator=2,
#     id_logic=2,
#     target_indicator_id=1
# )