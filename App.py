
import streamlit as st
import pandas as pd
import time

from Data.Database import Database
from Data.Market import MarketRepository
from Data.User import UserRepository
from Data.Assets import AssetsRepository
from Data.Strategies import StrategiesRepository

from Views.MainPage import render_dashboard
from Views.Register import render_register
from Views.Login import render_login
from Views.Dashbord import render_dashbord

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

def main():
    init_session_state()

    # if st.session_state.current_page == "LoginPage":
    #     render_login()
    # elif st.session_state.current_page == "RegisterPage":
    #     render_register()
    if st.session_state.current_page == "MainPage":
        render_dashboard()
    elif st.session_state.current_page == "Dashbord":
        render_dashbord()

if __name__ == "__main__":
    main()