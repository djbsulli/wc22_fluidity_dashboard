"""
Shared pitch-map rendering, matching the exact visual style used
throughout the analysis notebook: expected (blue) / unexpected (red)
zone shading, dashed grid boundaries, dark touch dots, and a bottom
legend. Adapted to draw ONE player's card at a time (rather than the
fixed highest/lowest comparison pair), so it can be reused for any
player-position row the dashboard needs to show.
"""
import matplotlib.pyplot as plt
from mplsoccer import Pitch

Y_BOUNDS = [0, 18, 62, 80]
X_BOUNDS = [0, 40, 80, 120]
LATERAL_LABELS = ['Wide Left', 'Center', 'Wide Right']
DEPTH_LABELS = ['Defensive Third', 'Middle Third', 'Attacking Third']


def get_match_context(match_id, team, matches_df):
    match = matches_df[matches_df['match_id'] == match_id].iloc[0]
    opponent = match['away_team'] if match['home_team'] == team else match['home_team']
    return opponent


def render_pitch_card(row, touches, matches_df, expected_cells_mapping):
    """
    Builds one matplotlib figure for a single player-position-match row,
    in the same visual style as the notebook's comparison plots.
    Returns the figure so the caller can pass it to st.pyplot().
    """
    match_touches = touches[
        (touches['player_id'] == row['player_id']) &
        (touches['match_id'] == row['match_id']) &
        (touches['position'] == row['position'])
    ]

    opponent = get_match_context(row['match_id'], row['team'], matches_df)

    fig, ax = plt.subplots(figsize=(8, 6.2))

    pitch = Pitch(pitch_type='statsbomb', line_color='#999999', pitch_color='white', linewidth=0.8)
    pitch.draw(ax=ax)

    expected_cells = set(expected_cells_mapping.get(row['position'], []))

    for i in range(3):
        for j in range(3):
            cell = (DEPTH_LABELS[i], LATERAL_LABELS[j])
            color = '#185FA5' if cell in expected_cells else '#993C1D'
            ax.fill_between(
                [X_BOUNDS[i], X_BOUNDS[i + 1]], Y_BOUNDS[j], Y_BOUNDS[j + 1],
                color=color, alpha=0.08, zorder=1
            )

    for y_val in Y_BOUNDS[1:-1]:
        ax.hlines(y=y_val, xmin=0, xmax=120, color='#185FA5', linestyle='--', linewidth=1.2, alpha=0.6, zorder=2)
    for x_val in X_BOUNDS[1:-1]:
        ax.vlines(x=x_val, ymin=0, ymax=80, color='#993C1D', linestyle='--', linewidth=1.2, alpha=0.6, zorder=2)

    ax.scatter(
        match_touches['x'], match_touches['y'],
        color='#0B0B0B', s=45, alpha=0.7, edgecolors='white', linewidths=0.4, zorder=3
    )

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor='#185FA5', alpha=0.3, label='Expected'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#993C1D', alpha=0.3, label='Unexpected'),
    ]
    ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.03),
              ncol=2, frameon=False, fontsize=10)

    ax.set_title(
        f"{row['name']} ({row['team']}) — {row['position']}\n"
        f"{row['touches']} touches vs {opponent} — fluidity {row['fluidity_pct']:.0%}",
        fontsize=11
    )

    plt.tight_layout()
    return fig
