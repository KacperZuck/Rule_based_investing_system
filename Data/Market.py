import warnings

import pandas as pd
from streamlit import cursor
import warnings

from Database import *

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

