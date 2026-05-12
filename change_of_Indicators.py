

















#TODO Modyfikacja Handlera pod wielu użytkowników

class UserSession:
    def __init__(self, user_id, config_path, data_path):
        self.user_id = user_id
        # Każdy użytkownik ma własną instancję Managera
        self.manager = Manager(config=config_path)
        self.data_source = pd.read_csv(data_path)
        self.is_running = False

class GlobalHandler:
    def __init__(self):
        # Słownik sesji: { "user_1": UserSessionObj, "user_2": ... }
        self.sessions = {}

    def add_user(self, user_id, config, data_path):
        self.sessions[user_id] = UserSession(user_id, config, data_path)

    def get_user_manager(self, user_id):
        return self.sessions[user_id].manager


#TODO 3. Schemat przepływu danych (Multi-User)

# W Streamlit dashboard_app.py
if 'handler' not in st.session_state:
    st.session_state.handler = GlobalHandler()

user_id = st.sidebar.text_input("ID Użytkownika")
symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "EURUSD"])

if st.sidebar.button("Załaduj moją sesję"):
    config_path = f"configs/config_{user_id}.yaml"
    data_path = f"data/{symbol}.csv"
    st.session_state.handler.add_user(user_id, config_path, data_path)
    st.success(f"Załadowano sesję dla {user_id}")

# Pobranie managera aktualnego użytkownika
if user_id in st.session_state.handler.sessions:
    current_session = st.session_state.handler.sessions[user_id]
    # Tutaj uruchamiasz pętlę symulacji dla konkretnego managera