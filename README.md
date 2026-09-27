# wc22_fluidity_dashboard
# Positional Fluidity Dashboard — 2022 World Cup

Dashboard showing team and player level in-possession fluidity statistics from the 2022 World Cup.

## Project structure

wc2022_dashboard/
├── app.py # Streamlit app: page layout and navigation
├── plotting.py # pitch-map plot rendering
├── data_utils.py # data loading + expected_cells_mapping
├── requirements.txt
└── data/
├── wc2022_touches_zoned.parquet
├── wc2022_player_match_fluidity.parquet
├── wc2022_team_fluidity_match_scores.parquet
└── wc2022_matches_metadata.parquet


## Data notes

- **Minimum touch threshold:** 25 touches per player, per position, per match, to reduce noise from small samples.
- expected_cells_mapping` in `data_utils.py` must stay in sync with whatever was used to compute `fluidity_pct` in the source notebook — if you change the mapping, results and shading will disagree unless the parquet files are also regenerated.
- Built as a single-tournament proof of concept. Team and player averages are shown at the match level only; a full season's worth of matches would be needed before drawing conclusions about fluidity's relationship to performance or outcomes.

## Source

Event data: [StatsBomb Open Data](https://github.com/statsbomb/open-data)
