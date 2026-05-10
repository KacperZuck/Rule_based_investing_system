import streamlit as st
import yaml

# 1. Ładowanie konfiguracji
with open("Logic/config.yaml", "r") as f:
    config = yaml.safe_load(f)

st.title("Panel Sterowania Wskaźnikami")

# 2. Dynamiczne GUI dla parametrów
new_config = []
for i, item in enumerate(config['active_strategy']):
    st.subheader(f"Wskaźnik: {item['type']}")
    # Suwak do zmiany parametrów w locie
    new_param = st.slider(f"Okres dla {item['type']} (id:{i})", 1, 200, item['params'][0])
    item['params'] = [new_param]
    new_config.append(item)

# 3. Przycisk zapisu
if st.button("Zapisz nową konfigurację"):
    with open("Logic/config.yaml", "w") as f:
        yaml.dump({"active_strategy": new_config}, f)
    st.success("Parametry zaktualizowane w YAML!")