
import pandas as pd
from streamlit import cursor

from Database import Database
import pyodbc
from datetime import datetime



class StrategiesRepository():
    def __init__(self, db: Database):
        self.db = db


    def add_strategy(self, name: str, public: bool, thresholdBuy: float, thresholdSell: float):
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """
                INSERT INTO Strategy(name, public, thresholdBuy, thresholdSell) \
                VALUES (?, ?, ?, ?, ?) \
                """

        try:
            cursor.execute(query, (name, 1 if public else 0, thresholdBuy, thresholdSell))
            self.conection.commit()
            return True
        except Exception as e:
            print(f"Błąd podczas dodawania strategii do bazy: {e}")
            cont.rollback()
        return False

    def get_all_strategy(self) -> pd.DataFrame:
        cont = self.db.connect()

        query = """
            SLECT * FROM Strategy ORDER BY id_strategy ASC 
            """
        try:
            data = pd.read_sql(query, cont)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Błąd podczas zapytania o wszstkie strategie: {e}")
        return pd.DataFrame()

    def get_signals_config(self, id_strategy: int) -> pd.DataFrame:
        """
        Pobiera kompletną architekturę logiczną sygnałów dla bota:
        Zwraca informacje o głównym wskaźniku, typie logiki oraz celach porównań (klucze obce).
        """
        cont = self.db.get_connection()
        query = """
                SELECT sc.id_signalconfig, \
                       sc.id_indicator AS main_indicator_id, \
                       l.[type]        AS logic_type, \
                       sc.thresholdLow, \
                       sc.thresholdHigh, \
                       sc.targetIndicatorId, \
                       sc.targetPriceField
                FROM SignalConfig sc
                         JOIN Logic l ON sc.id_logic = l.id_logic
                WHERE sc.id_strategy = ? \
                """
        return pd.read_sql(query, cont, params=[id_strategy])

    def save_signal_config(self, id_strategy:int, id_indicator:int, id_logic:int, low, float, hi):
        # id_strategy, id_indicator, id_logic, thresholdLow, thresholdHigh
        # id_strategy, id_indicator, id_logic, targetIndicatorId
        self.connect()
        return
    ## PROPOZYCJA
    #
    # def add_signal_config(self, id_strategy: int, id_indicator: int, id_logic: int,
    #                       threshold_low: float = None, threshold_high: float = None,
    #                       target_indicator_id: int = None, target_price_field: str = None) -> bool:
    #     """
    #     Zapisuje nową, modułową konfigurację sygnału dla danej strategii.
    #     Obsługuje dynamicznie oba typy logiki (THRESHOLD / CROSSOVER).
    #     """
    #     conn = self.db.get_connection()
    #     query = """
    #             INSERT INTO SignalConfig (id_strategy, id_indicator, id_logic, \
    #                                       thresholdLow, thresholdHigh, \
    #                                       targetIndicatorId, targetPriceField)
    #             VALUES (?, ?, ?, ?, ?, ?, ?) \
    #             """
    #     try:
    #         cursor = conn.cursor()
    #         # Przekazujemy parametry - jeśli są None, pyodbc automatycznie wstawi NULL do bazy
    #         cursor.execute(query, (
    #             id_strategy, id_indicator, id_logic,
    #             threshold_low, threshold_high,
    #             target_indicator_id, target_price_field
    #         ))
    #         conn.commit()
    #         return True
    #     except Exception as e:
    #         print(f"Błąd podczas dodawania SignalConfig: {e}")
    #         conn.rollback()
    #         return False
    #
    def save_strategy_signal(self, id_strategy:int, id_indicator:int, val:int): # sell 0, buy 1

        cont = self.db.connect()
        cursor = cont.cursor()

        query = """
            INSERT INTO StrategySignal(id_strategy, id_instrument, [timestamp], [value]) VALUES (?, ?, ?, ?)
        """

        try:
            cursor.execute(query, (id_strategy, id_indicator, datetime.now(),val))
            cont.commit()
            return True
        except Exception as e:
            print(f"Błąd przy próbie zapisu sygnału strategi (id={id_strategy}): {e}: ")
            cont.rollback()
        return False

    def get_all_indicators(self):
        cont = self.db.connect()
        query = """
            SELECT * FROM Indicator ORDER BY id_indicator ASC    
        """

        return pd.read_sql(query, cont)

    def get_indicator_parameters(self, id_indicator: int) -> dict:
        """Pobiera parametry wejściowe (np. okres N=14) dla konkretnego instancji wskaźnika."""
        conn = self.db.get_connection()
        query = "SELECT [name], [value] FROM IndicatorParameter WHERE id_indicator = ?"
        try:
            cursor = conn.cursor()
            cursor.execute(query, (id_indicator,))
            return {data[0]: data[1] for data in cursor.fetchall()}
        except Exception as e:
            print(f"Błąd pobierania parametrów wskaźnika {id_indicator}: {e}")
        return {}

Przykład wywołania zapisu nowego SignalConfig w kodzie:
Jeśli chcesz dodać strategię RSI (id=1), która ma sprawdzać wskaźnik RSI (id=3) z logiką THRESHOLD (id=1, np. bariery 30 i 70):

strategy_repo = StrategyRepository(db)
# Logika THRESHOLD
strategy_repo.add_signal_config(
    id_strategy=1,
    id_indicator=3,
    id_logic=1,
    threshold_low=30.0,
    threshold_high=70.0
)

# Logika CROSSOVER (np. strategia 2, wskaźnik EMA 9 id=2 przecina SMA 20 id=1)
strategy_repo.add_signal_config(
    id_strategy=2,
    id_indicator=2,
    id_logic=2,
    target_indicator_id=1
)