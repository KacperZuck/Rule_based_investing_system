from idlelib import query

import pandas as pd
from uvicorn.main import print_version

from Database import *
from datetime import datetime

class AssetsRepository():
    def __init__(self, db: Database):
        self.db = db


    def get_assets(self, id_user:int, id_instrument:int, id_strategy:int): ## TODO JESCZE DODAC NAME DLA INSTRUMENTU ABY NIE BYLO SAMYCH ID, CHYBA ZE PODZIELIC TO NA OSOBNE ZAPYTANIA ???
        cont = self.db.connect()

        query = """
            SELECT id_assets, id_instrument, id_strategy value FROM Assets WHERE id_assets = ? AND id_instrument = ? AND id_strategy = ?
        """

        try:
            cursor = cont.cursor()
            cursor.execute(query, (id_user, id_instrument, id_strategy))
            data = cursor.fetchall()
            if data:
                return
                # return {"id_asset": data[0], "": data[1], data[2]: data[3]}
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas pobierania pozycji: {e}")
        return False

    def get_user_position(self, id_user: int, id_instrument: int, id_strategy: int) -> dict or None:
        """Sprawdza, czy użytkownik ma otwartą pozycję dla danego waloru i strategii."""
        conn = self.db.connect()
        query = """
                SELECT id_assets, quantity, averagePrice, active, allocatedBalance
                FROM Assets
                WHERE id_user = ? AND id_instrument = ? AND id_strategy = ?\
                """
        try:
            cursor = conn.cursor()
            cursor.execute(query, (id_user, id_instrument, id_strategy))
            data = cursor.fetchone()
            if data:
                return {"id_assets": data[0], "quantity": float(data[1]), "averagePrice": float(data[2]),
                        "active": bool(data[3]), "allocatedBalance": float(data[4])}
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} pobierania pozycji: {e}")
        return None

    def get_portfolio_dashboard(self, id_user: int) -> pd.DataFrame:
        """Pobiera aktualny stan konta i akcji do wyświetlenia w tabeli Streamlit."""
        cont = self.db.connect()
        query = """
                SELECT i.ticker, i.[name], a.quantity, a.averagePrice, s.[name] AS managed_by
                FROM Assets a
                         JOIN Instrument i ON a.id_instrument = i.id_instrument
                         LEFT JOIN Strategy s ON a.id_strategy = s.id_strategy
                WHERE a.id_user = ? \
                  AND a.active = 1 \
                """
        return pd.read_sql(query, cont, params=[id_user])

    def allocate_funds_to_Asset(self, id_user: int, id_instrument: int, id_strategy: int, amount: float) -> bool:
        """
        Przenosi środki z głównego portfela (Wallet) do budżetu konkretnej strategii (Assets).
        Uruchamiane, gdy użytkownik w Streamlit przypisuje budżet do bota.
        """
        cont = self.db.connect()
        cursor = cont.cursor()
        query = """SELECT balance FROM Wallet WHERE id_user = ?"""
        try:
            # 1. Sprawdź, czy użytkownik ma tyle wolnej gotówki w głównym portfelu
            cursor.execute( query, (id_user,))
            balance = float(cursor.fetchone()[0])
            if balance < amount:
                print("Niewystarczające środki w głównym portfelu")
                return False

            position = self.get_user_position(id_user, id_instrument, id_strategy)
            if not position:
                ins_query = """
                            INSERT INTO Assets (id_user, id_instrument, id_strategy, allocatedBalance)
                            VALUES (?, ?, ?, ?) \
                            """
                cursor.execute(ins_query, (id_user, id_instrument, id_strategy, amount))
            else:
                cursor.execute("UPDATE Assets SET allocatedBalance = allocatedBalance + ? WHERE id_assets = ?",
                               (amount, position["id_assets"]))

            # 3. Odejmij środki z głównego portfela
            cursor.execute("UPDATE [Wallet] SET balance = balance - ? WHERE id_user = ?", (amount, id_user))

            cont.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas przenoszenai środkow: {e}")
            cont.rollback()
        return False

    def register_transaction(self, id_user: int, id_instrument: int, id_strategy: int,
                                           trade_type: str, quantity:float, price: float) -> bool:  ###TODO -- quantity bedzie cpochodzilo z dashboardu !!!
        """
        Zoptymalizowana wersja handlu: bot pobiera pieniądze na zakup i zwraca po sprzedaży
        WYŁĄCZNIE w ramach budżetu przypisanego do tej konkretnej pozycji (Assets.allocated_balance).
        """
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            position = self.get_user_position(id_user, id_instrument, id_strategy)
            if not position:
                raise ValueError(f"{RED}[ERROR]{RESET} posiadanego aktywa")
            if not position["allocatedBalance"]:
                raise ValueError(f"{RED}[ERROR]{RESET} środków w akrywie")

            id_assets = position["id_assets"]
            total_value = quantity * price

            # POBIERANIE AKTUALNEGO DEDYKOWANEGO BUDŻETU TEJ STRATEGII
            cursor.execute("SELECT allocatedBalance FROM Assets WHERE id_assets = ?", (id_assets,))
            avaibleBalance = float(cursor.fetchone()[0])

            if trade_type == 'BUY':  ### TODO __ DO PRZEMYSLENIA
                if avaibleBalance <= 0.0:
                    print(f"{RED}[ERROR]{RESET} Transakcja zablokowana: Pozycja nie posiada środków wyczerpała swój budżet, dostępne {avaibleBalance}, PRAWDOPODOBNIE BLAD SYSTEMU!!!")
                    return False
                if avaibleBalance < total_value:
                    quantity = avaibleBalance / price

                cursor.execute("""UPDATE Assets
                    SET quantity = ?, averagePrice = ?, allocatedBalance = 0.0000, active = 1 WHERE id_assets = ?
                    """, (quantity, price, id_assets))
                PNL = None
            else:  #TODO __SELL
                PNL = (price - position["averagePrice"]) * quantity
                cursor.execute("""
                   UPDATE Assets SET quantity = ?, allocatedBalance = ?, active = ? WHERE id_assets = ?
                   """, (0.0, total_value, 1, id_assets))

            # Rejestracja wpisu w historii transakcji
            new_transaction = """
                        INSERT INTO [Transaction] (id_assets, transactionType, quantity, price, totalValue, PNL, [timestamp])
                        VALUES (?, ?, ?, ?, ?, ?, ?) \
                        """
            cursor.execute(new_transaction, (id_assets, trade_type, quantity, price, total_value, PNL, datetime.now()))

            conn.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas transakcji po sygnale {trade_type} dla strategii (id: {id_strategy}): {e}")
            conn.rollback()
            return False