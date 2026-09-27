"""
Positional Fluidity Dashboard — 2022 World Cup

Two pages:
- Team: pick a team, pick one of their matches, see the 3 most fluid
  player-position performances in that match (deduplicated by player).
- Player: pick a player, pick one of their matches, see every
  qualifying position they played in that match.
"""
import streamlit as st

from data_utils import (
    load_touches, load_fluidity_scores, load_team_fluidity, load_matches,
    expected_cells_mapping,
)
from plotting import render_pitch_card, get_match_context

st.set_page_config(page_title="Positional Fluidity — WC2022", layout="wide")

touches = load_touches()
fluidity_scores = load_fluidity_scores()
team_fluidity = load_team_fluidity()
matches_df = load_matches()

st.title("Positional Fluidity — 2022 World Cup")

page = st.sidebar.radio("View", ["Team", "Player"])

# ---------------------------------------------------------------------------
# TEAM PAGE
# ---------------------------------------------------------------------------
if page == "Team":
    teams = sorted(fluidity_scores['team'].unique())
    selected_team = st.sidebar.selectbox("Select a team", teams)

    team_matches = fluidity_scores[fluidity_scores['team'] == selected_team]['match_id'].unique()
    match_labels = {}
    for mid in team_matches:
        opponent = get_match_context(mid, selected_team, matches_df)
        stage = matches_df.loc[matches_df['match_id'] == mid, 'competition_stage'].iloc[0]
        match_labels[f"vs {opponent} — {stage}"] = mid

    selected_label = st.selectbox("Select a match", list(match_labels.keys()))
    selected_match_id = match_labels[selected_label]

    match_data = fluidity_scores[
        (fluidity_scores['team'] == selected_team) &
        (fluidity_scores['match_id'] == selected_match_id)
    ]

    # dedupe by player: keep only their highest-scoring position this match
    top_per_player = (
        match_data.sort_values('fluidity_pct', ascending=False)
        .drop_duplicates(subset='player_id', keep='first')
    )
    top3 = top_per_player.nlargest(3, 'fluidity_pct')

    st.subheader(f"Most fluid performances — {selected_label}")

    if len(top3) == 0:
        st.info("No players in this match had enough touches to qualify for a fluidity score.")
    else:
        cols = st.columns(len(top3))
        for col, (_, row) in zip(cols, top3.iterrows()):
            with col:
                fig = render_pitch_card(row, touches, matches_df, expected_cells_mapping)
                st.pyplot(fig)

# ---------------------------------------------------------------------------
# PLAYER PAGE
# ---------------------------------------------------------------------------
else:
    players = sorted(fluidity_scores['name'].unique())
    selected_player = st.sidebar.selectbox("Select a player", players)

    player_data_all = fluidity_scores[fluidity_scores['name'] == selected_player]
    player_matches = player_data_all['match_id'].unique()
    player_team = player_data_all['team'].iloc[0]

    match_labels = {}
    for mid in player_matches:
        opponent = get_match_context(mid, player_team, matches_df)
        stage = matches_df.loc[matches_df['match_id'] == mid, 'competition_stage'].iloc[0]
        match_labels[f"vs {opponent} — {stage}"] = mid

    selected_label = st.selectbox("Select a match", list(match_labels.keys()))
    selected_match_id = match_labels[selected_label]

    match_rows = player_data_all[player_data_all['match_id'] == selected_match_id]

    st.subheader(f"{selected_player} — {selected_label}")

    cols = st.columns(len(match_rows)) if len(match_rows) > 1 else [st]
    for col, (_, row) in zip(cols, match_rows.iterrows()):
        with (col if col is not st else st.container()):
            fig = render_pitch_card(row, touches, matches_df, expected_cells_mapping)
            st.pyplot(fig)
