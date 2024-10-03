import streamlit as st
import pandas as pd
import sqlite3

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            league TEXT NOT NULL,
            season TEXT NOT NULL,
            team_manager TEXT,
            technical_staff TEXT,
            head_coach TEXT,
            assistant_coaches TEXT,
            team_medic TEXT,
            fitness_trainer TEXT,
            full_team_list TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_number TEXT NOT NULL UNIQUE,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES team (id)
        )
    ''')
    conn.commit()
    conn.close()

# Function to register a player
def register_player(name, id_number, team_id):
    conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    
    # Check if player with the same name is already registered
    c.execute('SELECT * FROM player WHERE name = ?', (name,))
    existing_player_by_name = c.fetchone()
    
    if existing_player_by_name:
        st.warning(f"⚠️ Player {name} is already registered.")
        conn.close()
        return False

    # Check if player ID is already registered
    c.execute('SELECT * FROM player WHERE id_number = ?', (id_number,))
    existing_player_by_id = c.fetchone()
    
    if existing_player_by_id:
        # Check if player is in another team
        if existing_player_by_id[3] is not None and existing_player_by_id[3] != team_id:
            st.warning(f"⚠️ Player ID {id_number} is already registered in another team.")
            conn.close()
            return False
    
    # Register the player
    c.execute('''
        INSERT INTO player (name, id_number, team_id)
        VALUES (?, ?, ?)
    ''', (name, id_number, team_id))
    conn.commit()
    conn.close()
    st.success(f"✅ Player {name} registered successfully!")
    return True

# Function to register a team
def register_team(team_name, league, season, team_manager, technical_staff, head_coach, assistant_coaches, team_medic, fitness_trainer, full_team_list):
    conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO team (team_name, league, season, team_manager, technical_staff, head_coach, assistant_coaches, team_medic, fitness_trainer, full_team_list)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (team_name, league, season, team_manager, technical_staff, head_coach, assistant_coaches, team_medic, fitness_trainer, full_team_list))
    team_id = c.lastrowid  # Get the ID of the newly registered team
    conn.commit()
    conn.close()
    st.success("Team registered successfully!")
    return team_id

# Function to get metrics
def get_metrics():
    conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
    teams_count = pd.read_sql_query("SELECT COUNT(*) as count FROM team", conn).iloc[0]['count']
    conn.close()
    return teams_count

# Initialize the database
init_db()

# Streamlit App Layout
st.markdown("""
    <style>
        .header-title {
            font-size: 2em;
            color: #007BFF;
            font-weight: bold;
        }
        .subheader-title {
            font-size: 1.5em;
            color: #28A745;
            font-weight: bold;
        }
        .kpi-card {
            background-color: #f1f1f1;
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .kpi-card h3 {
            margin: 0;
            font-size: 1.5em;
            color: #333;
        }
        .kpi-card p {
            font-size: 1.2em;
            color: #555;
        }
        .kpi-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏏 BMCA Cricket Registration Platform")

# Team Registration Section
st.markdown("<h2 class='subheader-title'>Register a Team</h2>", unsafe_allow_html=True)
with st.form("team_registration_form"):
    team_name = st.text_input("🏆 Team Name")
    league = st.selectbox("🏅 Select League", ["First League Men's", "First League Women's", "Second League Men's", "Second League Women's"])
    season = st.selectbox("📅 Select Season", ["2024/2025", "2025/2026", "2026/2027"])
    team_manager = st.text_input("👤 Team Manager")
    technical_staff = st.text_input("👨‍🏫 Technical Staff")
    head_coach = st.text_input("🏆 Head Coach")
    assistant_coaches = st.text_input("👥 Assistant Coaches (comma-separated)")
    team_medic = st.text_input("🏥 Team Medic")
    fitness_trainer = st.text_input("💪 Team Fitness Trainer")
    full_team_list = st.text_area("📋 Full Team List (Name - ID Number, one per line)")

    submitted = st.form_submit_button("✅ Register Team")
    
    if submitted:
        team_id = register_team(team_name, league, season, team_manager, technical_staff, head_coach, assistant_coaches, team_medic, fitness_trainer, full_team_list)

# Player Registration Section
st.markdown("<h2 class='subheader-title'>Register a Player</h2>", unsafe_allow_html=True)
conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
teams_df = pd.read_sql_query("SELECT id, team_name FROM team", conn)
conn.close()

with st.form("player_registration_form"):
    player_name = st.text_input("👤 Player Name")
    player_id_number = st.text_input("🆔 Player ID Number")
    team_name = st.selectbox("🏆 Select Team", teams_df['team_name'].tolist())  # Select box for teams
    
    register_player_button = st.form_submit_button("✅ Register Player")
    
    if register_player_button and player_name and player_id_number and team_name:
        selected_team_id = teams_df.loc[teams_df['team_name'] == team_name, 'id'].values[0]
        register_player(player_name, player_id_number, selected_team_id)
    else:
        st.warning("⚠️ Please fill in all required fields!")

# View Registered Teams Section
st.markdown("<h2 class='subheader-title'>View Registered Teams</h2>", unsafe_allow_html=True)

# Display KPI Metrics
teams_count = get_metrics()
st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
st.markdown(f"""
    <div class='kpi-card'>
        <h3>Total Teams</h3>
        <p>{teams_count}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Display Registered Teams
conn = sqlite3.connect('bmca_app/databases/bmca_cricket.db')
teams_df = pd.read_sql_query("SELECT * FROM team", conn)
conn.close()

if not teams_df.empty:
    st.dataframe(teams_df)
else:
    st.info("No teams registered yet.")
