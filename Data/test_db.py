import sys
from Database import *
from Market import MarketRepository
from User import UserRepository
from Strategies import StrategiesRepository
from Assets import AssetsRepository


def cleanup_test_data(db: Database, email: str, strategy_name: str):
    """Usuwa wszystkie dane testowe wygenerowane podczas działania skryptu."""
    print(f"\n{YELLOW}--- CZYSZCZENIE DANYCH TESTOWYCH ---{RESET}")
    cont = db.connect()
    cursor = cont.cursor()
    try:
        # Usuwanie powiązanych z użytkownikiem transakcji, aktywów, portfela i konta
        cursor.execute("DELETE FROM [Transaction] WHERE id_assets IN (SELECT id_assets FROM Assets WHERE id_user IN (SELECT id_user FROM [User] WHERE email = ?))", (email,))
        cursor.execute("DELETE FROM Assets WHERE id_user IN (SELECT id_user FROM [User] WHERE email = ?)", (email,))
        cursor.execute("DELETE FROM Wallet WHERE id_user IN (SELECT id_user FROM [User] WHERE email = ?)", (email,))
        cursor.execute("DELETE FROM [User] WHERE email = ?", (email,))
        print(f"{GREEN}[OK]{RESET} Usunięto użytkownika testowego i jego portfel.")

        # Usuwanie powiązanych ze strategią sygnałów, konfiguracji i samej strategii
        cursor.execute("DELETE FROM SignalConfig WHERE id_strategy IN (SELECT id_strategy FROM Strategy WHERE name = ?)", (strategy_name,))
        cursor.execute("DELETE FROM StrategySignal WHERE id_strategy IN (SELECT id_strategy FROM Strategy WHERE name = ?)", (strategy_name,))
        cursor.execute("DELETE FROM Strategy WHERE name = ?", (strategy_name,))
        print(f"{GREEN}[OK]{RESET} Usunięto testową strategię i jej sygnały.")

        cont.commit()
        print(f"{GREEN}[SUCCESS]{RESET} Baza danych została w 100% wyczyszczona z testów.")
    except Exception as e:
        print(f"{RED}[ERROR]{RESET} podczas czyszczenia bazy: {e}")
        cont.rollback()

