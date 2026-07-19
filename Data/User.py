
import pandas as pd
from Data.Database import *

class UserRepository():
    def __init__(self, db : Database):
        self.db = db

    def register_user(self, user_type: int, name: str, email: str, password: str) -> bool:
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """
                INSERT INTO [User] (id_usertype, [name], email, [password]) \
                VALUES (?, ?, ?, ?) \
                """
        try:
            cursor.execute(query, (user_type, name, email, password))
            user_id = cursor.execute("SELECT id_user FROM [User] WHERE email = ?", email).fetchone()[0]

            walletq = "INSERT INTO Wallet (id_user, balance) VALUES (?, 1000.0000)"
            cursor.execute(walletq, user_id)

            cont.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas rejsetracji: {e}")
            cont.rollback()
            return False

    def login(self, name: str, email: str, password: str) -> dict | bool:
        cont = self.db.connect()

        query = "SELECT id_user, [name], [password] FROM [User] WHERE email = ?"

        try:
            cursor = cont.cursor()
            cursor.execute(query, (email,))
            data = cursor.fetchone()
            if data:
                db_name = data[1]
                db_pass = data[2]
                if db_name == name and db_pass == password:
                    return {"id_user": data[0], "name": data[1], "password": data[2]}
                else:
                    print(f"{YELLOW}[INFO]{RESET} błąd logowania, niepoprawne dane")
            else:
                print(f"{YELLOW}[INFO]{RESET} nie znaleziono użytkownika")
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} zapytania dla logowania: {e}")
        return False

    def get_wallet(self, id_user: int) -> float:
        cont = self.db.connect()
        cursor = cont.cursor()

        try:
            cursor.execute("SELECT balance FROM [Wallet] WHERE id_user = ?", (id_user,))
            data = cursor.fetchone()
            return float(data[0]) if data else 0.0
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas sprawdzania portfela: {e}")
            cont.rollback()
        return 0.0

    def update_wallet(self, id_user: int, val:float) -> bool:
        cont = self.db.connect()
        cursor = cont.cursor()

        query = """
        UPDATE [Wallet] SET balance = balance + ? WHERE id_user = ? """
        try:
            cursor.execute(query, (val, id_user))
            cont.commit()
            return True
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} podczas aktualizowania wartosci portfela w bazie: {e}")
            cont.rollback()
        return False
