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
        # Używamy INNER JOIN zamiast AND w klauzuli FROM
        query = """
                SELECT c.[code], c.[name], s.[type]
                FROM Indicator i
                         JOIN [Source] s \
                ON i.id_source = s.id_source
                    JOIN [Code] c ON i.id_code = c.id_code
                ORDER BY i.id_indicator ASC \
                """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_sql(query, cont)
            return df
        except Exception as e:
            print(f"[ERROR] przy odczytywaniu wskaźników dla main page: {e}")
            return pd.DataFrame()

    def get_strategies_main_page(self) -> pd.DataFrame:
        cont = self.db.connect()
        # Używamy LEFT JOIN oraz GROUP BY, ponieważ używamy agregacji COUNT()
        query = """
                SELECT s.id_strategy, \
                       s.[name], \
                       s.thresholdBuy, \
                       s.thresholdSell, \
                       COUNT(sig.id_signalconfig) AS signals
                FROM Strategy s
                         LEFT JOIN SignalConfig sig ON s.id_strategy = sig.id_strategy
                WHERE s.[public] = 1
                GROUP BY s.id_strategy, s.[name], s.thresholdBuy, s.thresholdSell
                ORDER BY s.id_strategy ASC \
                """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_sql(query, cont)
            return df
        except Exception as e:
            print(f"[ERROR] przy odczytywaniu strategii dla main page: {e}")
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

    def get_signal_config_details(self, id_strategy: int) -> pd.DataFrame:
        """Pobiera sub-tabelę sygnałów dla strategii, zastępując ID czytelnymi nazwami."""
        cont = self.db.connect()
        query = """
                SELECT '[' + c.[code] + '] ' + c.[name] AS [Wskaźnik], 
                        CASE 
                            WHEN tc.[code] IS NOT NULL THEN l.[type] + ' (' + tc.[code] + ')'
                            ELSE l.[type]
                END \
                AS [Logika], 
                        sc.thresholdLow AS [Próg Dolny], 
                        sc.thresholdHigh AS [Próg Górny]
                    FROM SignalConfig sc
                    JOIN Indicator i ON sc.id_indicator = i.id_indicator
                    JOIN [Code] c ON i.id_code = c.id_code
                    JOIN Logic l ON sc.id_logic = l.id_logic
                    LEFT JOIN Indicator ti ON sc.targetIndicatorId = ti.id_indicator
                    LEFT JOIN [Code] tc ON ti.id_code = tc.id_code
                    WHERE sc.id_strategy = ?
                """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_sql(query, cont, params=[id_strategy])
            return df
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} pobierania szczegółów sygnałów: {e}")
            return pd.DataFrame()