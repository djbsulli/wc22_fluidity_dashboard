"""
Positional Fluidity Dashboard — 2022 World Cup

Team page: pick a team -> see their fluidity trend across the whole
tournament -> pick one of their matches (chronological) -> see that
match's team fluidity score/percentile and where it sits against every
other team-match performance -> see the 3 most fluid individual
performances from that match.

Player page: pick a player (grouped by position, then alphabetical,
with their team shown) -> pick one of their matches (chronological) ->
see every qualifying position they played that match.
"""
import streamlit as st

from data_utils import (
    load_touches, load_fluidity_scores, load_team_fluidity, load_matches,
    expected_cells_mapping,
)
from plotting import (
    render_pitch_card, render_team_line_chart, render_team_swarm_highlight,
    get_match_context, ordinal,
)

st.set_page_config(page_title="Positional Fluidity — WC2022", layout="wide")

touches = load_touches()
fluidity_scores = load_fluidity_scores()
team_fluidity = load_team_fluidity()
matches_df = load_matches()

st.title("Positional Fluidity — 2022 World Cup")

page = st.sidebar.radio("View", ["Team", "Player"])


def chronological_match_labels(team_or_player_matches, matches_df, opponent_team):
    """
    Builds an ordered {label: match_id} dict, sorted chronologically by
    match_date, so the selectbox lists matches in the order they were
    actually played rather than alphabetically.
    """
    info = matches_df[matches_df['match_id'].isin(team_or_player_matches)][
        ['match_id', 'match_date', 'competition_stage']
    ].sort_values('match_date')

    labels = {}
    for _, m in info.iterrows():
        opponent = get_match_context(m['match_id'], opponent_team, matches_df)
        labels[f"vs {opponent} — {m['competition_stage']}"] = m['match_id']
    return labels


# ---------------------------------------------------------------------------
# TEAM PAGE
# ---------------------------------------------------------------------------
if page == "Team":
    teams = sorted(fluidity_scores['team'].unique())
    selected_team = st.sidebar.selectbox("Select a team", teams)

    # 1. Fluidity trend across the whole tournament
    fig_line, team_line_data = render_team_line_chart(selected_team, team_fluidity, matches_df)
    st.pyplot(fig_line, use_container_width=True)

    # 2. Match selector, chronological
    team_match_ids = team_fluidity[team_fluidity['team'] == selected_team]['match_id'].tolist()
    match_labels = chronological_match_labels(team_match_ids, matches_df, selected_team)
    selected_label = st.selectbox("Select a match", list(match_labels.keys()))
    selected_match_id = match_labels[selected_label]

    # 3. Team fluidity score + percentile, and swarm highlight
    match_team_row = team_fluidity[
        (team_fluidity['team'] == selected_team) & (team_fluidity['match_id'] == selected_match_id)
    ].iloc[0]

    st.subheader(selected_label)
    col1, col2 = st.columns(2)
    col1.metric("Team Fluidity", f"{match_team_row['team_fluidity_pct']:.0%}")
    col2.metric("Percentile (all team-matches)", ordinal(match_team_row['team_fluidity_percentile']))

    st.pyplot(render_team_swarm_highlight(team_fluidity, match_team_row), use_container_width=False)

    # 4. Top 3 and bottom 3 most/least fluid individual performances this match
    match_data = fluidity_scores[
        (fluidity_scores['team'] == selected_team) & (fluidity_scores['match_id'] == selected_match_id)
    ]

    # top 3: dedupe by player using their HIGHEST-scoring position
    top_per_player = (
        match_data.sort_values('fluidity_pct', ascending=False)
        .drop_duplicates(subset='player_id', keep='first')
    )
    top3 = top_per_player.nlargest(3, 'fluidity_pct')

    # bottom 3: dedupe by player using their LOWEST-scoring position,
    # and exclude anyone already shown above in the top 3
    bottom_per_player = (
        match_data.sort_values('fluidity_pct', ascending=True)
        .drop_duplicates(subset='player_id', keep='first')
    )
    bottom_per_player = bottom_per_player[~bottom_per_player['player_id'].isin(top3['player_id'])]
    bottom3 = bottom_per_player.nsmallest(3, 'fluidity_pct')

    st.subheader("Most fluid players in Match")
    if len(top3) == 0:
        st.info("No players in this match had enough touches to qualify for a fluidity score.")
    else:
        cols = st.columns(len(top3))
        for col, (_, row) in zip(cols, top3.iterrows()):
            with col:
                fig = render_pitch_card(row, touches, matches_df, expected_cells_mapping, mode='team')
                st.pyplot(fig)

    st.subheader("Least fluid players in Match")
    if len(bottom3) == 0:
        st.info("Not enough additional qualifying players this match to show a bottom 3.")
    else:
        cols = st.columns(len(bottom3))
        for col, (_, row) in zip(cols, bottom3.iterrows()):
            with col:
                fig = render_pitch_card(row, touches, matches_df, expected_cells_mapping, mode='team')
                st.pyplot(fig)

# ---------------------------------------------------------------------------
# PLAYER PAGE
# ---------------------------------------------------------------------------
else:
   # Step 1: filter by team
    teams_list = sorted(fluidity_scores['team'].unique())
    selected_team_player_page = st.sidebar.selectbox("Select a team", teams_list)

    # Step 2: alphabetical player list, filtered to that team
    team_players = (
        fluidity_scores[fluidity_scores['team'] == selected_team_player_page][['player_id', 'name']]
        .drop_duplicates()
        .sort_values('name')
    )

    selected_label = st.sidebar.selectbox("Select a player", team_players['name'].tolist())
    selected_player_id = team_players.loc[team_players['name'] == selected_label, 'player_id'].iloc[0]

    player_data_all = fluidity_scores[fluidity_scores['player_id'] == selected_player_id]
    player_team = player_data_all['team'].iloc[0]

    # match selector, chronological
    player_match_ids = player_data_all['match_id'].tolist()
    match_labels = chronological_match_labels(player_match_ids, matches_df, player_team)
    selected_match_label = st.selectbox("Select a match", list(match_labels.keys()))
    selected_match_id = match_labels[selected_match_label]

    match_rows = player_data_all[player_data_all['match_id'] == selected_match_id]

    st.subheader(f"{selected_label} — {selected_match_label}")

    if len(match_rows) == 1:
        # single card: constrain to a narrower column so it doesn't stretch
        # full page width and look oversized next to the team page's 3-across layout
        narrow_col = st.columns([1, 2, 1])[1]
        with narrow_col:
            fig = render_pitch_card(match_rows.iloc[0], touches, matches_df, expected_cells_mapping, mode='player')
            st.pyplot(fig)
    else:
        cols = st.columns(len(match_rows))
        for col, (_, row) in zip(cols, match_rows.iterrows()):
            with col:
                fig = render_pitch_card(row, touches, matches_df, expected_cells_mapping, mode='player')
                st.pyplot(fig)
