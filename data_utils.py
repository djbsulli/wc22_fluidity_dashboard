"""
Loads the three parquet files the dashboard needs, cached so Streamlit
doesn't reload them on every widget interaction. Also holds the final
expected_cells_mapping, needed by the plotting module to shade each
position's expected/deviation zones.
"""
import streamlit as st
import pandas as pd

@st.cache_data
def load_touches():
    return pd.read_parquet('data/wc2022_fluidity_score_touches.parquet')


@st.cache_data
def load_fluidity_scores():
    return pd.read_parquet('data/wc2022_player_match_fluidity_results.parquet')


@st.cache_data
def load_team_fluidity():
    return pd.read_parquet('data/wc2022_team_match_fluidity_results.parquet')


@st.cache_data
def load_matches():
    return pd.read_parquet('data/matches_metadata.parquet')


# Final expected-zone mapping, copied from the analysis notebook.
# Must stay in sync with whatever was used to compute fluidity_pct.
expected_cells_mapping = {
    'Center Back': [
        ('Defensive Third', 'Wide Left'), ('Defensive Third', 'Center'), ('Defensive Third', 'Wide Right'),
        ('Middle Third', 'Center'),
    ],
    'Defensive Midfield': [
        ('Defensive Third', 'Center'),
        ('Middle Third', 'Center'),
        ('Attacking Third', 'Center'),
    ],
    'Central Midfield': [
        ('Defensive Third', 'Center'),
        ('Middle Third', 'Center'),
        ('Attacking Third', 'Center'),
    ],
    'Attacking Midfield': [
        ('Middle Third', 'Center'),
        ('Attacking Third', 'Wide Left'), ('Attacking Third', 'Center'), ('Attacking Third', 'Wide Right'),
    ],
    'Center Forward': [
        ('Middle Third', 'Center'),
        ('Attacking Third', 'Wide Left'), ('Attacking Third', 'Center'), ('Attacking Third', 'Wide Right'),
    ],
    'Left Back': [
        ('Defensive Third', 'Wide Left'), ('Middle Third', 'Wide Left'), ('Attacking Third', 'Wide Left'),
    ],
    'Right Back': [
        ('Defensive Third', 'Wide Right'), ('Middle Third', 'Wide Right'), ('Attacking Third', 'Wide Right'),
    ],
    'Left Wing Back': [
        ('Defensive Third', 'Wide Left'), ('Middle Third', 'Wide Left'), ('Attacking Third', 'Wide Left'),
    ],
    'Right Wing Back': [
        ('Defensive Third', 'Wide Right'), ('Middle Third', 'Wide Right'), ('Attacking Third', 'Wide Right'),
    ],
    'Left Midfield': [
        ('Defensive Third', 'Wide Left'), ('Middle Third', 'Wide Left'), ('Attacking Third', 'Wide Left'),
        ('Attacking Third', 'Center'),
    ],
    'Right Midfield': [
        ('Defensive Third', 'Wide Right'), ('Middle Third', 'Wide Right'), ('Attacking Third', 'Wide Right'),
        ('Attacking Third', 'Center'),
    ],
    'Left Wing': [
        ('Defensive Third', 'Wide Left'), ('Middle Third', 'Wide Left'), ('Attacking Third', 'Wide Left'),
        ('Attacking Third', 'Center'),
    ],
    'Right Wing': [
        ('Defensive Third', 'Wide Right'), ('Middle Third', 'Wide Right'), ('Attacking Third', 'Wide Right'),
        ('Attacking Third', 'Center'),
    ],
}
