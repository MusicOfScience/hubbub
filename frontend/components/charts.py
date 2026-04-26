"""Plotly chart components for election visualisation."""
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats


def probability_bell_curve(mean: float, std: float, win_threshold: float = 0) -> go.Figure:
    """
    Render a probability bell curve (normal distribution).
    mean: projected margin
    std: standard deviation
    win_threshold: 0 means ALP wins if margin > 0
    """
    x = np.linspace(mean - 4 * std, mean + 4 * std, 400)
    y = stats.norm.pdf(x, mean, std)

    fig = go.Figure()

    # Shade ALP win region (right of threshold)
    x_alp = x[x >= win_threshold]
    y_alp = y[x >= win_threshold]
    fig.add_trace(go.Scatter(
        x=x_alp, y=y_alp, fill="tozeroy",
        fillcolor="rgba(229,57,53,0.25)", line=dict(color="#E53935"),
        name="ALP Win", hoverinfo="skip"
    ))

    # Shade LIB win region (left of threshold)
    x_lib = x[x < win_threshold]
    y_lib = y[x < win_threshold]
    fig.add_trace(go.Scatter(
        x=x_lib, y=y_lib, fill="tozeroy",
        fillcolor="rgba(21,101,192,0.25)", line=dict(color="#1565C0"),
        name="LIB Win", hoverinfo="skip"
    ))

    # Bell curve line
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color="#333", width=2),
        name="Distribution", hoverinfo="skip"
    ))

    # Vertical line at mean
    fig.add_vline(x=mean, line_dash="dash", line_color="#555", annotation_text=f"Projected: {int(mean):+,}")
    fig.add_vline(x=win_threshold, line_dash="dot", line_color="#999", annotation_text="Even")

    fig.update_layout(
        title="Projected Margin Distribution",
        xaxis_title="Margin (votes, + = ALP)",
        yaxis_title="Probability Density",
        showlegend=True,
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(gridcolor="#eee")
    fig.update_yaxes(gridcolor="#eee", showticklabels=False)
    return fig


def tcp_progress_chart(vote_types_df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart of TCP votes by vote type."""
    if vote_types_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No TCP data available")
        return fig

    fig = go.Figure()

    alp_cols = [c for c in vote_types_df.columns if "alp" in c.lower() or "chen" in c.lower()]
    lib_cols = [c for c in vote_types_df.columns if "lib" in c.lower() or "morrison" in c.lower()]
    type_col = "vote_type" if "vote_type" in vote_types_df.columns else vote_types_df.columns[0]

    if alp_cols and lib_cols:
        fig.add_trace(go.Bar(
            name="ALP (Chen)",
            x=vote_types_df[type_col],
            y=vote_types_df[alp_cols[0]],
            marker_color="#E53935",
        ))
        fig.add_trace(go.Bar(
            name="LIB (Morrison)",
            x=vote_types_df[type_col],
            y=vote_types_df[lib_cols[0]],
            marker_color="#1565C0",
        ))
        fig.update_layout(barmode="stack")

    fig.update_layout(
        title="TCP Votes by Vote Type",
        xaxis_title="Vote Type",
        yaxis_title="Votes",
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def booth_swing_chart(booths_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of booth-level swings."""
    if booths_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No booth swing data")
        return fig

    swing_col = "alp_tcp_swing" if "alp_tcp_swing" in booths_df.columns else None
    size_col = "enrolled" if "enrolled" in booths_df.columns else None
    name_col = "booth_name" if "booth_name" in booths_df.columns else booths_df.columns[0]

    x_col = "alp_primary_pct_curr" if "alp_primary_pct_curr" in booths_df.columns else booths_df.columns[0]

    if swing_col is None:
        fig = go.Figure()
        fig.update_layout(title="No swing data columns found")
        return fig

    colors = ["#E53935" if s > 0 else "#1565C0" for s in booths_df[swing_col]]

    fig = go.Figure(go.Scatter(
        x=booths_df[x_col] if x_col in booths_df.columns else list(range(len(booths_df))),
        y=booths_df[swing_col],
        mode="markers+text",
        text=booths_df[name_col] if name_col in booths_df.columns else "",
        textposition="top center",
        marker=dict(
            color=colors,
            size=booths_df[size_col] / 200 if size_col else 10,
            opacity=0.75,
        ),
        hovertemplate="%{text}<br>Swing: %{y:.1f}%<extra></extra>"
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="#999")
    fig.update_layout(
        title="Booth-Level ALP TCP Swing",
        xaxis_title="ALP Primary %",
        yaxis_title="TCP Swing (pp)",
        height=400,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def outstanding_requirement_chart(required_df: pd.DataFrame) -> go.Figure:
    """Bar chart showing required vote shares from outstanding votes."""
    if required_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No outstanding vote data")
        return fig

    fig = px.bar(
        required_df,
        x="vote_type" if "vote_type" in required_df.columns else required_df.columns[0],
        y="required_pct" if "required_pct" in required_df.columns else required_df.columns[-1],
        color_discrete_sequence=["#E53935"],
        title="Required % of Outstanding Votes (ALP to Win)",
    )
    fig.add_hline(y=50, line_dash="dash", line_color="#1565C0", annotation_text="50% threshold")
    fig.update_layout(
        height=350,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def historical_comparison_chart(history_df: pd.DataFrame) -> go.Figure:
    """Line/bar chart of historical vs current party vote shares."""
    if history_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No historical data")
        return fig

    fig = go.Figure()
    colour_map = {"ALP": "#E53935", "LIB": "#1565C0", "GRN": "#2E7D32", "IND": "#757575"}

    for col in history_df.columns:
        if col in ("election", "year", "date", "booth_id"):
            continue
        party = col.split("_")[0].upper()
        colour = colour_map.get(party, "#757575")
        fig.add_trace(go.Bar(
            name=col,
            x=history_df.get("election", history_df.index.astype(str)),
            y=history_df[col],
            marker_color=colour,
        ))

    fig.update_layout(
        barmode="group",
        title="Historical Vote Comparison",
        xaxis_title="Election",
        yaxis_title="Vote Share (%)",
        height=350,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def scenario_matrix_chart(scenarios_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of scenario outcomes."""
    if scenarios_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No scenario data")
        return fig

    margin_col = "projected_margin" if "projected_margin" in scenarios_df.columns else scenarios_df.columns[-1]
    x_col = "swing_variation" if "swing_variation" in scenarios_df.columns else scenarios_df.columns[0]

    colors = ["#E53935" if v > 0 else "#1565C0" for v in scenarios_df[margin_col]]

    fig = go.Figure(go.Scatter(
        x=scenarios_df[x_col],
        y=scenarios_df[margin_col],
        mode="markers",
        marker=dict(color=colors, size=6, opacity=0.6),
        hovertemplate=f"{x_col}: %{{x:.2f}}<br>Margin: %{{y:,}}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="#999", annotation_text="Toss-up")
    fig.update_layout(
        title="Scenario Outcome Matrix",
        xaxis_title=x_col.replace("_", " ").title(),
        yaxis_title="Projected Margin (+ = ALP)",
        height=400,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig
