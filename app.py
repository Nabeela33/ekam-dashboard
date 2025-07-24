import streamlit as st
import pandas as pd
import os

# File paths
scoreboard_file = "EKAM 2025-ScoreBoard.xlsx"
schedule_file = "Scoring Schedule 2025.xlsx"

# Streamlit config
st.set_page_config(page_title="EKAM 2025 Sports Dashboard", layout="wide")

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
        2025 - Sports Score Dashboard
    </h1>
""", unsafe_allow_html=True)

# EKAM logo top-right corner
logo_url = "https://raw.githubusercontent.com/Nabeela33/ekam-dashboard/main/logos/EKAM.png"
logo_html = f"""
<style>
.top-right-logo {{
    position: fixed;
    top: 15px;
    right: 20px;
}}
.top-right-logo img {{
    height: 60px;
}}
</style>
<div class="top-right-logo">
    <img src="{logo_url}" alt="EKAM Logo" />
</div>
"""
st.markdown(logo_html, unsafe_allow_html=True)

def display_event_with_rounds(tab, df, emoji, title):
    if df is None or df.empty:
        return  # Do nothing if df is None or empty

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

    # Schedule sheets
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

    # Determine selected player's gender
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

    col1, col2, col3 = st.columns(3)
    col1.metric("⚔️ Matches Played", f"{unique_matches:,}")
    col2.metric("🧑‍🧑 Teams Participating", f"{unique_teams:,}")
    col3.metric("🎽 Total Players", f"{unique_players:,}")

    # Tabs
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
        st.subheader("📋 Team and Player Points")
        score_df["Team Points"] = pd.to_numeric(score_df["Team Points"], errors="coerce")
        team_totals = (
            score_df.dropna(subset=["Team Name"])
            .groupby("Team Name")["Team Points"]
            .sum()
            .sort_values(ascending=False)
        )
    
        for team in team_totals.index:
            group = score_df[score_df["Team Name"] == team]
            team_total = team_totals[team]
            team_players_df = group[["Player", "Team Points"]].dropna(subset=["Player"]).copy()
            team_players_df = (
                team_players_df.groupby("Player", as_index=False)
                .sum()
                .sort_values("Team Points", ascending=False)
            )
    
            # Construct GitHub logo URL
            safe_team_name = team.replace(" ", "%20")
            logo_url = f"https://raw.githubusercontent.com/Nabeela33/ekam-dashboard/main/logos/{safe_team_name}.png"
    
            # Show logo and team name above the expander
            st.markdown(f"""
                <div style='display: flex; align-items: center; margin-bottom: -10px; margin-top: 20px;'>
                    <img src="{logo_url}" style="width:35px;height:35px;margin-right:10px;border-radius:5px;">
                    <h4 style='margin: 0px;'>{team} — {team_total:.0f}</h4>
                </div>
            """, unsafe_allow_html=True)
    
            # Expander with no label override
            with st.expander("View Players", expanded=False):
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
# EKAM Footer with Logo
footer_logo_url = "https://raw.githubusercontent.com/Nabeela33/ekam-dashboard/main/logos/EKAM.png"  # Replace with actual path
footer_html = f"""
<style>
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        background-color: transparent;
    }}
    .footer img {{
        height: 40px;
        opacity: 0.8;
    }}
</style>
<div class="footer">
    <img src="{footer_logo_url}" alt="EKAM Logo" />
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
