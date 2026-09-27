"""
Shared plotting functions for the dashboard: pitch-map cards (team and
player views use different title layouts), a single team's fluidity
trend line across the tournament, and a swarm plot highlighting one
match's team-fluidity score against every other team-match performance.
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from mplsoccer import Pitch
import seaborn as sns

Y_BOUNDS = [0, 18, 62, 80]
X_BOUNDS = [0, 40, 80, 120]
LATERAL_LABELS = ['Wide Left', 'Center', 'Wide Right']
DEPTH_LABELS = ['Defensive Third', 'Middle Third', 'Attacking Third']

LINE_COLOR = '#0C447C'
HIGHLIGHT_COLOR = '#993C1D'
BASE_COLOR = '#888780'


def ordinal(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def get_match_context(match_id, team, matches_df):
    match = matches_df[matches_df['match_id'] == match_id].iloc[0]
    opponent = match['away_team'] if match['home_team'] == team else match['home_team']
    return opponent


def render_pitch_card(row, touches, matches_df, expected_cells_mapping, mode='team'):
    """
    Builds one pitch-map figure for a single player-position-match row.

    mode='team'   -> 4-line title: Name / Position / Touches / Fluidity% (Xth Percentile Position)
                     Sized for a 3-across column layout.
    mode='player' -> 3-line title: Position / Touches / Fluidity% (Xth percentile for Position)
                     Sized smaller, since the player page often renders just one card at
                     full column width, which would otherwise look oversized versus team view.
    """
    match_touches = touches[
        (touches['player_id'] == row['player_id']) &
        (touches['match_id'] == row['match_id']) &
        (touches['position'] == row['position'])
    ]

    if mode == 'team':
        figsize = (8, 7.2)
        title_fontsize = 11
        legend_fontsize = 10
        dot_size = 45
    else:
        figsize = (6, 5.4)
        title_fontsize = 9.5
        legend_fontsize = 8.5
        dot_size = 32

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('white')

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
        color='#0B0B0B', s=dot_size, alpha=0.7, edgecolors='white', linewidths=0.4, zorder=3
    )

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor='#185FA5', alpha=0.3, label='Expected'),
        plt.Rectangle((0, 0), 1, 1, facecolor='#993C1D', alpha=0.3, label='Unexpected'),
    ]
    ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.03),
              ncol=2, frameon=False, fontsize=legend_fontsize)

    percentile = ordinal(row['fluidity_percentile_position'])

    if mode == 'team':
        pct_label = f"{row['fluidity_pct']:.0%} ({percentile} Percentile {row['broad_position']})"
        title = f"{row['name']}\n{row['position']}\n{row['touches']} touches\n{pct_label}"
    else:
        pct_label = f"{row['fluidity_pct']:.0%} ({percentile} percentile for {row['broad_position']})"
        title = f"{row['position']}\n{row['touches']} touches\n{pct_label}"

    ax.set_title(title, fontsize=title_fontsize, pad=12)

    plt.tight_layout(rect=[0, 0, 1, 0.90])
    return fig


def render_team_line_chart(team, team_fluidity, matches_df):
    """
    Line chart of one team's fluidity across all their matches, in
    chronological order, with each point labeled by opponent. Sized to
    fill the full page width with generous text, tight x-axis margins
    so the line runs edge-to-edge rather than floating in whitespace.
    """
    team_data = team_fluidity[team_fluidity['team'] == team].copy()
    team_data = team_data.merge(matches_df[['match_id', 'match_date']], on='match_id', how='left')
    team_data = team_data.sort_values('match_date')
    team_data['game_number'] = range(1, len(team_data) + 1)

    fig, ax = plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor('white')

    ax.plot(
        team_data['game_number'], team_data['team_fluidity_pct'],
        marker='o', linewidth=2.5, markersize=10, color=LINE_COLOR
    )
    for _, row in team_data.iterrows():
        ax.annotate(
            row['opponent'], (row['game_number'], row['team_fluidity_pct']),
            xytext=(0, 14), textcoords='offset points',
            ha='center', fontsize=8, fontweight='bold', color='#0B0B0B',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2)
        )

    ax.set_xlim(0.5, len(team_data) + 0.5)
    ax.set_ylim(0.1,0.4)
    ax.margins(y=0.15)
    ax.set_xticks(team_data['game_number'])
    ax.tick_params(axis='both', labelsize=10)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xlabel('Game Number', fontsize=10, style='italic')
    ax.set_ylabel('Fluidity (%)', fontsize=10, style='italic')
    ax.set_title(f'{team} — Fluidity Across the Tournament', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.2)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    return fig, team_data


def render_team_swarm_highlight(team_fluidity, highlighted_row):
    """
    Swarm plot of every team-match fluidity score (all 128 rows), with
    the selected match's own performance highlighted and labeled.
    Sized small/compact, matching the line chart above it.
    """
    plot_data = team_fluidity.reset_index(drop=True).copy()
    plot_data['group'] = ''

    overall_mean = plot_data['team_fluidity_pct'].mean()

    data_min, data_max = plot_data['team_fluidity_pct'].min(), plot_data['team_fluidity_pct'].max()
    pad = (data_max - data_min) * 0.12
    xlim_low, xlim_high = data_min - pad, data_max + pad

    fig, ax = plt.subplots(figsize=(6, 2.6))
    fig.patch.set_facecolor('white')

    ax.axvspan(overall_mean, xlim_high, color='#185FA5', alpha=0.05, zorder=0)
    ax.axvspan(xlim_low, overall_mean, color='#993C1D', alpha=0.05, zorder=0)
    ax.axvline(x=overall_mean, color='#0B0B0B', linestyle='--', linewidth=0.8, alpha=0.7, zorder=2)

    sns.swarmplot(data=plot_data, x='team_fluidity_pct', y='group', size=3.5, color=BASE_COLOR, ax=ax)

    ax.text(overall_mean, 0.56, 'Tournament average', fontsize=6, style='italic', va='bottom', ha='left', color='#0B0B0B')

    ax.scatter(
        highlighted_row['team_fluidity_pct'], 0,
        color=HIGHLIGHT_COLOR, s=50, zorder=5, edgecolors='white', linewidths=0.6
    )
    ax.annotate(
        "Selected Match",
        (highlighted_row['team_fluidity_pct'], 0),
        xytext=(0, 10), textcoords='offset points',
        ha='center', va='bottom', fontsize=6, fontweight='bold', color=HIGHLIGHT_COLOR
    )

    ax.set_xlim(xlim_low, xlim_high)
    ax.set_ylim(-0.4, 0.65)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.tick_params(axis='x', labelsize=5)
    ax.set_yticks([])
    ax.set_ylabel('')
    ax.set_xlabel('Fluidity (%)', fontsize=7, style='italic')
    ax.set_title('Vs All Team-Match Scores', fontsize=8, fontweight='bold')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis='x', alpha=0.15)

    plt.tight_layout()
    return fig
