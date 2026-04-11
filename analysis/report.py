"""
NDExBio Trial Analysis - Report Assembly

Generates the Observations section of the paper as markdown,
populated with computed metrics. Also produces supplementary tables.

The output is a draft — the analyst agent or human author should
review and refine the narrative, especially the anecdote sections
which are marked with [AGENT: ...] placeholders for agentic judgment.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import AGENTS, TEAMS


def _agent_name(username: str) -> str:
    agent = AGENTS.get(username)
    return agent.display_name if agent else username


def _pct(n: float | None) -> str:
    if n is None:
        return "N/A"
    return f"{n:.1%}"


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def _section_vital_signs(metrics: dict) -> str:
    """Generate the activity overview section."""
    activity = metrics["activity"]
    total = activity["total_networks"]
    content = activity["total_content_networks"]

    lines = [
        "### Community Activity Overview\n",
        f"Over the observation period, the {len(activity['by_agent'])} agents ",
        f"published a total of **{total} networks** on NDEx, of which ",
        f"**{content}** were content networks (analyses, critiques, syntheses, ",
        f"requests, reports) and {total - content} were self-knowledge networks ",
        "(session histories, plans, collaborator maps).\n",
        "\n",
        "**Table 1** summarizes the vital signs for each agent. ",
        "**Figure 1** shows the community activity timeline.\n",
        "\n",
        "| Agent | Role | Content Networks | Total Nodes | Total Edges | Active Days |\n",
        "|-------|------|-----------------|-------------|-------------|-------------|\n",
    ]

    for username in AGENTS:
        if username not in activity["by_agent"]:
            continue
        d = activity["by_agent"][username]
        lines.append(
            f"| {_agent_name(username)} | {AGENTS[username].role} "
            f"| {d['content']} | {d['node_total']} | {d['edge_total']} "
            f"| {len(d.get('by_date', {}))} |\n"
        )

    lines.append("\n")
    return "".join(lines)


def _section_interactions(metrics: dict) -> str:
    """Generate the interaction analysis section."""
    inter = metrics["interactions"]
    total_refs = inter["total_cross_references"]
    total_replies = inter["total_reply_interactions"]
    within = inter["within_team_replies"]
    cross = inter["cross_team_replies"]
    max_depth = inter["max_thread_depth"]
    n_cross_chains = inter["cross_team_chains"]

    lines = [
        "### Inter-Agent Interaction and Discourse\n",
        "\n",
        "The central empirical question is whether agents formed a community ",
        "— interacting with and building on each other's work — rather than ",
        "simply publishing in parallel.\n",
        "\n",
        f"We observed **{total_refs} cross-agent references** across all networks ",
        f"and **{total_replies} explicit reply-to links**. ",
    ]

    if within + cross > 0:
        lines.append(
            f"Of the reply interactions, {within} were within-team and "
            f"**{cross} were cross-team** ({_pct(cross / (within + cross))} of replies). "
        )

    if max_depth > 1:
        lines.append(
            f"The longest threaded conversation chain reached **{max_depth} steps**. "
        )

    if n_cross_chains > 0:
        lines.append(
            f"We found **{n_cross_chains} cross-team interaction chains**, "
            "where agents from different teams discovered and responded to "
            "each other's work without explicit coordination. "
        )

    lines.append("\n\n")

    # Latency
    lat = inter.get("latency_stats", {})
    if lat.get("count"):
        lines.append(
            f"Response latency — the time between a network being published and "
            f"another agent publishing a response — had a median of "
            f"**{lat['median_hours']:.1f} hours** "
            f"(range: {lat['min_hours']:.1f}–{lat['max_hours']:.1f} hours, "
            f"n={lat['count']}). "
        )

    lines.append("\n\n")

    # Reference matrix as table
    ref_matrix = inter["reference_matrix"]
    active_agents = sorted(
        set(ref_matrix.keys()) | {t for targets in ref_matrix.values() for t in targets},
        key=lambda a: list(AGENTS.keys()).index(a) if a in AGENTS else 999
    )

    if len(active_agents) >= 2:
        lines.append("**Table 2: Cross-Agent Reference Matrix**\n\n")
        header = "| | " + " | ".join(_agent_name(a) for a in active_agents) + " |\n"
        sep = "|---" * (len(active_agents) + 1) + "|\n"
        lines.append(header)
        lines.append(sep)
        for from_a in active_agents:
            row = f"| **{_agent_name(from_a)}** "
            for to_a in active_agents:
                val = ref_matrix.get(from_a, {}).get(to_a, 0)
                row += f"| {val if val else '·'} "
            row += "|\n"
            lines.append(row)
        lines.append("\n")

    # Best chain anecdote placeholder
    chains = inter.get("thread_chains", [])
    if chains:
        best = chains[0]
        lines.append("#### Notable Interaction Chain\n\n")
        lines.append(
            f"The most notable interaction chain spanned **{best['unique_agents']} agents** "
            f"across **{best['teams_spanned']} teams** in {best['length']} steps:\n\n"
        )
        for i, step in enumerate(best["steps"]):
            agent_label = _agent_name(step.get("agent", ""))
            lines.append(
                f"{i + 1}. **{agent_label}** — {step.get('message_type', '?')}: "
                f"_{step.get('name', 'unnamed')}_\n"
            )
        lines.append(
            "\n[AGENT: Review this chain and write a 2-3 sentence narrative "
            "describing what happened scientifically at each step. This becomes "
            "the basis for Figure B (thread narrative diagram).]\n\n"
        )

    lines.append(
        "**Figure 2** shows the interaction heatmap. "
        "**Figure A** (Cytoscape) shows the interaction graph.\n\n"
    )

    return "".join(lines)


def _section_service_usage(metrics: dict) -> str:
    """Generate the expert/service agent usage section."""
    svc = metrics["service_usage"]

    if svc["total_requests"] == 0 and svc["total_responses"] == 0:
        return (
            "### Expert and Service Agent Usage\n\n"
            "No service requests were observed during the observation period. "
            "The expert and analyst agents (R. Zenith, R. Solstice, R. Corona, R. Nexus) "
            "were available but not consulted by other agents.\n\n"
            "[AGENT: Assess whether this reflects the trial duration, the agents' "
            "advertising effectiveness, or a design issue.]\n\n"
        )

    lines = [
        "### Expert and Service Agent Usage\n\n",
        f"We observed **{svc['total_requests']} requests** directed at expert and ",
        f"analyst agents, and **{svc['total_responses']} responses**.\n\n",
    ]

    if svc["requests_by_service_agent"]:
        lines.append("Requests by service agent:\n\n")
        for agent, count in sorted(svc["requests_by_service_agent"].items()):
            lines.append(f"- **{_agent_name(agent)}**: {count} requests\n")
        lines.append("\n")

    if svc["unused_service_agents"]:
        names = [_agent_name(a) for a in svc["unused_service_agents"]]
        lines.append(
            f"The following service agents received no requests: {', '.join(names)}.\n\n"
        )

    lines.append(
        "[AGENT: Select 1-2 examples of expert interactions that demonstrate "
        "domain-specific advice with caveats (the 'HEK 293T moment'). "
        "Describe concretely what the expert agent said and why it mattered.]\n\n"
    )

    return "".join(lines)


def _section_triage(metrics: dict) -> str:
    """Generate the triage funnel section."""
    funnels = metrics["triage_funnel"]["by_agent"]
    if not funnels:
        return (
            "### Literature Triage\n\n"
            "No triage funnel data was available for this trial.\n\n"
        )

    lines = [
        "### Literature Triage\n\n",
        "Research agents exercised selective judgment in processing the literature, ",
        "not merely consuming everything available.\n\n",
    ]

    for agent, data in sorted(funnels.items()):
        t1 = data.get("tier1_scan", 0)
        t2 = data.get("tier2_review", 0)
        t3 = data.get("tier3_analysis", 0)
        lines.append(
            f"**{_agent_name(agent)}** scanned {t1} papers, selected {t2} for review "
            f"({_pct(data.get('t1_to_t2_rate'))} acceptance), and performed deep analysis "
            f"on {t3} ({_pct(data.get('overall_selectivity'))} overall selectivity).\n\n"
        )

    lines.append("**Figure 3** shows the triage funnels.\n\n")
    return "".join(lines)


def _section_accumulation(metrics: dict) -> str:
    """Generate the knowledge accumulation section."""
    acc = metrics["accumulation"]
    totals = acc["final_totals"]

    lines = [
        "### Knowledge Accumulation\n\n",
        f"By the end of the observation period, the community had accumulated "
        f"**{totals['networks']} content networks** containing a total of "
        f"**{totals['nodes']} nodes** and **{totals['edges']} edges** ",
        "of structured knowledge.\n\n",
    ]

    by_agent = acc.get("final_by_agent", {})
    if by_agent:
        # Identify largest contributor
        largest = max(by_agent.items(), key=lambda x: x[1]["edges"])
        lines.append(
            f"The largest contributor by edge count was {_agent_name(largest[0])} "
            f"with {largest[1]['edges']} edges across {largest[1]['networks']} networks. "
        )

    lines.append(
        "\n\n**Figure 4** shows the cumulative growth of knowledge over time.\n\n"
    )
    return "".join(lines)


def _section_schema(metrics: dict) -> str:
    """Generate the schema diversity section."""
    schema = metrics["schema_diversity"]
    glob = schema["global"]
    conv = schema["convention_surface"]

    lines = [
        "### Schema Diversity\n\n",
        "A key claim of NDExBio is that CX2 imposes no constraints on data schema. ",
        "We tested this by analyzing the property keys, node types, and edge types ",
        "used across all agent-published networks.\n\n",
        f"Agents collectively used **{glob['total_node_types']} unique node types**, ",
        f"**{glob['total_edge_types']} unique edge types**, and ",
        f"**{glob['total_property_keys']} unique property keys**. ",
        f"Of these property keys, only **{len(conv['convention_keys'])}** ",
        f"({conv['convention_fraction']:.0%}) were convention-mandated; the remaining ",
        f"**{len(conv['invented_keys'])}** were invented by agents to serve their ",
        "specific purposes.\n\n",
    ]

    # Jaccard similarities
    jaccard = schema.get("pairwise_jaccard", {})
    if jaccard:
        vals = list(jaccard.values())
        avg_jaccard = sum(vals) / len(vals) if vals else 0
        lines.append(
            f"Pairwise schema similarity (Jaccard index on property key sets) "
            f"averaged **{avg_jaccard:.2f}**, indicating that agents shared the "
            "convention surface but diverged substantially in their domain-specific "
            "representations.\n\n"
        )

    lines.append("**Figure 5** shows the schema diversity heatmap.\n\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Supplementary materials
# ---------------------------------------------------------------------------

def _supplementary_network_catalog(metrics: dict, dataset: dict) -> str:
    """Full catalog of all networks published during the trial."""
    lines = [
        "## Supplementary Table S1: Complete Network Catalog\n\n",
        "| Agent | Network Name | Type | Nodes | Edges | Created |\n",
        "|-------|-------------|------|-------|-------|--------|\n",
    ]
    networks = sorted(dataset["networks"], key=lambda n: n.get("creation_time", ""))
    for n in networks:
        if n.get("is_self_knowledge"):
            continue
        lines.append(
            f"| {_agent_name(n.get('agent_username', ''))} "
            f"| {n.get('name', '')[:60]} "
            f"| {n.get('ndex_message_type', '')} "
            f"| {n.get('node_count', 0)} "
            f"| {n.get('edge_count', 0)} "
            f"| {n.get('creation_time', '')[:10]} |\n"
        )
    return "".join(lines)


def _supplementary_property_keys(metrics: dict) -> str:
    """Complete list of observed property keys."""
    schema = metrics["schema_diversity"]
    conv_keys = set(schema["convention_surface"]["convention_keys"])
    all_keys = (
        schema["global"]["unique_property_keys"]
    )

    lines = [
        "## Supplementary Table S2: Observed Property Keys\n\n",
        "| Property Key | Convention? | Agents Using |\n",
        "|-------------|-------------|-------------|\n",
    ]
    for key in sorted(all_keys):
        is_conv = "Yes" if key in conv_keys else ""
        agents_using = []
        for agent, agent_schema in schema["by_agent"].items():
            all_agent_keys = (
                set(agent_schema.get("node_property_keys", []))
                | set(agent_schema.get("edge_property_keys", []))
                | set(agent_schema.get("network_property_keys", []))
            )
            if key in all_agent_keys:
                agents_using.append(_agent_name(agent))
        lines.append(
            f"| `{key}` | {is_conv} | {', '.join(agents_using)} |\n"
        )
    return "".join(lines)


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def generate_observations_section(
    metrics: dict,
    dataset: dict | None = None,
    output_dir: str = "output",
) -> dict[str, str]:
    """
    Generate the Observations section and supplementary materials.

    Returns dict with keys:
        'observations': markdown for the main Observations section
        'supplementary': markdown for supplementary tables
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # --- Main section ---
    obs_parts = [
        "## Observed Behavior\n\n",
        _section_vital_signs(metrics),
        _section_interactions(metrics),
        _section_service_usage(metrics),
        _section_triage(metrics),
        _section_accumulation(metrics),
        _section_schema(metrics),
    ]
    observations = "".join(obs_parts)

    obs_path = out / "observations_draft.md"
    with open(obs_path, "w") as f:
        f.write(observations)
    print(f"Observations draft written to {obs_path}")

    # --- Supplementary ---
    supp_parts = [
        "# Supplementary Materials\n\n",
    ]
    if dataset:
        supp_parts.append(_supplementary_network_catalog(metrics, dataset))
        supp_parts.append("\n")
    supp_parts.append(_supplementary_property_keys(metrics))

    supplementary = "".join(supp_parts)

    supp_path = out / "supplementary_draft.md"
    with open(supp_path, "w") as f:
        f.write(supplementary)
    print(f"Supplementary draft written to {supp_path}")

    return {
        "observations": observations,
        "supplementary": supplementary,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m analysis.report <metrics.json> [dataset.json] [output_dir]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        m = json.load(f)
    d = None
    if len(sys.argv) > 2 and sys.argv[2] != "-":
        with open(sys.argv[2]) as f:
            d = json.load(f)
    out = sys.argv[3] if len(sys.argv) > 3 else "output"
    generate_observations_section(m, d, out)
