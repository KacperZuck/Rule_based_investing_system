import ast

import streamlit as st
from Logic.Static.indicator_map import INDICATOR_MAP

def render_sidebar():
    st.sidebar.header("Zarządzanie sesją")
    u_manager = st.session_state.user_manager

    available_strats = list(u_manager.strategies.keys())
    if not available_strats:
        st.sidebar.warning("Brak strategii")
        st.stop()
    selected = st.sidebar.selectbox("Wybierz dostepne strategie", available_strats)
    st.sidebar.divider()

    investing_money = st.sidebar.text_input("Zadeklaruj inwestowaną kwotę", placeholder="wpisz kwote...")
    st.sidebar.divider()

    st.sidebar.subheader("Symulacja")
    speed = st.sidebar.slider("Prędkość [s]", 0.0, 4.0, 1.0)
    st.sidebar.divider()

    if st.sidebar.button("Zapisz stan sesji"):
        save_file = f"Configs/config_{u_manager.user_id}.yaml"
        u_manager.save_user_data(save_file)
        st.sidebar.success(f"Sesja zapisana: {save_file}")
    st.sidebar.divider()

    return selected, speed


def render_creator_sidebar():
    st.sidebar.subheader("Kreator Strategii")
    new_strat_name = st.sidebar.text_input("Nazwa nowej strategii", placeholder="wpisz nazwe...")
    st.sidebar.divider()

    selected_ind_key = st.sidebar.selectbox("Dodaj wskaźnik", list(INDICATOR_MAP.keys()))
    meta = INDICATOR_MAP[selected_ind_key]

    source_info = meta.get('source', 'CLOSE')
    st.sidebar.info(f"Źródło danych wskaźnika: {source_info}")

    current_params = []
    for p_name, p_config in meta["params"].items():
        if p_config["type"] == "int":
            val = st.sidebar.number_input(
                f"Parametr: {p_name}",
                p_config["min"], p_config["max"], p_config["default"]
            )
        elif p_config["type"] == "float":
            val = st.sidebar.slider(
                f"Parametr: {p_name}",
                float(p_config["min"]), float(p_config["max"]), float(p_config["default"])
            )
        current_params.append(val)

    logic_type = None
    logic_params = {}

    if "logic" in meta:
        logic_type = st.sidebar.selectbox("Logika sygnału", meta["logic"])

        if logic_type == "THRESHOLD":
            logic_params["low"] = st.sidebar.number_input("Próg Kupna (Low)", value=30)
            logic_params["high"] = st.sidebar.number_input("Próg Sprzedaży (High)", value=70)
        elif logic_type == "CROSSOVER":
            st.sidebar.write("Sygnał dla przecięcia lini")
            available_targets = ["CLOSE"] + list(INDICATOR_MAP.keys())
            logic_params["target"] = st.sidebar.selectbox("Przecięcie z:", available_targets)

            if logic_params["target"] != "CLOSE":
                logic_params["target_params"] = st.sidebar.text_input(
                    "Parametry celu (np. [26])",
                    value="[26]",
                    help="Wpisz parametry wskaźnika docelowego jako listę"
                )

    st.sidebar.divider()

    if st.sidebar.button("Dodaj Strategie"):
        if not new_strat_name:
            st.sidebar.error("Wymagane jest podanie nazwy strategii")
        else:
            t_params_raw = logic_params.get("target_params", "[]")
            try:
                parsed_target_params = ast.literal_eval(t_params_raw)
            except:
                parsed_target_params = []

            new_signal_cfg = {
                "type": selected_ind_key,
                "params": current_params,  # lista [14]
                "logic": logic_type,
                "logic_params": {
                    **logic_params,
                    "target_params": parsed_target_params
                }
            }

            success = st.session_state.user_manager.add_custom_strategy(
                new_strat_name,
                [new_signal_cfg]
            )

            if success:
                st.sidebar.success(f"Dodano strategię: {new_strat_name}")
                st.rerun()

    return None, 0

def main_sidebar():
    mode = st.sidebar.segmented_control(
        "RSIInGPW",
        options=["Symulacja", "Tworzenie"],
        default="Symulacja"
    )
    st.sidebar.divider()
    if mode == "Symulacja":
        return render_sidebar()
    else:
        return render_creator_sidebar()