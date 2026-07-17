from idlelib import query

import pyodbc
import pandas as pd
from datetime import datetime


class Database:
    def __init__(self):
        # Parametry połączenia - dostosuj do swojego serwera
        self.server = 'localhost\\SQLEXPRESS'  # Twoja nazwa serwera MS SQL
        self.database = 'Regulowy_System_Inwestycyjny'

        # Connection String dla Windows Authentication (zaufane połączenie)
        self.conection_str = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"Trusted_Connection=yes;"
        )
        self.conection = None

    def connect(self):
        """Nawiązuje połączenie z bazą danych."""
        if not self.conection:
            try:
                self.conection = pyodbc.connect(self.conection_str)
            except Exception as e:
                print(f"Błąd podczas łączenia z bazą SQL: {e}")
                return None
        return self.conection

    def close(self):
        """Zamyka bezpiecznie połączenie."""
        if self.conection:
            self.conection.close()

    def get_candles(self, ticker: str) -> pd.DataFrame:
        """
        Pobiera świece dla danego instrumentu i interwału bezpośrednio do Pandas DataFrame.
        Idealne do analizy technicznej i rysowania wykresów.
        """
        self.connect()
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
            df = pd.read_sql(query, self.conection, params=[ticker])
            # Konwertujemy timestamp na index dla łatwiejszego liczenia wskaźników
            df['time_stamp'] = pd.to_datetime(df['time_stamp'])
            df.set_index('time_stamp', inplace=True)
            return df
        except Exception as e:
            print(f"Błąd pobierania danych: {e}")
            return pd.DataFrame()

    def register_transaction(self, id_assets: int, trans_type: str, qty: float, price: float) -> bool:
        """
        Rejestruje nową transakcję (BUY/SELL) w bazie danych w bezpieczny sposób (Parameterized Query).
        Zapobiega atakom SQL Injection.
        """
        self.connect()

        total_value = qty * price

        query = """
                INSERT INTO [Transaction] (id_assets, transaction_type, quantity, price, total_value, [timestamp])
                VALUES (?, ?, ?, ?, ?, ?) \
                """

        try:
            cursor = self.conection.cursor()
            # Wykonujemy zapytanie przekazując parametry w bezpieczny sposób (jako krotkę)
            cursor.execute(query, (id_assets, trans_type, qty, price, total_value, datetime.now()))

            # W transakcjach modyfikujących dane (INSERT/UPDATE/DELETE) musimy zatwierdzić zmiany!
            self.conection.commit()
            return True
        except Exception as e:
            print(f"Błąd podczas zapisu transakcji: {e}")
            self.conection.rollback()  # Wycofujemy zmiany w razie błędu
            return False

    def register_user(self, user_type:int, name:str, email:str, password:str) -> bool:
        self.connect()

        query = """
            INSERT INTO User (user_type, name, email, password) VALUES (?, ?, ?, ?)  
                """
        try:
            cursor = self.conection.cursor()
            cursor.execute(query, (user_type, name, email, password))

            self.conection.commit()
            return True
        except Exception as e:
            print(f"Blad podczas rejsetracji: {e}")
            self.conection.rollback()
            return False

    def login(self, name:str, email:str, password:str) -> bool:
        self.connect()
        query = """
            SELECT u.name, u.email, u.password FROM User AS u WHERE u.email = email AND u.password = password """
        try:
            data = pd.read_sql(query, self.conection, params=[name, email, password])
            if not data.empty:
                return True
        except Exception as e:
            print(f"Błąd zapytania dla logowania: {e}")
        return False

    def logout(self): # CHYBA NIE POTRZEBNE
        self.connect()
        return

    def add_strategy(self, name:str,public:bool, thresholdBuy:float, thresholdSell:float):
        self.connect()

        query = """
            INSERT INTO Strategy(name, public, thresholdBuy, thresholdSell) VALUES (?, ?, ?, ?, ?)
        """
        try:
            cursor = self.conection.cursor()
            cursor.execute(query, (name, public, thresholdBuy, thresholdSell))

            self.conection.commit()
            return True
        except Exception as e:
            print(f"Błąd podczas dodawania strategii do bazy: {e}")
            self.conection.rollback()
            return False

    def get_all_strategy(self) -> pd.DataFrame:
        self.connect()

        query = """
            SLECT * FROM Strategy ORDER BY id_strategy ASC 
            """
        try:
            data = pd.read_sql(query, self.conection)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Błąd podczas zapytania o wszstkie strategie: {e}")
        return pd.DataFrame()

    def add_signal_config(self):
        # id_strategy, id_indicator, id_logic, thresholdLow, thresholdHigh
        # id_strategy, id_indicator, id_logic, targetIndicatorId
        self.connect()
        return
    def change_signal_config(self):
        self.connect()
        return
    
# ============================================================================
# PRZYKŁAD UŻYCIA W KODZIE
# ============================================================================
if __name__ == "__main__":
    db = Database()

    print("Łączenie z bazą...")
    if db.connect():
        print("Połączono pomyślnie!")

        # 1. Pobieranie danych giełdowych do Pandas
        print("\nPobieram świece dla NDAQ (1d)...")
        df_candles = db.get_candles('NDAQ', '1d')

        if not df_candles.empty:
            print(f"Pobrano {len(df_candles)} rekordów. Podgląd danych:")
            print(df_candles.tail(3))  # Wyświetla 3 ostatnie świece
        else:
            print("Brak danych lub błąd zapytania.")

        # 2. Rejestracja przykładowej transakcji
        # Zakładamy, że w tabeli Assets istnieje już rekord id_assets = 1 (np. pozycja NDAQ dla użytkownika)
        print("\nRejestruję przykładową transakcję kupna (BUY)...")
        success = db.register_transaction(id_assets=1, trans_type='BUY', qty=10.0, price=162.50)

        if success:
            print("Transakcja zapisana w tabeli [Transaction]!")
        else:
            print("Nie udało się zapisać transakcji (sprawdź czy id_assets = 1 istnieje w bazie).")

        # Zamykamy połączenie
        db.close()