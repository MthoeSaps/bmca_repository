import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            league TEXT NOT NULL,
            season TEXT NOT NULL,
            payment_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_number TEXT NOT NULL UNIQUE,
            dob DATE NOT NULL,
            contact_number TEXT NOT NULL,
            email_address TEXT NOT NULL,
            fee REAL NOT NULL,
            team_id INTEGER,
            payment_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')
    conn.commit()
    conn.close()

# Function to register a player
def register_player(name, id_number, dob, contact, email, team_id, payment_status):
    fee = 2.0
    try:
        conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO players (name, id_number, dob, contact_number, email_address, fee, team_id, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, id_number, dob, contact, email, fee, team_id, payment_status))
        conn.commit()
        conn.close()
        st.success(f"✅ Player {name} registered successfully!")
    except sqlite3.IntegrityError:
        st.warning("⚠️ Player with this ID Number already registered!")

# Function to register a team
def register_team(team_name, league, season, payment_status):
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO teams (team_name, league, season, payment_status)
        VALUES (?, ?, ?, ?)
    ''', (team_name, league, season, payment_status))
    conn.commit()
    conn.close()
    st.success(f"✅ Team {team_name} registered successfully!")

# Function to retrieve registered players
def get_players():
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    df = pd.read_sql_query("SELECT * FROM players", conn)
    conn.close()
    return df

# Function to retrieve teams
def get_teams():
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    df = pd.read_sql_query("SELECT * FROM teams", conn)
    conn.close()
    return df

# Function to edit a player
def edit_player(player_id, name, id_number, dob, contact, email, team_id, payment_status):
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('''
        UPDATE players
        SET name = ?, id_number = ?, dob = ?, contact_number = ?, email_address = ?, team_id = ?, payment_status = ?
        WHERE id = ?
    ''', (name, id_number, dob, contact, email, team_id, payment_status, player_id))
    conn.commit()
    conn.close()
    st.success("✅ Player updated successfully!")

# Function to delete a player
def delete_player(player_id):
    conn = sqlite3.connect('c:/Users/mthoe/OneDrive/Desktop/bmca_app/databases/bmca_cricket.db')
    c = conn.cursor()
    c.execute('DELETE FROM players WHERE id = ?', (player_id,))
    conn.commit()
    conn.close()
    st.success("🗑️ Player deleted successfully!")

# Initialize the database
init_db()

# Streamlit App Layout
st.title("🏏 BMCA Cricket Registration Platform")

# Team Registration Section
st.header("🏆 Register a Team")
with st.form("team_registration_form"):
    team_name = st.text_input("🏅 Team Name")
    league = st.selectbox("📋 League", ["First League Men's", "First League Women's", "Second League Men's", "Second League Women's"])
    season = st.selectbox("📅 Season", ["2024/2025", "2025/2026", "2026/2027"])
    payment_status = st.checkbox("✅ Payment Received")
    if st.form_submit_button("✅ Register Team"):
        register_team(team_name, league, season, payment_status)

# Player Registration Section
st.header("👤 Register a Player")
teams_df = get_teams()
team_options = [(row['id'], row['team_name']) for index, row in teams_df.iterrows()]

with st.form("player_registration_form"):
    name = st.text_input("👤 Player Name")
    id_number = st.text_input("🆔 ID Number")
    dob = st.date_input("📅 Date of Birth")
    contact = st.text_input("📞 Contact Number")
    email = st.text_input("✉️ Email Address")
    
    # Select Team Dropdown
    team_id = st.selectbox("🏅 Select Team", [team[1] for team in team_options], index=0 if team_options else -1)
    selected_team_id = team_options[[team[1] for team in team_options].index(team_id)][0] if team_options else None
    
    payment_status = st.checkbox("✅ Registration Fee Paid")
    
    submitted = st.form_submit_button("✅ Register Player")
    
    if submitted and selected_team_id:
        register_player(name, id_number, dob, contact, email, selected_team_id, payment_status)
    elif submitted:
        st.warning("⚠️ Please select a team.")

# Management Platform Section
st.header("📋 Manage Players")

# Search and Filter
search_term = st.text_input("🔍 Search Players")
players_df = get_players()

if search_term:
    players_df = players_df[players_df['name'].str.contains(search_term, case=False)]

# KPI Metric Cards
total_players = len(players_df)
total_fee_collected = total_players * 2  # Assuming $2 fee per player
average_age = (pd.to_datetime('today') - pd.to_datetime(players_df['dob'])).dt.days // 365 if not players_df.empty else 0

st.markdown("""
    <style>
        .kpi-card {
            display: inline-block;
            width: 150px;
            padding: 10px;
            margin: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
            background-color: #f9f9f9;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="kpi-card">
        <h4>Total Players</h4>
        <p>{total_players}</p>
    </div>
    <div class="kpi-card">
        <h4>Total Fee Collected</h4>
        <p>${total_fee_collected}</p>
    </div>
    <div class="kpi-card">
        <h4>Average Age</h4>
        <p>{average_age} years</p>
    </div>
""", unsafe_allow_html=True)

# Player Management
if not players_df.empty:
    for index, row in players_df.iterrows():
        with st.expander(row['name']):
            name = st.text_input("👤 Player Name", value=row['name'], key=f"name_{row['id']}")
            id_number = st.text_input("🆔 ID Number", value=row['id_number'], key=f"id_number_{row['id']}")
            dob = st.date_input("📅 Date of Birth", value=pd.to_datetime(row['dob']).date(), key=f"dob_{row['id']}")
            contact = st.text_input("📞 Contact Number", value=row['contact_number'], key=f"contact_{row['id']}")
            email = st.text_input("✉️ Email Address", value=row['email_address'], key=f"email_{row['id']}")
            
            # Select Team Dropdown for Editing
            team_id = st.selectbox("🏅 Select Team", [team[1] for team in team_options], index=[team[1] for team in team_options].index(row['team_id']), key=f"team_{row['id']}")
            selected_team_id = team_options[[team[1] for team in team_options].index(team_id)][0] if team_options else None
            
            payment_status = st.checkbox("✅ Registration Fee Paid", value=row['payment_status'], key=f"payment_{row['id']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                    edit_player(row['id'], name, id_number, dob, contact, email, selected_team_id, payment_status)
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                    delete_player(row['id'])
                    st.experimental_rerun()  # Refresh the app to update the player list

else:
    st.warning("⚠️ No players registered! Please register players first.")

# Display Timestamps
st.subheader("📅 Registration Timestamps")

teams_df = get_teams()
if not teams_df.empty:
    st.write("### Teams Registered")
    for index, row in teams_df.iterrows():
        st.write(f"- **{row['team_name']}** (Registered on: {row['created_at']})")

players_df = get_players()
if not players_df.empty:
    st.write("### Players Registered")
    for index, row in players_df.iterrows():
        st.write(f"- **{row['name']}** (Registered on: {row['created_at']})")

st.header("📋 Submit Team List")
if st.button("✅ Submit Team List"):
    if players_df.empty:
        st.warning("⚠️ No players registered! Please register players first.")
    else:
        st.success("✅ Team list submitted successfully!")
