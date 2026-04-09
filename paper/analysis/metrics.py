"""
NDExBio Trial Analysis - Metrics Computation

Takes the extracted dataset (from extract.py) and computes all
programmatic metrics for the Observations section.

Each compute_* function returns a dict that becomes one section
of the metrics output. The top-level compute_all() assembles them.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import (
    AGENTS,
    CONVENTION_PROPERTIES,
    REQUIRED_PROPERTIES,
    ROLE_CATEGORIES,
    TEAMS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _date_str(s: str | None) -> str | None:
    """Extract YYYY-MM-DD from an ISO timestamp."""
    dt = _parse_iso(s)
    return dt.strftime("%Y-%m-%d") if dt else None


def _networks_excluding_self_knowledge(networks: list[dict]) -> list[dict]:
    """Filter out self-knowledge networks for analyses that focus on content."""
    return [n for n in networks if not n.get("is_self_knowledge", False)]


# ---------------------------------------------------------------------------
# 1. Activity Overview / Vital Signs
# ---------------------------------------------------------------------------

def compute_activity(networks: list[dict]) -> dict:
    """
    Basic vital signs: counts by agent, by date, by type.
    """
    by_agent = defaultdict(lambda: {
        "total": 0, "content": 0, "self_knowledge": 0,
        "node_total": 0, "edge_total": 0,
        "by_type": Counter(), "by_date": Counter(),
    })

    daily_total = Counter()  # date -> count across all agents

    for n in networks:
        agent = n.get("agent_username", "unknown")
        rec = by_agent[agent]
        rec["total"] += 1

        if n.get("is_self_knowledge"):
            rec["self_knowledge"] += 1
        else:
            rec["content"] += 1

        rec["node_total"] += n.get("node_count", 0)
        rec["edge_total"] += n.get("edge_count", 0)

        msg_type = n.get("ndex_message_type", "unknown")
        rec["by_type"][msg_type] += 1

        date = _date_str(n.get("creation_time"))
        if date:
            rec["by_date"][date] += 1
            daily_total[date] += 1

    # Convert Counters to plain dicts for JSON
    result = {}
    for agent, rec in by_agent.items():
        result[agent] = {
            **rec,
            "by_type": dict(rec["by_type"]),
            "by_date": dict(rec["by_date"]),
        }

    return {
        "by_agent": result,
        "daily_total": dict(daily_total),
        "total_networks": len(networks),
        "total_content_networks": len(_networks_excluding_self_knowledge(networks)),
    }


# ---------------------------------------------------------------------------
# 2. Interaction Matrix and Threading
# ---------------------------------------------------------------------------

def compute_interactions(networks: list[dict]) -> dict:
    """
    Build the interaction matrix from ndex-reply-to and UUID cross-references.
    Also compute thread chains and response latencies.
    """
    # --- Interaction matrix (from reply-to) ---
    reply_matrix = defaultdict(lambda: defaultdict(int))  # from -> to -> count
    reply_edges = []  # detailed list

    # --- Interaction matrix (from all UUID references) ---
    ref_matrix = defaultdict(lambda: defaultdict(int))

    # --- Build UUID lookup for timestamps ---
    uuid_to_record = {n["uuid"]: n for n in networks}

    for n in networks:
        agent = n.get("agent_username", "")

        # Reply-to links
        reply_to_agent = n.get("reply_to_agent")
        reply_to_uuid = n.get("ndex_reply_to", "")
        if reply_to_agent and reply_to_agent != agent:
            reply_matrix[agent][reply_to_agent] += 1
            # Compute latency
            parent = uuid_to_record.get(reply_to_uuid)
            latency_hours = None
            if parent:
                t1 = parent.get("creation_epoch_ms")
                t2 = n.get("creation_epoch_ms")
                if t1 and t2:
                    latency_hours = round((t2 - t1) / 3600000, 2)
            reply_edges.append({
                "from_agent": agent,
                "from_uuid": n["uuid"],
                "from_name": n.get("name", ""),
                "to_agent": reply_to_agent,
                "to_uuid": reply_to_uuid,
                "latency_hours": latency_hours,
                "message_type": n.get("ndex_message_type", ""),
            })

        # Cross-references (broader: any UUID pointing to another agent's network)
        for ref in n.get("resolved_references", []):
            if ref.get("is_cross_agent") and ref.get("owner"):
                ref_matrix[agent][ref["owner"]] += 1

    # --- Thread chains (follow reply-to chains) ---
    # Build parent -> children map
    reply_to_map = {}  # child_uuid -> parent_uuid
    for n in networks:
        rt = n.get("ndex_reply_to", "")
        if rt:
            reply_to_map[n["uuid"]] = rt

    # Find chain roots (networks that are replied to but don't reply to anything,
    # or whose parent isn't in our dataset)
    all_parents = set(reply_to_map.values())
    all_children = set(reply_to_map.keys())
    roots = all_parents - all_children

    # Build forward map: parent -> [children]
    children_map = defaultdict(list)
    for child, parent in reply_to_map.items():
        children_map[parent].append(child)

    # Walk chains from roots
    chains = []
    def _walk(uuid, chain_so_far):
        chain_so_far.append(uuid)
        kids = children_map.get(uuid, [])
        if not kids:
            chains.append(list(chain_so_far))
        else:
            for kid in kids:
                _walk(kid, chain_so_far)
        chain_so_far.pop()

    for root in roots:
        _walk(root, [])

    # Annotate chains with agent info
    annotated_chains = []
    for chain in chains:
        if len(chain) < 2:
            continue  # skip trivial
        agents_in_chain = []
        teams_in_chain = set()
        steps = []
        for uuid in chain:
            rec = uuid_to_record.get(uuid)
            if rec:
                agent = rec.get("agent_username", "unknown")
                agents_in_chain.append(agent)
                agent_def = AGENTS.get(agent)
                if agent_def:
                    teams_in_chain.add(agent_def.team)
                steps.append({
                    "uuid": uuid,
                    "agent": agent,
                    "name": rec.get("name", ""),
                    "message_type": rec.get("ndex_message_type", ""),
                    "creation_time": rec.get("creation_time", ""),
                })
            else:
                agents_in_chain.append("external")
                steps.append({"uuid": uuid, "agent": "external"})

        annotated_chains.append({
            "length": len(chain),
            "agents": agents_in_chain,
            "unique_agents": len(set(agents_in_chain)),
            "teams_spanned": len(teams_in_chain),
            "is_cross_team": len(teams_in_chain) > 1,
            "steps": steps,
        })

    # Sort chains by interestingness: cross-team first, then by length
    annotated_chains.sort(
        key=lambda c: (c["is_cross_team"], c["unique_agents"], c["length"]),
        reverse=True,
    )

    # --- Classify interactions as within-team vs cross-team ---
    within_team = 0
    cross_team = 0
    for from_agent, targets in reply_matrix.items():
        from_def = AGENTS.get(from_agent)
        for to_agent, count in targets.items():
            to_def = AGENTS.get(to_agent)
            if from_def and to_def and from_def.team == to_def.team:
                within_team += count
            else:
                cross_team += count

    # --- Response latencies ---
    latencies = [e["latency_hours"] for e in reply_edges if e["latency_hours"] is not None]
    latency_stats = {}
    if latencies:
        latencies_sorted = sorted(latencies)
        latency_stats = {
            "count": len(latencies),
            "min_hours": latencies_sorted[0],
            "max_hours": latencies_sorted[-1],
            "median_hours": latencies_sorted[len(latencies_sorted) // 2],
            "mean_hours": round(sum(latencies) / len(latencies), 2),
        }

    return {
        "reply_matrix": {k: dict(v) for k, v in reply_matrix.items()},
        "reference_matrix": {k: dict(v) for k, v in ref_matrix.items()},
        "reply_edges": reply_edges,
        "total_reply_interactions": sum(
            sum(v.values()) for v in reply_matrix.values()
        ),
        "total_cross_references": sum(
            sum(v.values()) for v in ref_matrix.values()
        ),
        "within_team_replies": within_team,
        "cross_team_replies": cross_team,
        "latency_stats": latency_stats,
        "thread_chains": annotated_chains[:20],  # top 20 most interesting
        "max_thread_depth": max((c["length"] for c in annotated_chains), default=0),
        "chains_by_depth": dict(Counter(c["length"] for c in annotated_chains)),
        "cross_team_chains": len([c for c in annotated_chains if c["is_cross_team"]]),
    }


# ---------------------------------------------------------------------------
# 3. Expert / Service Agent Usage
# ---------------------------------------------------------------------------

def compute_service_usage(networks: list[dict]) -> dict:
    """Track how expert and analyst agents were used."""
    expert_agents = set(ROLE_CATEGORIES.get("expert", []))
    analyst_agents = set(ROLE_CATEGORIES.get("analyst", []))
    service_agents = expert_agents | analyst_agents

    # Find requests directed at service agents (via reply-to)
    requests = []  # networks from non-service agents replying to / referencing service agents
    responses = []  # networks from service agents replying to others

    for n in networks:
        agent = n.get("agent_username", "")
        reply_to_agent = n.get("reply_to_agent")
        msg_type = n.get("ndex_message_type", "")

        if agent not in service_agents and reply_to_agent in service_agents:
            requests.append({
                "requester": agent,
                "service_agent": reply_to_agent,
                "uuid": n["uuid"],
                "name": n.get("name", ""),
                "message_type": msg_type,
            })

        if agent in service_agents and reply_to_agent and reply_to_agent not in service_agents:
            responses.append({
                "service_agent": agent,
                "requester": reply_to_agent,
                "uuid": n["uuid"],
                "name": n.get("name", ""),
                "message_type": msg_type,
            })

    # Count by service agent
    requests_by_service = Counter(r["service_agent"] for r in requests)
    requests_by_requester = Counter(r["requester"] for r in requests)

    # Identify unused service agents
    used_services = set(requests_by_service.keys()) | {
        r["service_agent"] for r in responses
    }
    unused_services = service_agents - used_services

    return {
        "requests": requests,
        "responses": responses,
        "total_requests": len(requests),
        "total_responses": len(responses),
        "requests_by_service_agent": dict(requests_by_service),
        "requests_by_requester": dict(requests_by_requester),
        "unused_service_agents": sorted(unused_services),
    }


# ---------------------------------------------------------------------------
# 4. Triage Funnel (for research agents)
# ---------------------------------------------------------------------------

def compute_triage_funnel(networks: list[dict]) -> dict:
    """
    Compute the literature triage funnel for research agents.
    Looks for ndex-workflow tags indicating triage tier.
    """
    researcher_agents = set(ROLE_CATEGORIES.get("researcher", []))
    funnels = {}

    for agent in researcher_agents:
        agent_networks = [
            n for n in networks
            if n.get("agent_username") == agent and not n.get("is_self_knowledge")
        ]

        tier_counts = Counter()
        for n in agent_networks:
            workflow = n.get("ndex_workflow", "").lower()
            msg_type = n.get("ndex_message_type", "").lower()

            # Heuristic tier classification from workflow/type annotations
            if any(t in workflow for t in ["tier1", "scan", "triage"]):
                tier_counts["tier1_scan"] += 1
            elif any(t in workflow for t in ["tier2", "review"]):
                tier_counts["tier2_review"] += 1
            elif any(t in workflow for t in ["tier3", "deep", "analysis"]):
                tier_counts["tier3_analysis"] += 1
            elif msg_type in ("analysis", "review"):
                tier_counts["tier2_review"] += 1
            elif msg_type in ("synthesis", "hypothesis"):
                tier_counts["tier3_analysis"] += 1
            # else: uncategorized

        if tier_counts:
            t1 = tier_counts.get("tier1_scan", 0)
            t2 = tier_counts.get("tier2_review", 0)
            t3 = tier_counts.get("tier3_analysis", 0)
            funnels[agent] = {
                "tier1_scan": t1,
                "tier2_review": t2,
                "tier3_analysis": t3,
                "t1_to_t2_rate": round(t2 / t1, 3) if t1 > 0 else None,
                "t2_to_t3_rate": round(t3 / t2, 3) if t2 > 0 else None,
                "overall_selectivity": round(t3 / t1, 3) if t1 > 0 else None,
            }

    return {"by_agent": funnels}


# ---------------------------------------------------------------------------
# 5. Knowledge Accumulation
# ---------------------------------------------------------------------------

def compute_accumulation(networks: list[dict]) -> dict:
    """
    Cumulative growth of networks, nodes, and edges over time.
    Excludes self-knowledge networks.
    """
    content = _networks_excluding_self_knowledge(networks)

    # Sort by creation time
    content.sort(key=lambda n: n.get("creation_epoch_ms") or 0)

    cumulative = []
    running_networks = 0
    running_nodes = 0
    running_edges = 0

    by_agent_running = defaultdict(lambda: {"networks": 0, "nodes": 0, "edges": 0})

    for n in content:
        running_networks += 1
        running_nodes += n.get("node_count", 0)
        running_edges += n.get("edge_count", 0)

        agent = n.get("agent_username", "unknown")
        by_agent_running[agent]["networks"] += 1
        by_agent_running[agent]["nodes"] += n.get("node_count", 0)
        by_agent_running[agent]["edges"] += n.get("edge_count", 0)

        cumulative.append({
            "timestamp": n.get("creation_time"),
            "date": _date_str(n.get("creation_time")),
            "agent": agent,
            "network_name": n.get("name", ""),
            "cumulative_networks": running_networks,
            "cumulative_nodes": running_nodes,
            "cumulative_edges": running_edges,
        })

    return {
        "timeline": cumulative,
        "final_totals": {
            "networks": running_networks,
            "nodes": running_nodes,
            "edges": running_edges,
        },
        "final_by_agent": dict(by_agent_running),
    }


# ---------------------------------------------------------------------------
# 6. Schema Diversity
# ---------------------------------------------------------------------------

def compute_schema_diversity(networks: list[dict]) -> dict:
    """
    Analyze schema diversity across agents.
    """
    content = _networks_excluding_self_knowledge(networks)

    agent_schemas = defaultdict(lambda: {
        "node_types": set(),
        "edge_types": set(),
        "node_property_keys": set(),
        "edge_property_keys": set(),
        "network_property_keys": set(),
    })

    for n in content:
        agent = n.get("agent_username", "unknown")
        schema = n.get("schema")
        if not schema:
            continue
        agent_schemas[agent]["node_types"].update(schema.get("node_types", []))
        agent_schemas[agent]["edge_types"].update(schema.get("edge_types", []))
        agent_schemas[agent]["node_property_keys"].update(schema.get("node_property_keys", []))
        agent_schemas[agent]["edge_property_keys"].update(schema.get("edge_property_keys", []))
        agent_schemas[agent]["network_property_keys"].update(schema.get("network_property_keys", []))

    # Convert sets to sorted lists
    for agent in agent_schemas:
        for key in agent_schemas[agent]:
            agent_schemas[agent][key] = sorted(agent_schemas[agent][key])

    # Global unique sets
    all_node_types = set()
    all_edge_types = set()
    all_property_keys = set()
    for s in agent_schemas.values():
        all_node_types.update(s["node_types"])
        all_edge_types.update(s["edge_types"])
        all_property_keys.update(s["node_property_keys"])
        all_property_keys.update(s["edge_property_keys"])
        all_property_keys.update(s["network_property_keys"])

    # Convention vs. invented property keys
    convention_keys = all_property_keys & CONVENTION_PROPERTIES
    invented_keys = all_property_keys - CONVENTION_PROPERTIES

    # Pairwise Jaccard similarity on all property keys
    agents_list = sorted(agent_schemas.keys())
    jaccard_matrix = {}
    for i, a1 in enumerate(agents_list):
        keys1 = (
            set(agent_schemas[a1]["node_property_keys"])
            | set(agent_schemas[a1]["edge_property_keys"])
            | set(agent_schemas[a1]["network_property_keys"])
        )
        for a2 in agents_list[i + 1:]:
            keys2 = (
                set(agent_schemas[a2]["node_property_keys"])
                | set(agent_schemas[a2]["edge_property_keys"])
                | set(agent_schemas[a2]["network_property_keys"])
            )
            intersection = len(keys1 & keys2)
            union = len(keys1 | keys2)
            jaccard = round(intersection / union, 3) if union > 0 else 0.0
            jaccard_matrix[f"{a1}:{a2}"] = jaccard

    return {
        "by_agent": {k: dict(v) for k, v in agent_schemas.items()},
        "global": {
            "unique_node_types": sorted(all_node_types),
            "unique_edge_types": sorted(all_edge_types),
            "unique_property_keys": sorted(all_property_keys),
            "total_node_types": len(all_node_types),
            "total_edge_types": len(all_edge_types),
            "total_property_keys": len(all_property_keys),
        },
        "convention_surface": {
            "convention_keys": sorted(convention_keys),
            "invented_keys": sorted(invented_keys),
            "convention_fraction": round(
                len(convention_keys) / len(all_property_keys), 3
            ) if all_property_keys else 0,
        },
        "pairwise_jaccard": jaccard_matrix,
    }


# ---------------------------------------------------------------------------
# 7. Network Size Distributions
# ---------------------------------------------------------------------------

def compute_size_distributions(networks: list[dict]) -> dict:
    """Node and edge count distributions by agent and by type."""
    content = _networks_excluding_self_knowledge(networks)

    by_agent = defaultdict(lambda: {"nodes": [], "edges": []})
    by_type = defaultdict(lambda: {"nodes": [], "edges": []})

    for n in content:
        agent = n.get("agent_username", "unknown")
        msg_type = n.get("ndex_message_type", "unknown")
        nc = n.get("node_count", 0)
        ec = n.get("edge_count", 0)
        by_agent[agent]["nodes"].append(nc)
        by_agent[agent]["edges"].append(ec)
        by_type[msg_type]["nodes"].append(nc)
        by_type[msg_type]["edges"].append(ec)

    def _stats(values):
        if not values:
            return {"count": 0}
        s = sorted(values)
        return {
            "count": len(s),
            "min": s[0],
            "max": s[-1],
            "median": s[len(s) // 2],
            "mean": round(sum(s) / len(s), 1),
            "total": sum(s),
        }

    return {
        "by_agent": {
            a: {"nodes": _stats(d["nodes"]), "edges": _stats(d["edges"])}
            for a, d in by_agent.items()
        },
        "by_type": {
            t: {"nodes": _stats(d["nodes"]), "edges": _stats(d["edges"])}
            for t, d in by_type.items()
        },
    }


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def compute_all(dataset: dict) -> dict:
    """Compute all metrics from an extracted dataset."""
    networks = dataset["networks"]

    metrics = {
        "trial_id": dataset.get("trial_id"),
        "extraction_time": dataset.get("extraction_time"),
        "observation_start": dataset.get("observation_start"),
        "observation_end": dataset.get("observation_end"),
        "total_networks_extracted": len(networks),
        "activity": compute_activity(networks),
        "interactions": compute_interactions(networks),
        "service_usage": compute_service_usage(networks),
        "triage_funnel": compute_triage_funnel(networks),
        "accumulation": compute_accumulation(networks),
        "schema_diversity": compute_schema_diversity(networks),
        "size_distributions": compute_size_distributions(networks),
    }

    return metrics


def load_and_compute(dataset_path: str, output_path: str | None = None) -> dict:
    """Load extracted JSON and compute metrics."""
    with open(dataset_path) as f:
        dataset = json.load(f)

    metrics = compute_all(dataset)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(metrics, f, indent=2, default=str)
        print(f"Metrics written to {out}")

    return metrics


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m analysis.metrics <extracted_data.json> [output.json]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace("extracted_", "metrics_")
    load_and_compute(inp, out)
