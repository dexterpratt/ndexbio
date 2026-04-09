"""
NDExBio Trial Analysis - Figure Generation

Produces matplotlib figures for the Observations section.
Cytoscape-based figures (interaction graph, thread diagram) are
handled separately by the analyst agent using the Cytoscape MCP.

Each make_* function produces one figure and saves it to disk.
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from .config import AGENTS, FIGURE_DPI, FIGURE_FORMAT, ROLE_CATEGORY_COLORS

# Consistent style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
})


def _agent_color(username: str) -> str:
    agent = AGENTS.get(username)
    return agent.color if agent else "#999999"


def _agent_label(username: str) -> str:
    agent = AGENTS.get(username)
    return agent.display_name if agent else username


def _save(fig, output_dir: str, name: str):
    path = Path(output_dir) / f"{name}.{FIGURE_FORMAT}"
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved {path}")
    return str(path)


# ===================================================================
# Figure 1: Activity Timeline
# ===================================================================

def make_activity_timeline(metrics: dict, output_dir: str) -> str:
    """
    Stacked bar chart: networks published per day, colored by agent.
    Shows the community pulse over the observation period.
    """
    activity = metrics["activity"]
    by_agent = activity["by_agent"]

    # Collect all dates
    all_dates = set()
    for agent_data in by_agent.values():
        all_dates.update(agent_data.get("by_date", {}).keys())
    if not all_dates:
        print("  WARNING: No dated networks found, skipping activity timeline")
        return ""
    dates = sorted(all_dates)

    # Build matrix: agents x dates
    agent_names = sorted(by_agent.keys(), key=lambda a: AGENTS.get(a, AGENTS.get(a, None)).role_category if AGENTS.get(a) else "zzz")
    matrix = np.zeros((len(agent_names), len(dates)))
    for i, agent in enumerate(agent_names):
        for j, date in enumerate(dates):
            matrix[i, j] = by_agent.get(agent, {}).get("by_date", {}).get(date, 0)

    fig, ax = plt.subplots(figsize=(12, 5))

    bottom = np.zeros(len(dates))
    for i, agent in enumerate(agent_names):
        ax.bar(
            range(len(dates)), matrix[i], bottom=bottom,
            color=_agent_color(agent), label=_agent_label(agent),
            width=0.8, edgecolor="white", linewidth=0.3,
        )
        bottom += matrix[i]

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Networks Published")
    ax.set_title("Community Activity Over Time")
    ax.legend(loc="upper left", fontsize=7, ncol=2, framealpha=0.9)

    return _save(fig, output_dir, "fig_activity_timeline")


# ===================================================================
# Figure 2: Interaction Heatmap
# ===================================================================

def make_interaction_heatmap(metrics: dict, output_dir: str) -> str:
    """
    Heatmap of agent-to-agent interactions (replies + cross-references).
    Rows = initiating agent, Columns = target agent.
    """
    interactions = metrics["interactions"]
    ref_matrix = interactions["reference_matrix"]

    # Use all agents that appear in the data, ordered by config
    active_agents = sorted(
        set(ref_matrix.keys()) | {
            t for targets in ref_matrix.values() for t in targets
        },
        key=lambda a: list(AGENTS.keys()).index(a) if a in AGENTS else 999
    )

    if len(active_agents) < 2:
        print("  WARNING: Fewer than 2 agents with interactions, skipping heatmap")
        return ""

    n = len(active_agents)
    matrix = np.zeros((n, n))
    for i, from_agent in enumerate(active_agents):
        for j, to_agent in enumerate(active_agents):
            matrix[i, j] = ref_matrix.get(from_agent, {}).get(to_agent, 0)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

    labels = [_agent_label(a) for a in active_agents]
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Referenced Agent")
    ax.set_ylabel("Referencing Agent")
    ax.set_title("Cross-Agent References")

    # Annotate cells with counts
    for i in range(n):
        for j in range(n):
            val = int(matrix[i, j])
            if val > 0:
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=8, color="white" if val > matrix.max() * 0.6 else "black")

    fig.colorbar(im, ax=ax, label="Reference Count", shrink=0.8)

    return _save(fig, output_dir, "fig_interaction_heatmap")


# ===================================================================
# Figure 3: Triage Funnel
# ===================================================================

def make_triage_funnel(metrics: dict, output_dir: str) -> str:
    """
    Funnel diagram for research agents' literature triage.
    Side-by-side funnels if multiple research agents have data.
    """
    funnels = metrics["triage_funnel"]["by_agent"]
    if not funnels:
        print("  WARNING: No triage funnel data, skipping")
        return ""

    agents = sorted(funnels.keys())
    n_agents = len(agents)

    fig, axes = plt.subplots(1, n_agents, figsize=(4 * n_agents, 6), squeeze=False)

    for idx, agent in enumerate(agents):
        ax = axes[0, idx]
        data = funnels[agent]
        tiers = ["tier1_scan", "tier2_review", "tier3_analysis"]
        tier_labels = ["Scanned", "Reviewed", "Deep Analysis"]
        values = [data.get(t, 0) for t in tiers]

        # Draw horizontal bars, centered, decreasing width
        max_val = max(values) if max(values) > 0 else 1
        colors = ["#264653", "#2A9D8F", "#E9C46A"]

        for i, (val, label, color) in enumerate(zip(values, tier_labels, colors)):
            width = val / max_val * 0.9
            left = (1 - width) / 2
            ax.barh(2 - i, width, left=left, height=0.7, color=color,
                    edgecolor="white", linewidth=1)
            ax.text(0.5, 2 - i, f"{label}\n{val}", ha="center", va="center",
                    fontsize=9, fontweight="bold")

        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 2.7)
        ax.set_title(_agent_label(agent), fontsize=10)
        ax.axis("off")

        # Add selectivity annotation
        if data.get("overall_selectivity") is not None:
            ax.text(0.5, -0.3,
                    f"Overall: {data['overall_selectivity']:.1%} selected",
                    ha="center", va="center", fontsize=8, style="italic")

    fig.suptitle("Literature Triage Funnel", fontsize=13, y=0.98)

    return _save(fig, output_dir, "fig_triage_funnel")


# ===================================================================
# Figure 4: Knowledge Accumulation Curve
# ===================================================================

def make_accumulation_curve(metrics: dict, output_dir: str) -> str:
    """
    Cumulative edges (or nodes) over time, colored by agent.
    Shows knowledge growing in the community.
    """
    timeline = metrics["accumulation"]["timeline"]
    if not timeline:
        print("  WARNING: No accumulation data, skipping")
        return ""

    # Group by agent, build cumulative per-agent
    agent_cumulative = defaultdict(lambda: {"dates": [], "edges": []})
    running = defaultdict(int)

    for point in timeline:
        agent = point["agent"]
        running[agent] += point.get("cumulative_edges", 0) - (
            agent_cumulative[agent]["edges"][-1] if agent_cumulative[agent]["edges"] else 0
        )
        # Actually, just use per-network edge count
        pass

    # Simpler approach: just plot the global cumulative
    dates = [p.get("date", "") for p in timeline]
    cum_edges = [p["cumulative_edges"] for p in timeline]
    cum_networks = [p["cumulative_networks"] for p in timeline]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(range(len(dates)), cum_edges, color="#264653", linewidth=2, label="Cumulative Edges")
    ax1.set_ylabel("Cumulative Edges", color="#264653")
    ax1.tick_params(axis="y", labelcolor="#264653")

    ax2 = ax1.twinx()
    ax2.plot(range(len(dates)), cum_networks, color="#E76F51", linewidth=2,
             linestyle="--", label="Cumulative Networks")
    ax2.set_ylabel("Cumulative Networks", color="#E76F51")
    ax2.tick_params(axis="y", labelcolor="#E76F51")

    # Sparse x-axis labels
    if len(dates) > 20:
        step = max(1, len(dates) // 15)
        ticks = list(range(0, len(dates), step))
    else:
        ticks = list(range(len(dates)))
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([dates[i] for i in ticks], rotation=45, ha="right", fontsize=8)

    ax1.set_title("Knowledge Accumulation Over Time")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    return _save(fig, output_dir, "fig_accumulation_curve")


# ===================================================================
# Figure 5: Schema Diversity Heatmap
# ===================================================================

def make_schema_diversity(metrics: dict, output_dir: str) -> str:
    """
    Heatmap of property key usage by agent.
    Convention keys highlighted separately.
    """
    schema = metrics["schema_diversity"]
    by_agent = schema["by_agent"]

    if not by_agent:
        print("  WARNING: No schema data, skipping")
        return ""

    # Collect all property keys across agents
    all_keys = set()
    for agent_schema in by_agent.values():
        all_keys.update(agent_schema.get("node_property_keys", []))
        all_keys.update(agent_schema.get("edge_property_keys", []))
        all_keys.update(agent_schema.get("network_property_keys", []))

    if not all_keys:
        return ""

    keys = sorted(all_keys)
    agents = sorted(by_agent.keys())

    # Build presence matrix
    matrix = np.zeros((len(keys), len(agents)))
    for j, agent in enumerate(agents):
        agent_keys = (
            set(by_agent[agent].get("node_property_keys", []))
            | set(by_agent[agent].get("edge_property_keys", []))
            | set(by_agent[agent].get("network_property_keys", []))
        )
        for i, key in enumerate(keys):
            matrix[i, j] = 1 if key in agent_keys else 0

    fig, ax = plt.subplots(figsize=(max(8, len(agents) * 1.2), max(6, len(keys) * 0.3)))
    im = ax.imshow(matrix, cmap="Blues", aspect="auto", interpolation="nearest")

    ax.set_xticks(range(len(agents)))
    ax.set_xticklabels([_agent_label(a) for a in agents], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(keys)))

    # Color convention keys differently in y-axis labels
    from .config import CONVENTION_PROPERTIES
    ylabels = []
    for key in keys:
        if key in CONVENTION_PROPERTIES:
            ylabels.append(f"* {key}")
        else:
            ylabels.append(f"  {key}")
    ax.set_yticklabels(ylabels, fontsize=7, fontfamily="monospace")

    ax.set_title("Schema Diversity: Property Key Usage by Agent\n(* = convention key)")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Property Key")

    # Add convention fraction annotation
    conv = schema["convention_surface"]
    ax.text(
        0.5, -0.12,
        f"Convention keys: {len(conv['convention_keys'])} of {len(conv['convention_keys']) + len(conv['invented_keys'])} total "
        f"({conv['convention_fraction']:.0%})",
        transform=ax.transAxes, ha="center", fontsize=9, style="italic",
    )

    return _save(fig, output_dir, "fig_schema_diversity")


# ===================================================================
# Figure 6: Network Size Distributions
# ===================================================================

def make_size_distributions(metrics: dict, output_dir: str) -> str:
    """Box plots of network sizes by message type."""
    by_type = metrics["size_distributions"]["by_type"]
    if not by_type:
        print("  WARNING: No size data, skipping")
        return ""

    types = sorted(by_type.keys())
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Node counts
    node_data = [by_type[t]["nodes"].get("count", 0) for t in types]
    # We need the raw values, not stats. Reconstruct from by_agent raw data.
    # Since we only have stats here, we'll show bar charts of medians with ranges.

    medians_n = [by_type[t]["nodes"].get("median", 0) for t in types]
    mins_n = [by_type[t]["nodes"].get("min", 0) for t in types]
    maxs_n = [by_type[t]["nodes"].get("max", 0) for t in types]

    x = range(len(types))
    ax1.bar(x, medians_n, color="#2A9D8F", alpha=0.8, edgecolor="white")
    ax1.errorbar(x, medians_n,
                 yerr=[
                     [m - mn for m, mn in zip(medians_n, mins_n)],
                     [mx - m for m, mx in zip(medians_n, maxs_n)],
                 ],
                 fmt="none", ecolor="black", capsize=3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(types, rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Node Count")
    ax1.set_title("Network Size by Type (Nodes)")

    # Edge counts
    medians_e = [by_type[t]["edges"].get("median", 0) for t in types]
    mins_e = [by_type[t]["edges"].get("min", 0) for t in types]
    maxs_e = [by_type[t]["edges"].get("max", 0) for t in types]

    ax2.bar(x, medians_e, color="#E76F51", alpha=0.8, edgecolor="white")
    ax2.errorbar(x, medians_e,
                 yerr=[
                     [m - mn for m, mn in zip(medians_e, mins_e)],
                     [mx - m for m, mx in zip(medians_e, maxs_e)],
                 ],
                 fmt="none", ecolor="black", capsize=3)
    ax2.set_xticks(x)
    ax2.set_xticklabels(types, rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Edge Count")
    ax2.set_title("Network Size by Type (Edges)")

    fig.suptitle("Network Size Distributions", fontsize=13, y=1.02)
    fig.tight_layout()

    return _save(fig, output_dir, "fig_size_distributions")


# ===================================================================
# Figure 7: Vital Signs Summary Table (as figure)
# ===================================================================

def make_vital_signs_table(metrics: dict, output_dir: str) -> str:
    """
    Render a summary table as a figure for inclusion in the paper.
    One row per agent with key stats.
    """
    activity = metrics["activity"]["by_agent"]

    agents = sorted(activity.keys(), key=lambda a: list(AGENTS.keys()).index(a) if a in AGENTS else 999)

    headers = ["Agent", "Role", "Networks", "Content", "Nodes", "Edges", "Active Days"]
    rows = []
    colors = []

    for agent in agents:
        d = activity[agent]
        agent_def = AGENTS.get(agent)
        rows.append([
            _agent_label(agent),
            agent_def.role if agent_def else "",
            str(d["total"]),
            str(d["content"]),
            str(d["node_total"]),
            str(d["edge_total"]),
            str(len(d.get("by_date", {}))),
        ])
        colors.append(_agent_color(agent))

    fig, ax = plt.subplots(figsize=(14, 1 + 0.4 * len(rows)))
    ax.axis("off")

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    # Style header
    for j in range(len(headers)):
        cell = table[0, j]
        cell.set_facecolor("#264653")
        cell.set_text_props(color="white", fontweight="bold")

    # Color agent name cells
    for i, color in enumerate(colors):
        table[i + 1, 0].set_text_props(fontweight="bold")
        # Light tint of agent color for row
        table[i + 1, 0].set_facecolor(color + "30")  # 30 = ~19% alpha in hex

    ax.set_title("Community Vital Signs", fontsize=13, pad=20)

    return _save(fig, output_dir, "fig_vital_signs_table")


# ===================================================================
# Generate all figures
# ===================================================================

def generate_all(metrics: dict, output_dir: str) -> dict[str, str]:
    """
    Generate all matplotlib figures. Returns dict of name -> filepath.

    NOTE: Cytoscape-based figures (interaction graph, thread narrative
    diagram) are NOT generated here. They require the Cytoscape MCP
    and are produced by the analyst agent interactively.
    See cytoscape_workflow.md for instructions.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    print(f"Generating figures in {out}/")

    paths = {}
    paths["activity_timeline"] = make_activity_timeline(metrics, output_dir)
    paths["interaction_heatmap"] = make_interaction_heatmap(metrics, output_dir)
    paths["triage_funnel"] = make_triage_funnel(metrics, output_dir)
    paths["accumulation_curve"] = make_accumulation_curve(metrics, output_dir)
    paths["schema_diversity"] = make_schema_diversity(metrics, output_dir)
    paths["size_distributions"] = make_size_distributions(metrics, output_dir)
    paths["vital_signs_table"] = make_vital_signs_table(metrics, output_dir)

    return {k: v for k, v in paths.items() if v}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m analysis.figures <metrics.json> [output_dir]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        m = json.load(f)
    out = sys.argv[2] if len(sys.argv) > 2 else "output/figures"
    generate_all(m, out)
