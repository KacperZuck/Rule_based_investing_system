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
        if not self.conection or self.conection.closed:
            try:
                self.conection = pyodbc.connect(self.conection_str)
            except Exception as e:
                print(f"Błąd podczas łączenia z bazą SQL: {e}")
                raise e
        return self.conection

    def close(self):
        """Zamyka bezpiecznie połączenie."""
        if self.conection and not self.conection.closed:
            self.conection.close()

# ============================================================================
# PRZYKŁAD UŻYCIA W KODZIE
# ============================================================================
# if __name__ == "__main__":
#     db = Database()
#
#     print("Łączenie z bazą...")8
#     if db.connect():
#         print("Połączono pomyślnie!")
#
#         # 1. Pobieranie danych giełdowych do Pandas
#         print("\nPobieram świece dla NDAQ (1d)...")
#         df_candles = db.get_candles('NDAQ', '1d')
#
#         if not df_candles.empty:
#             print(f"Pobrano {len(df_candles)} rekordów. Podgląd danych:")
#             print(df_candles.tail(3))  # Wyświetla 3 ostatnie świece
#         else:
#             print("Brak danych lub błąd zapytania.")
#
#         # 2. Rejestracja przykładowej transakcji
#         # Zakładamy, że w tabeli Assets istnieje już rekord id_assets = 1 (np. pozycja NDAQ dla użytkownika)
#         print("\nRejestruję przykładową transakcję kupna (BUY)...")
#         success = db.register_transaction(id_assets=1, trans_type='BUY', qty=10.0, price=162.50)
#
#         if success:
#             print("Transakcja zapisana w tabeli [Transaction]!")
#         else:
#             print("Nie udało się zapisać transakcji (sprawdź czy id_assets = 1 istnieje w bazie).")
#
#         # Zamykamy połączenie
#         db.close()