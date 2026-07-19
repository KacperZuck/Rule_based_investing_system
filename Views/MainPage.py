
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
    # df_instruments = st.session_state.market_repo.get_all_instruments()
    df_instruments = st.session_state.market_repo.get_instruments_main_page()
    # df_strategies = st.session_state.strategy_repo.get_all_strategy()
    df_strategies = st.session_state.strategy_repo.get_strategies_main_page()
    df_indicators = st.session_state.strategy_repo.get_indicators_main_page()

    tab1, tab2, tab3 = st.tabs([
        "Instrumenty", "Strategie", "Wskaźniki"
    ])

    with tab1:
        st.write("Dostępne instrumenty")
        if not df_instruments.empty:
            cols_to_drop = [col for col in df_instruments.columns if 'id' in col.lower()]
            df_display = df_instruments.drop(columns=cols_to_drop)
            st.dataframe(df_display, width='stretch', hide_index=True)
            st.divider()

            # TODO __ NARAZIE __ WERSJA TESTOWA
            st.write("#### Wybierz instrument do analizy:")

            # Generowanie kafelków z przyciskami na podstawie bazy
            col1, col2, col3 = st.columns(3)
            for idx, row in df_instruments.iterrows():
                ticker = row['ticker']
                name = row['name']

                with [col1, col2, col3][idx % 3]:
                    with st.container(border=True):
                        st.write(f"**{ticker}**")
                        st.caption(name)
                        if st.button(f"Analizuj {ticker}", key=f"btn_analyze_{ticker}"):
                            st.session_state.selected_ticker = ticker
                            st.session_state.current_page = "Dashbord"
                            st.rerun()
        else:
            st.warning("Brak zdefiniowanych instrumentów w tabeli [Instrument].")

    with tab2:
        st.write("### Zdefiniowane Strategie w bazie")
        if not df_strategies.empty:
            # Zamiast płaskiej tabeli, dla każdej strategii tworzymy rozwijany panel
            for _, row in df_strategies.iterrows():
                # Bezpieczne pobieranie wartości (jeśli kolumny nie ma, wstawi wartość domyślną)
                strat_name = row.get('name', 'Brak nazwy')
                signals_count = row.get('signals', row.get('Signals', 0))  # Sprawdza małą i wielką literę
                t_buy = row.get('thresholdBuy', row.get('threshold_buy', 0.0))
                t_sell = row.get('thresholdSell', row.get('threshold_sell', 0.0))
                id_strat = row.get('id_strategy')

                expander_title = f"{strat_name}"

                with st.expander(expander_title):
                    # Wyświetlanie głównych parametrów strategii
                    c1, c2 = st.columns(2)
                    c1.metric("Próg Kupna (Threshold Buy)", t_buy)
                    c2.metric("Próg Sprzedaży (Threshold Sell)", t_sell)

                    st.write("Użyte wskaźniki jako sygnały:")
                    # Pobieranie przetłumaczonej sub-tabeli dla danego id_strategy
                    if id_strat is not None:
                        df_sub = st.session_state.strategy_repo.get_signal_config_details(id_strat)

                        if not df_sub.empty:
                            # dropna usuwa kolumny, które są całkowicie puste
                            st.dataframe(df_sub.dropna(axis=1, how='all'), width='stretch', hide_index=True)
                        else:
                            st.info("Brak skonfigurowanych warunków sygnałów w tabeli SignalConfig.")
                    else:
                        st.error("Błąd: Brak ID strategii do pobrania konfiguracji.")
        else:
            st.warning("Brak zdefiniowanych strategii w tabeli [Strategy].")

    with tab3:
        st.write("### Dostępne wskaźniki techniczne")
        if not df_indicators.empty:
            # Jeżeli w df_indicators znajduje się jakieś ID, usuwamy je z widoku
            if 'id_indicator' in df_indicators.columns:
                df_indicators = df_indicators.drop(columns=['id_indicator'])
            st.dataframe(df_indicators, width='stretch', hide_index=True)
        else:
            st.warning("Brak wskaźników w tabeli [Indicator].")