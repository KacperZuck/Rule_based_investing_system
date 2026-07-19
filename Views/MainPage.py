
import streamlit as st
import pandas as pd
import time

from Data.Database import Database
from Data.Market import MarketRepository
from Data.User import UserRepository
from Data.Assets import AssetsRepository
from Data.Strategies import StrategiesRepository


def render_dashboard():

    st.title("RBIS - Regułowy system inwestycyjny")
    with st.sidebar:
        st.header("Portfel")
        balance = st.session_state.user_repo.get_wallet(st.session_state.logged_user_id)
        st.metric("Aktualne środki", f"{balance:.2f}") # TODO __ WALUTA
        st.divider()
        st.subheader("Strategie")
        st.info("NARAZIE BRAK \nbedzie --> listę z asset_repo.get_portfolio_dashboard()  ")

    st.subheader("Główny widok")
    df_instruments = st.session_state.market_repo.get_all_instruments()
    # df_instruments = st.session_state.market_repo.get_instruments_main_page()
    df_strategies = st.session_state.strategy_repo.get_all_strategy()
    # df_strategies = st.session_state.strategy_repo.get_strategies_main_page()
    df_indicators = st.session_state.strategy_repo.get_indicators_main_page()

    tab1, tab2, tab3 = st.tabs([
        "Instrumenty", "Strategie", "Wskaźniki"
    ])

    with tab1:
        st.write("Dostępne instrumenty")
        if not df_instruments.empty:
            st.dataframe(df_instruments, use_container_width=True, hide_index=True)
            st.divider()

            # TODO __ NARAZIE __ WERSJA TESTOWA
            st.write("#### Wybierz instrument do analizy:")

            # Generowanie kafelków z przyciskami na podstawie bazy
            col1, col2, col3 = st.columns(3)
            for idx, row in df_instruments.iterrows():
                ticker = row['ticker']
                name = row['name']

                # Rozdzielamy kafelki równomiernie do 3 kolumn
                with [col1, col2, col3][idx % 3]:
                    with st.container(border=True):
                        st.write(f"**{ticker}**")
                        st.caption(name)
                        if st.button(f"Analizuj {ticker}", key=f"btn_analyze_{ticker}"):
                            st.session_state.selected_ticker = ticker
                            st.session_state.current_page = "Dashbord"
                            st.rerun()

    with tab2:
        st.write("Zdefiniowane Strategie w bazie")
        if not df_strategies.empty:
            st.dataframe(df_strategies, use_container_width=True, hide_index=True)
        else:
            st.warning("###Brak zdefiniowanych strategii w tabeli [Strategy].")

    with tab3:
        st.write("Dostępne wskaźniki techniczne")
        if not df_indicators.empty:
            st.dataframe(df_indicators, use_container_width=True, hide_index=True)
        else:
            st.warning("Brak wskaźników w tabeli [Indicator].")