def run_integration_tests():
    print(f"{YELLOW}TESTY INTEGRACYJNE Z BAZA DANYCH{RESET}")

    # 1. Inicjalizacja bazy
    db = Database()
    try:
        conn = db.connect()
        print(f"{GREEN}[OK]{RESET} Połączenie z SQL Server nawiązane pomyślnie.")
    except Exception as e:
        print(f"{RED}[FAIL]{RESET} Nie udało się połączyć z bazą: {e}")
        sys.exit(1)

    # Inicjalizacja wszystkich repozytoriów
    market_repo = MarketRepository(db)
    user_repo = UserRepository(db)
    strat_repo = StrategiesRepository(db)
    asset_repo = AssetsRepository(db)

    TEST_EMAIL = "test@test.pl"
    TEST_NAME = "tester"
    TEST_PASS = "test"
    TEST_STRATEGY = "testowa_strategia"
    ID_INSTRUMENT = 1

    # -------------------------------------------------------------------------
    # TEST 1: Pobieranie świeczek (MarketRepository)
    # -------------------------------------------------------------------------
    print("\n--- TEST MARKET ---")
    df = market_repo.get_candles(ticker="NDAQ")
    if not df.empty:
        print(f"{GREEN}[OK]{RESET} Pobrano {len(df)} świec dla NDAQ.")
        print("     Ostatni rekord:")
        print(df.tail(1))
    else:
        print(f"{RED}[FAIL]{RESET} Zwrócono pusty DataFrame dla NDAQ")

    print("\n")
    instrument = market_repo.get_instrument(ticker="NDAQ")
    if instrument:
        print(f"{GREEN}[OK]{RESET} Pobrano dane dla NDAQ.")
        print(instrument)
    else:
        print(f"{RED}[FAIL]{RESET} Zwrócono pusty DataFrame dla NDAQ")

    # -------------------------------------------------------------------------
    # TEST 2: Rejestracja i logowanie użytkownika (UserRepository)
    # -------------------------------------------------------------------------

    print("\n--- TEST Obsługa użytkownika i portfela ---")

    reg_success = user_repo.register_user(user_type=1, name=TEST_NAME, email=TEST_EMAIL, password=TEST_PASS)
    if reg_success:
        print(f"{GREEN}[OK]{RESET} Zarejestrowano nowego użytkownika: {TEST_EMAIL}")

        user_data = user_repo.login(email=TEST_EMAIL, name=TEST_NAME, password=TEST_PASS)
        if user_data:
            id_user = user_data["id_user"]
            print(f"{GREEN}[OK]{RESET} Zalogowano pomyślnie. ID Użytkownika w bazie: {id_user}")

            balance = user_repo.get_wallet(id_user)
            print(f"{GREEN}[OK]{RESET} Aktualne saldo: {balance}")
            print(f"{YELLOW}[INFO]{RESET} Dodawanie 500.0")
            if user_repo.update_wallet(id_user, 500.0) != 0.0:
                new_balance = user_repo.get_wallet(id_user)
                if new_balance == balance + 500.0:
                    print(f"{GREEN}[OK]{RESET} Nowy stan: {new_balance} USD")
                else:
                    print(f"{RED}[FAIL]{RESET} Środki nie zaktualizowane")

            print(f"{YELLOW}[INFO]{RESET} Odejmowanie 200.0 USD...")
            if user_repo.update_wallet(id_user, -200.0):
                final_balance = user_repo.get_wallet(id_user)
                if final_balance == new_balance - 200.0:
                    print(f"{GREEN}[OK]{RESET} Środki odjęte pomyślnie: {final_balance}")
                else:
                    print(f"{RED}[FAIL]{RESET} Środki nie zaktualizowały się poprawnie")
        else:
            print(f"{RED}[FAIL]{RESET} Błąd logowania testowego")

    else:
        print(f"{YELLOW}[INFO]{RESET} Użytkownik {TEST_EMAIL} prawdopodobnie już istnieje (lub błąd klucza).")

    # -------------------------------------------------------------------------
    # TEST 3: Dodawanie konfiguracji sygnałów (StrategyRepository)
    # -------------------------------------------------------------------------

    print("\n--- TEST strategii i sygnałów ---")
    id_strategy = strat_repo.add_strategy(name=TEST_STRATEGY, public=False, thresholdBuy=0.7, thresholdSell=0.3)
    if id_strategy:
        print(f"{GREEN}[OK]{RESET} Dodano nową strategię '{TEST_STRATEGY}' (ID: {id_strategy}).")
    else:
        print(f"{RED}[FAIL]{RESET} blad w dodawaniu strategi")
    # 2. Lista strategii
    df_strats = strat_repo.get_all_strategy()
    if not df_strats.empty:
        print(f"{GREEN}[OK]{RESET} Pobrano listę strategii ({len(df_strats)} sztuk).")
    else:
        print(f"{RED}[FAIL]{RESET} we wszystkich strategiach")

    # 3. Konfiguracja sygnału dla nowej strategii
    config_success = strat_repo.save_signal_config(
        id_strategy=id_strategy, id_indicator=3, id_logic=1, threshold_low=30.0, threshold_high=70.0
    )
    if config_success:
        print(f"{GREEN}[OK]{RESET} Zapisano konfigurację (SignalConfig) dla strategii.")
    else:
        print(f"{RED}[FAIL]{RESET} blad w zapisie konfiguracji")

    # 4. Pobieranie struktury sygnałów
    df_config = strat_repo.get_signals_config(id_strategy)
    if not df_config.empty:
        print(f"{GREEN}[OK]{RESET} Pobrano SignalConfig: Znaleziono {len(df_config)} warunków dla strategii {id_strategy}")
    else:
        print(f"{RED}[FAIL]{RESET} blad w pobraniu sigconfig")

    # 5. Sprawdzenie parametrów wskaźnika i sygnału zapisu
    indic_params = strat_repo.get_indicator_parameters(id_indicator=3)
    if indic_params:
        print(f"{GREEN}[OK]{RESET} Pobrano parametry wskaźnika (ID=3): {indic_params}")
    else:
        print(f"{RED}[FAIL]{RESET} blad w pobrania param wskaznika")

    if strat_repo.save_strategy_signal(id_strategy, ID_INSTRUMENT, val=1):
        print(f"{GREEN}[OK]{RESET} Zapisano nowy wygenerowany sygnał (BUY).")
    else:
        print(f"{RED}[FAIL]{RESET} blad w dodawaniu syganlu dla strategi")

    indic = strat_repo.get_all_indicators()
    if not indic.empty:
        print(f"{GREEN}[OK]{RESET} Pobrano parametry dla wszystkich wskaźnikow: {indic}")
    else:
        print(f"{RED}[FAIL]{RESET} blad w dodawaniu strategi")

    # -------------------------------------------------------------------------
    # TEST 4: Alokacja budżetu i handel wewnątrz-budżetowy (AssetRepository)
    # -------------------------------------------------------------------------
    print("\n--- TEST ASSETS ---")

    if asset_repo.allocate_funds_to_Asset(id_user, ID_INSTRUMENT, id_strategy, amount=500.0):
        print(f"{GREEN}[OK]{RESET} Alokowano 500.0 do sub-portfela strategii.")
    else:
        print(f"{RED}[FAIL]{RESET} alokacji")

        # 2. Wykonanie zakupu
    if asset_repo.register_transaction(id_user, ID_INSTRUMENT, id_strategy, trade_type="BUY", quantity=5.0,
                                       price=100.0):
        print(f"{GREEN}[OK]{RESET} Bot wykonał operację BUY (5.0 szt. po 100.0 USD).")
    else:
        print(f"{RED}[FAIL]{RESET} rejestracji transakcji")

        # 3. Sprawdzenie pozycji
    pos = asset_repo.get_user_position(id_user, ID_INSTRUMENT, id_strategy)
    if pos:
        print(f"{GREEN}[OK]{RESET} Aktualna pozycja: Sztuk = {pos['quantity']}, Śr. cena = {pos['averagePrice']}")
    else:
        print(f"{RED}[FAIL]{RESET} sprawdzenia aktywa uzytkownika")

    # 4. Widok dashboardu
    df_dash = asset_repo.get_portfolio_dashboard(id_user)
    if not df_dash.empty:
        print(f"{GREEN}[OK]{RESET} Wygenerowano dane Dashboardu. Widoczne wiersze: {len(df_dash)}")
    else:
        print(f"{RED}[FAIL]{RESET} dashboard")

    # Sprzątanie połączenia
    cleanup_test_data(db, TEST_EMAIL, TEST_STRATEGY)
    print("\n=== TESTY ZAKOŃCZONE ===")


if __name__ == "__main__":
    run_integration_tests()