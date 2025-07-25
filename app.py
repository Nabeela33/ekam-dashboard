import streamlit as st
import pandas as pd
import os

# File paths
scoreboard_file = "EKAM 2025-ScoreBoard.xlsx"
schedule_file = "Scoring Schedule 2025.xlsx"

# Streamlit config
st.set_page_config(page_title="EKAM 2025 Sports Dashboard", layout="wide")

# Global font styling for the entire app
st.markdown("""
    <style>
        html, body, [class*="st-"] {
            font-family: 'Segoe UI', sans-serif !important;
            font-size: 14px !important;
        }
        h1 {
            font-size: 48px !important;
        }
        h2 {
            font-size: 30px !important;
        }
        h3 {
            font-size: 26px !important;
        }
        h4 {
            font-size: 22px !important;
        }
        h5, h6, label {
            font-size: 18px !important;
        }
        .stTabs [role="tab"] {
            font-size: 18px !important;
            font-weight: 600 !important;
        }
        .stMetricValue {
            font-size: 24px !important;
            font-weight: bold;
        }
        .stDataFrame, .stTable {
            font-size: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)


# Sidebar: Theme toggle
with st.sidebar:
    st.markdown("---")
    st.header("🎨 Display Settings")
    theme_mode = st.radio("Select Theme Mode", ["Light", "Dark"], index=0)

# Apply dark theme styling
if theme_mode == "Dark":
    dark_style = """
        <style>
        html, body, [class*="st-"] {
            background-color: #121212 !important;
            color: #f0f0f0 !important;
        }
        .stApp {
            background-color: #121212 !important;
        }
        h1, h2, h3, h4, h5, h6, label {
            color: #f0f0f0 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #1c1c1c !important;
        }
        .stDownloadButton, .stButton button {
            background-color: #333 !important;
            color: #f0f0f0 !important;
            border: 1px solid #555 !important;
        }
        hr {
            border-color: #444 !important;
        }
        </style>
    """
    st.markdown(dark_style, unsafe_allow_html=True)

# Title
st.markdown("""
    <h1 style='text-align: center;'>
        🏆 
        <span style='color:#00008B;'>E</span>
        <span style='color:#87CEEB;'>K</span>
        <span style='color:#800000;'>A</span>
        <span style='color:#F4EE00;'>M</span>
        2025 - Sports Dashboard
    </h1>
""", unsafe_allow_html=True)

def display_event_with_rounds(tab, df, emoji, title):
    if df is None or df.empty:
        return

    if "Round" in df.columns:
        unique_rounds = df["Round"].dropna().astype(str).str.strip().unique()
        for round_name in sorted(unique_rounds, key=lambda x: (
            "round" in x.lower(),
            int("".join(filter(str.isdigit, x))) if any(char.isdigit() for char in x) else 99,
            x.lower()
        )):
            round_df = df[df["Round"].astype(str).str.strip().str.lower() == round_name.strip().lower()]
            filtered_df = apply_common_filters(round_df)
            display_df = filtered_df.drop(columns=["Round"], errors="ignore")
            if not display_df.empty:
                with tab.expander(f"{emoji} {title} - {round_name.strip().title()}", expanded=False):
                    st.dataframe(display_df, use_container_width=True)
    else:
        st.warning(f"⚠️ 'Round' column not found in {title} sheet.")

try:
    score_xls = pd.ExcelFile(scoreboard_file)
    schedule_xls = pd.ExcelFile(schedule_file)

    score_df = pd.read_excel(score_xls, sheet_name="Schedule")
    team_points_df = pd.read_excel(score_xls, sheet_name="Team Standing", skiprows=2)
    team_points_df = team_points_df[team_points_df["Team Name"].str.lower() != "total"]

    badminton_men_df = pd.read_excel(schedule_xls, sheet_name="Badminton Men's Singles", skiprows=2)
    badminton_women_df = pd.read_excel(schedule_xls, sheet_name="Badminton Women's Singles", skiprows=2)
    badminton_womendoubles_df = pd.read_excel(schedule_xls, sheet_name="Badminton Women's Doubles", skiprows=2)
    badminton_mendoubles_df = pd.read_excel(schedule_xls, sheet_name="Badminton Men's Doubles", skiprows=2)
    badminton_mixeddoubles_df = pd.read_excel(schedule_xls, sheet_name="Badminton Mixed Doubles", skiprows=2)
    TT_men_df = pd.read_excel(schedule_xls, sheet_name="TT Men's Singles", skiprows=2)
    TT_women_df = pd.read_excel(schedule_xls, sheet_name="TT Women's Singles", skiprows=2)
    TT_womendoubles_df = pd.read_excel(schedule_xls, sheet_name="TT Women's Doubles", skiprows=2)
    TT_mendoubles_df = pd.read_excel(schedule_xls, sheet_name="TT Men's Doubles", skiprows=2)
    chess_df = pd.read_excel(schedule_xls, sheet_name="Chess", skiprows=2)
    carrom_df = pd.read_excel(schedule_xls, sheet_name="Carrom", skiprows=2)
    ludo_df = pd.read_excel(schedule_xls, sheet_name="Ludo", skiprows=2)
    dart_df = pd.read_excel(schedule_xls, sheet_name="Dart", skiprows=2)
    sudoku_df = pd.read_excel(schedule_xls, sheet_name="Sudoku", skiprows=2)

    with st.sidebar:
        st.markdown("---")
        st.header("🔍 Filters")
        all_teams = set(score_df["Team Name"].dropna().unique())
        all_player = set(score_df["Player"].dropna().unique())
        selected_team = st.selectbox("Select Team", ["All"] + sorted(all_teams))
        selected_player = st.selectbox("Select Player", ["All"] + sorted(all_player))

    selected_gender = None
    if selected_player != "All":
        gender_row = score_df[score_df["Player"].astype(str).str.lower() == selected_player.lower()]
        if not gender_row.empty and "M/F" in gender_row.columns:
            selected_gender = gender_row["M/F"].values[0].strip().upper()

    def apply_common_filters(df):
        if selected_team != "All":
            team_filters = []
            for col in ["Team Name", "Team Name1", "Team Name2", "Team Name3", "Team Name4"]:
                if col in df.columns:
                    team_filters.append(df[col] == selected_team)
            if team_filters:
                df = df[pd.concat(team_filters, axis=1).any(axis=1)]
        if selected_player != "All":
            player_filters = []
            for col in ["Player", "Player Name1", "Player Name2","Player Name3", "Player Name4", "Player Name"]:
                if col in df.columns:
                    player_filters.append(df[col].astype(str).str.contains(selected_player, case=False, na=False))
            if player_filters:
                df = df[pd.concat(player_filters, axis=1).any(axis=1)]
        return df

    match_cols = ["Date", "Match No", "Round", "Game"]
    valid_matches_df = score_df.dropna(subset=match_cols)
    unique_matches = valid_matches_df[match_cols].drop_duplicates().shape[0]
    unique_teams = score_df["Team Name"].dropna().nunique()
    unique_players = score_df["Player"].dropna().nunique()

    # Custom styling for centered and larger metric display
    st.markdown("""
        <style>
        .metric-container {
            text-align: center;
            padding: 10px;
            border-radius: 12px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .metric-header {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #000;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Metric display using HTML
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-header">⚔️ Matches Played</div>
                <div class="metric-value">{unique_matches:,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-header">🧑‍🧑 Teams Participating</div>
                <div class="metric-value">{unique_teams:,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-header">🎽 Total Players</div>
                <div class="metric-value">{unique_players:,}</div>
            </div>
        """, unsafe_allow_html=True)


    tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Team & Player Points", 
        "🏸 Badminton Events",
        "🏓 TT Events",
        "♟ Chess Events",
        "🔴 Carrom Events",
        "🎲 Ludo Events",
        "🎯 Dart Events",
        "🔢 Sudoku Events"
    ])

    with tab2:
        score_df["Team Points"] = pd.to_numeric(score_df["Team Points"], errors="coerce")
        team_totals = (
            score_df.dropna(subset=["Team Name"])
            .groupby("Team Name")["Team Points"]
            .sum()
            .sort_values(ascending=False)
        )
    
        # Logo mapping
        team_logos = {
            "Apollo Order": "https://i.postimg.cc/xXYhzV64/Apollo-Order.png",
            "Athena Army": "https://i.postimg.cc/jLyB2S4f/Athena-Army.png",
            "EKAM": "https://i.postimg.cc/kD0k7bK9/EKAM.png",
            "Hercules Unit": "https://i.postimg.cc/PNpgG4L2/Hercules-Unit.png",
            "Hydra Syndicate": "https://i.postimg.cc/Pvw9mXGB/Hydra-Syndicate.png",
            "Kraken Crew": "https://i.postimg.cc/G8N68BfF/Kraken-Crew.png",
            "Spartan Brigade": "https://i.postimg.cc/G89ZmPX3/Spartan-Brigade.png",
            "Titan Batallion": "https://i.postimg.cc/B8mr37cw/Titan-Batallion.png",
            "Zeus Legion": "https://i.postimg.cc/KKG6dhLM/Zeus-Legion.png",
            "Hermes Herd": "https://i.postimg.cc/L5NxyZNv/Hermes-Herd.png"
        }
    
        # Style setup
        st.markdown("""
            <style>
                .team-card {
                    border-radius: 12px;
                    background: linear-gradient(135deg, #f0f2f5, #e4e7ed);
                    padding: 16px 20px;
                    margin-bottom: 16px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.06);
                }
                .team-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .team-left {
                    display: flex;
                    align-items: center;
                    gap: 14px;
                }
                .team-logo {
                    height: 60px;
                    width: 60px;
                    object-fit: contain;
                    background-color: #fff;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                }
                .team-name {
                    font-size: 22px;
                    font-weight: 700;
                    color: #222;
                }
                .team-points {
                    font-size: 20px;
                    font-weight: 600;
                    color: #444;
                }
                .medal {
                    font-size: 26px;
                    margin-right: 6px;
                }
            </style>
        """, unsafe_allow_html=True)
    
        medals = ["🥇", "🥈", "🥉"]
        for idx, team in enumerate(team_totals.index):
            team_total = int(team_totals[team])
            group = score_df[score_df["Team Name"] == team]
            team_players_df = (
                group[["Player", "Team Points"]]
                .dropna(subset=["Player"])
                .groupby("Player", as_index=False)
                .sum()
                .sort_values("Team Points", ascending=False)
            )
    
            logo_url = team_logos.get(team, "")
            medal = medals[idx] if idx < 3 else ""
    
            card_html = f"""
                <div class="team-card">
                    <div class="team-header">
                        <div class="team-left">
                            {'<img src="' + logo_url + '" class="team-logo">' if logo_url else ''}
                            <span class="team-name">{medal} {team}</span>
                        </div>
                        <div class="team-points">{team_total} pts</div>
                    </div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    
            with st.expander("🔍 Player Details"):
                st.dataframe(team_players_df, use_container_width=True)



    with tab3:
        if selected_gender in [None, "M"]:
            if not badminton_men_df.empty:
                display_event_with_rounds(tab3, badminton_men_df, "🏸", "Badminton - Men's Singles")
            if not badminton_mendoubles_df.empty:
                display_event_with_rounds(tab3, badminton_mendoubles_df, "🏸", "Badminton - Men's Doubles")

        if selected_gender in [None, "F"]:
            if not badminton_women_df.empty:
                display_event_with_rounds(tab3, badminton_women_df, "🏸", "Badminton - Women's Singles")
            if not badminton_womendoubles_df.empty:
                display_event_with_rounds(tab3, badminton_womendoubles_df, "🏸", "Badminton - Women's Doubles")

        if not badminton_mixeddoubles_df.empty:
            display_event_with_rounds(tab3, badminton_mixeddoubles_df, "🏸", "Badminton - Mixed Doubles")

    with tab4:
        if selected_gender in [None, "M"]:
            display_event_with_rounds(tab4, TT_men_df, "🏓", "TT - Men's Singles")
            display_event_with_rounds(tab4, TT_mendoubles_df, "🏓", "TT - Men's Doubles")
        if selected_gender in [None, "F"]:
            display_event_with_rounds(tab4, TT_women_df, "🏓", "TT - Women's Singles")
            display_event_with_rounds(tab4, TT_womendoubles_df, "🏓", "TT - Women's Doubles")

    with tab5:
        display_event_with_rounds(tab5, chess_df, "♟", "Chess")

    with tab6:
        display_event_with_rounds(tab6, carrom_df, "🔴", "Carrom")

    with tab7:
        display_event_with_rounds(tab7, ludo_df, "🎲", "Ludo")

    with tab8:
        display_event_with_rounds(tab8, dart_df, "🎯", "Dart")

    with tab9:
        display_event_with_rounds(tab9, sudoku_df, "🔢", "Sudoku")

except FileNotFoundError as fnf_err:
    st.error(f"❌ File not found: `{fnf_err.filename}`")
except Exception as e:
    st.error(f"⚠️ An unexpected error occurred:\n\n`{str(e)}`")
