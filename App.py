
import streamlit as st
import pandas as pd
import time

from Data.Database import Database
from Data.Market import MarketRepository
from Data.User import UserRepository
from Data.Assets import AssetsRepository
from Data.Strategies import StrategiesRepository

from Logic.Managers.UserManager import UserManager
from Logic.SideBar import main_sidebar
from Logic.Plots import StrategyPlot

st.set_page_config(page_title="RBIS", layout="wide")

def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "MainPage"
        st.session_state.selected_ticker = None
        st.session_state.selected_strategy = None

    st.session_state.db = Database()
    st.session_state.market_repo = MarketRepository(st.session_state.db)
    st.session_state.user_repo = UserRepository(st.session_state.db)
    st.session_state.asset_repo = AssetsRepository(st.session_state.db)
    st.session_state.strategy_repo = StrategiesRepository(st.session_state.db)

    #TODO Tymczasowe mockowanie ID zalogowanego użytkownika (do testów UI)
    # Docelowo tu będzie ID z ekranu logowania
    st.session_state.logged_user_id = 1

def render_login():
    pass
def render_register():
    pass

def render_dashboard():
    st.title("Główny widok")

    with st.sidebar:
        st.header("Portfel")
        balance = st.session_state.user_repo.get_balance(st.session_state.logged_user_id)
        st.metric("Aktualne środki", f"{balance:2f}") # TODO __ WALUTA
        st.divider()
        st.subheader("Strategie")
        st.info("NARAZIE BRAK bedzie --> listę z asset_repo.get_portfolio_dashboard()  ")

    st.subheader("RBIS - Regułowy system inwestycyjny")

    df_instrument = st.session_state.market_repo.get_instruments()
    df_strategies = st.session_state.strategy_repo.get_strategies()
    df_indicators = st.session_state.strategy_repo.get_indicators()

    tab1, tab2, tab3 = st.tabs([
        "Instrumenty", "Strategie", "Wskaźniki"
    ])

    with tab1:
        st.write("Dostępne instrumenty")
        if not df_instrument.empty:
            st.dataframe(df_instrument, use_column_width=True, hide_index=True)
            st.divider()

            # TODO __ NARAZIE __ WERSJA TESTOWA
            st.write("#### Wybierz instrument do analizy:")

            # Generowanie kafelków z przyciskami na podstawie bazy
            col1, col2, col3 = st.columns(3)
            for idx, row in df_instrument.iterrows():
                ticker = row['ticker']
                name = row['name']

                # Rozdzielamy kafelki równomiernie do 3 kolumn
                with [col1, col2, col3][idx % 3]:
                    with st.container(border=True):
                        st.write(f"**{ticker}**")
                        st.caption(name)
                        if st.button(f"Analizuj {ticker}", key=f"btn_analyze_{ticker}"):
                            st.session_state.selected_ticker = ticker
                            st.session_state.current_page = "SIMULATION"
                            st.rerun()

    with tab2:
        st.write("### Zdefiniowane Strategie w bazie")
        if not df_strategies.empty:
            st.dataframe(df_strategies, use_container_width=True, hide_index=True)
        else:
            st.warning("Brak zdefiniowanych strategii w tabeli [Strategy].")

    with tab3:
        st.write("### Dostępne wskaźniki techniczne")
        if not df_indicators.empty:
            st.dataframe(df_indicators, use_container_width=True, hide_index=True)
        else:
            st.warning("Brak wskaźników w tabeli [Indicator].")

def render_simulation():
    ticker = st.session_state.selected_ticker

    if st.button("Powrót do głównego widoku"):
        st.session_state.current_page = "MainPage"
        st.session_state.selected_ticker = None
        st.rerun()

    st.title(f"Analiza {ticker}")
    st.divider()

    #TODO ___ PRZEKLEJENIE KODU Z DASBOARD

    st.info("Wcześniejszy program")

def main():
    init_session_state()

    # if st.session_state.current_page == "LoginPage":
    #     render_login()
    # elif st.session_state.current_page == "RegisterPage":
    #     render_register()
    if st.session_state.current_page == "MainPage":
        render_dashboard()
    elif st.session_state.current_page == "Simulation":
        render_simulation()

if __name__ == "__main__":
    main()