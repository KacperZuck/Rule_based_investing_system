from idlelib import query

import pyodbc
import pandas as pd
from datetime import datetime


# KOLORY dla info
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


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
                print(f"{RED}[ERROR]{RESET} podczas łączenia z bazą SQL: {e}")
                raise e
        return self.conection

    def close(self):
        """Zamyka bezpiecznie połączenie."""
        if self.conection and not self.conection.closed:
            self.conection.close()
