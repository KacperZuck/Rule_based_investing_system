import warnings

import pandas as pd
from streamlit import cursor
import warnings

from Data.Database import *

class MarketRepository():
    def __init__(self, db : Database):
        self.db = db


    def get_candles(self, ticker: str) -> pd.DataFrame:

        cont = self.db.connect()

        query = """
                SELECT CAST(c.time_stamp AS VARCHAR(50)) AS time_stamp, c.[open], c.[high], c.[low], c.[close], c.volume
                FROM Candle c JOIN Instrument i ON c.id_instrument = i.id_instrument
                WHERE i.ticker = ? ORDER BY c.time_stamp ASC """

        try:
            # Blokujemy ostrzeżenie Pandas dotyczące braku silnika SQLAlchemy
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Przekazujemy wyciągnięte wcześniej id_instrument oraz timeframe_code
                df = pd.read_sql(query, cont, params=[ticker])

            if not df.empty:
                df['time_stamp'] = pd.to_datetime(df['time_stamp'])
                df.set_index('time_stamp', inplace=True)
            else:
                print(f"{YELLOW}[INFO]{RESET} brak tickera {ticker} w bazie")
            return df
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} pobierania świec z bazy: {e}")
            return pd.DataFrame()


    def get_all_instruments(self) -> pd.DataFrame:

        cont = self.db.connect()
        query = ("SELECT id_instrument, ticker, [name] FROM Instrument ORDER BY id_instrument ASC")

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                data = pd.read_sql(query, cont)

            if not data.empty:
                return data

        except Exception as e:
            print(f"{RED}[ERROR]{RESET} blad podczas odpytywania o instrumenty: {e}")
        return pd.DataFrame()

    def get_instrument(self, ticker: str) -> pd.DataFrame:

        cont = self.db.connect()
        cursor = cont.cursor()

        try:
            cursor.execute("SELECT id_instrument, ticker, name FROM Instrument WHERE ticker = ?", (ticker,))
            data = cursor.fetchone()

            if not data:
                print(f"{RED}[ERROR]{RESET}: Nie znaleziono instrumentu o tickerze '{ticker}' w słowniku Instrument.")
                return pd.DataFrame()

            return {"id_instrument": data[0], "ticker": data[1], "name": data[2]}
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas sprawdzania ID instrumentu: {e}")
            return pd.DataFrame()

    def get_instruments_main_page(self):
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """ SELECT i.id_instrument, i.ticker, i.[name], c.[high], c.[low], c.[close]
            FROM Instrument i AND Candle c WHERE i.id_instrument = c.id_instrument
            ORDER BY c.time_stamp TOP 1 ASC """

        try:
            cursor.execute(query)
            data = cursor.fetchall()

            if not data:
                print(f"{RED}[ERROR]{RESET}: blad przy pobieraniu danych dla main page")
                return pd.DataFrame()

            return {"id_instrument": data[0], "ticker": data[1], "name": data[2],
                    "high": data[3], "low": data[4], "close": data[5]}
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas zapytania o pobranie instrumentow dla main page: {e}")
            return pd.DataFrame()
