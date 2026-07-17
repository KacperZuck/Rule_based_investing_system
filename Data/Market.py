
import pandas as pd
from Database import Database

class MarketRepository():
    def __init__(self, db : Database):
        self.db = db


    def get_candles(self, ticker: str) -> pd.DataFrame:
        """
        Pobiera świece dla danego instrumentu i interwału bezpośrednio do Pandas DataFrame.
        Idealne do analizy technicznej i rysowania wykresów.
        """
        cont = self.db.connect()
        query = """
                SELECT c.time_stamp, c.[open], c.[high], c.[low], c.[close], c.volume
                FROM Candle c
                    JOIN Instrument i \
                ON c.id_instrument = i.id_instrument
                    JOIN TimeFrame t ON c.id_timeframe = t.id_timeframe
                WHERE i.ticker = ? AND t.code = ?
                ORDER BY c.time_stamp ASC \
                """

        try:
            # Pandas pozwala na bezpośrednie czytanie z zapytania SQL
            df = pd.read_sql(query, cont, params=[ticker])
            # Konwertujemy timestamp na index dla łatwiejszego liczenia wskaźników
            df['time_stamp'] = pd.to_datetime(df['time_stamp'])
            df.set_index('time_stamp', inplace=True)
            return df
        except Exception as e:
            print(f"Błąd pobierania danych: {e}")
            return pd.DataFrame()


# db = Database()
# market_repo = MarketRepository(db)
# df = market_repo.get_candles('NDAQ', '1d')
