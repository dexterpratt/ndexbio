"""Local Store MCP Server — exposes local graph database operations as MCP tools.

Provides cached, queryable access to NDEx networks via a two-tier
local store (SQLite catalog + LadybugDB graph database).

Run with:  python -m tools.local_store.server [--profile NAME] [--cache-dir PATH]
"""

import argparse
import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from ndex2.cx2 import CX2Network

from tools.ndex_mcp.config import load_ndex_config, has_credentials
from tools.ndex_mcp.ndex_client_wrapper import NDExClientWrapper
from tools.local_store.store import LocalStore

mcp = FastMCP("local_store", log_level="INFO")

_store: LocalStore | None = None
_ndex: NDExClientWrapper | None = None


def _get_store() -> LocalStore:
    global _store
    if _store is None:
        _store = LocalStore()
    return _store


def _get_ndex() -> NDExClientWrapper | None:
    global _ndex
    return _ndex


# ── Catalog Operations ───────────────────────────────────────────────


@mcp.tool()
def query_catalog(
    category: str | None = None,
    agent: str | None = None,
    data_type: str | None = None,
) -> dict:
    """List cached networks, optionally filtered by category, agent, or data_type.

    Categories: science-kg, interaction-data, plan, episodic-memory,
    collaborator-map, review-log, request, message.

    Args:
        category: Filter by network category.
        agent: Filter by owning agent (rdaneel, drh, etc.).
        data_type: Filter by data type (graph, tabular, agent-state).
    """
    store = _get_store()
    filters = {}
    if category:
        filters["category"] = category
    if agent:
        filters["agent"] = agent
    if data_type:
        filters["data_type"] = data_type
    results = store.query_catalog(**filters)
    return {
        "status": "success",
        "count": len(results),
        "networks": results,
    }


@mcp.tool()
def get_cached_network(network_uuid: str) -> dict:
    """Get catalog metadata for a cached network.

    Args:
        network_uuid: UUID of the network.
    """
    store = _get_store()
    entry = store.get_catalog_entry(network_uuid)
    if entry is None:
        return {"status": "error", "message": f"Network {network_uuid} not in cache"}
    return {"status": "success", "data": entry}


# ── Graph Queries ────────────────────────────────────────────────────


@mcp.tool()
def query_graph(cypher: str) -> dict:
    """Execute a Cypher query against the local graph database.

    The graph contains BioNode and Network node tables with Interacts
    and InNetwork relationship tables. BioNode properties: id, cx2_id,
    network_uuid, name, node_type, properties (MAP).

    Example queries:
    - Neighborhood: MATCH (n:BioNode {name: 'TRIM25'})-[r:Interacts]-(m) RETURN m.name, r.interaction
    - Cross-network: MATCH (n:BioNode)-[:InNetwork]->(net1:Network {uuid: 'X'}) ...
    - Path: MATCH path = (a:BioNode {name: 'NS1'})-[:Interacts*1..3]-(b:BioNode {name: 'RIG-I'}) RETURN path

    Args:
        cypher: Cypher query string.
    """
    store = _get_store()
    try:
        rows = store.query_graph(cypher)
        return {
            "status": "success",
            "row_count": len(rows),
            "rows": rows,
        }
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def get_network_nodes(network_uuid: str) -> dict:
    """Get all nodes for a cached network.

    Args:
        network_uuid: UUID of the network.
    """
    store = _get_store()
    nodes = store.graph.get_network_nodes(network_uuid)
    return {
        "status": "success",
        "count": len(nodes),
        "nodes": nodes,
    }


@mcp.tool()
def get_network_edges(network_uuid: str) -> dict:
    """Get all edges for a cached network.

    Args:
        network_uuid: UUID of the network.
    """
    store = _get_store()
    edges = store.graph.get_network_edges(network_uuid)
    return {
        "status": "success",
        "count": len(edges),
        "edges": edges,
    }


@mcp.tool()
def find_neighbors(node_name: str, network_uuid: str | None = None) -> dict:
    """Find all neighbors of a node by name.

    Args:
        node_name: Name of the node to find neighbors for.
        network_uuid: Optional — restrict to a specific network.
    """
    store = _get_store()
    if network_uuid:
        query = (
            "MATCH (n:BioNode {name: $name, network_uuid: $uuid})"
            "-[r:Interacts]-(m:BioNode) "
            "RETURN m.name, m.node_type, r.interaction, r.network_uuid"
        )
        rows = store.query_graph(query, {"name": node_name, "uuid": network_uuid})
    else:
        query = (
            "MATCH (n:BioNode {name: $name})-[r:Interacts]-(m:BioNode) "
            "RETURN DISTINCT m.name, m.node_type, r.interaction, r.network_uuid"
        )
        rows = store.query_graph(query, {"name": node_name})
    neighbors = [
        {"name": r[0], "type": r[1], "interaction": r[2], "network_uuid": r[3]}
        for r in rows
    ]
    return {"status": "success", "count": len(neighbors), "neighbors": neighbors}


@mcp.tool()
def find_path(
    source_name: str,
    target_name: str,
    max_hops: int = 4,
) -> dict:
    """Find paths between two nodes by name across all cached networks.

    Args:
        source_name: Name of the source node.
        target_name: Name of the target node.
        max_hops: Maximum path length (default 4).
    """
    store = _get_store()
    query = (
        f"MATCH path = (a:BioNode {{name: $src}})"
        f"-[:Interacts*1..{max_hops}]-"
        f"(b:BioNode {{name: $tgt}}) "
        f"RETURN nodes(path), length(path) AS hops "
        f"ORDER BY hops LIMIT 10"
    )
    try:
        rows = store.query_graph(query, {"src": source_name, "tgt": target_name})
        paths = []
        for r in rows:
            node_names = [n.get("name", "") if isinstance(n, dict) else str(n) for n in r[0]]
            paths.append({"nodes": node_names, "hops": r[1]})
        return {"status": "success", "count": len(paths), "paths": paths}
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
def find_contradictions(network_uuid_1: str, network_uuid_2: str) -> dict:
    """Find contradictions: same node pair with opposite interaction types across two networks.

    Args:
        network_uuid_1: UUID of the first network.
        network_uuid_2: UUID of the second network.
    """
    store = _get_store()
    query = (
        "MATCH (a:BioNode)-[r1:Interacts {network_uuid: $uuid1}]->(b:BioNode), "
        "      (c:BioNode)-[r2:Interacts {network_uuid: $uuid2}]->(d:BioNode) "
        "WHERE a.name = c.name AND b.name = d.name "
        "  AND ((r1.interaction CONTAINS 'ecreases' AND r2.interaction CONTAINS 'ncreases') "
        "    OR (r1.interaction CONTAINS 'ncreases' AND r2.interaction CONTAINS 'ecreases')) "
        "RETURN a.name, b.name, r1.interaction, r2.interaction"
    )
    rows = store.query_graph(query, {"uuid1": network_uuid_1, "uuid2": network_uuid_2})
    contradictions = [
        {
            "source": r[0], "target": r[1],
            "interaction_1": r[2], "interaction_2": r[3],
            "network_1": network_uuid_1, "network_2": network_uuid_2,
        }
        for r in rows
    ]
    return {"status": "success", "count": len(contradictions), "contradictions": contradictions}


# ── Cache Management ─────────────────────────────────────────────────


@mcp.tool()
def cache_network(network_uuid: str, agent: str | None = None, category: str | None = None) -> dict:
    """Download a network from NDEx and cache it in the local store.

    Downloads the CX2 data, imports it into the graph database, and
    creates a catalog entry. If the network is already cached, it is
    re-downloaded and updated.

    Args:
        network_uuid: NDEx UUID of the network to cache.
        agent: Owning agent name (rdaneel, drh, etc.).
        category: Network category override.
    """
    ndex = _get_ndex()
    if ndex is None:
        return {"status": "error", "message": "NDEx client not configured"}

    store = _get_store()

    # Download from NDEx
    dl_result = ndex.download_network(network_uuid)
    if dl_result["status"] != "success":
        return dl_result

    # Parse CX2
    cx2 = CX2Network()
    cx2.create_from_raw_cx2(dl_result["data"])

    # Import to local store
    stats = store.import_network(cx2, network_uuid, agent=agent, category=category)

    # Get NDEx modification timestamp
    summary = ndex.get_network_summary(network_uuid)
    if summary["status"] == "success":
        ndex_modified = str(summary["data"].get("modificationTime", ""))
        store.mark_published(network_uuid, ndex_modified=ndex_modified)

    return {
        "status": "success",
        "data": {
            "network_uuid": network_uuid,
            "node_count": stats["node_count"],
            "edge_count": stats["edge_count"],
            "name": (cx2.get_network_attributes() or {}).get("name", ""),
        },
    }


@mcp.tool()
def publish_network(network_uuid: str) -> dict:
    """Export a cached network and upload/update it on NDEx.

    If the network already exists on NDEx (UUID is a valid NDEx UUID),
    it is updated. Otherwise a new network is created.

    Args:
        network_uuid: UUID of the cached network to publish.
    """
    ndex = _get_ndex()
    if ndex is None:
        return {"status": "error", "message": "NDEx client not configured"}

    store = _get_store()
    entry = store.get_catalog_entry(network_uuid)
    if entry is None:
        return {"status": "error", "message": f"Network {network_uuid} not in cache"}

    # Export from graph
    cx2 = store.export_network(network_uuid)

    # Try update first (assumes UUID is from NDEx); fall back to create
    if entry.get("ndex_modified"):
        result = ndex.update_network(network_uuid, cx2)
    else:
        result = ndex.create_network(cx2)

    if result["status"] == "success":
        # Get new modification timestamp
        summary = ndex.get_network_summary(network_uuid)
        ndex_modified = ""
        if summary["status"] == "success":
            ndex_modified = str(summary["data"].get("modificationTime", ""))
        store.mark_published(network_uuid, ndex_modified=ndex_modified)

    return result


@mcp.tool()
def check_staleness(network_uuid: str) -> dict:
    """Check if a cached network is stale compared to NDEx.

    Args:
        network_uuid: UUID of the cached network.
    """
    ndex = _get_ndex()
    if ndex is None:
        return {"status": "error", "message": "NDEx client not configured"}

    store = _get_store()
    entry = store.get_catalog_entry(network_uuid)
    if entry is None:
        return {"status": "error", "message": f"Network {network_uuid} not in cache"}

    summary = ndex.get_network_summary(network_uuid)
    if summary["status"] != "success":
        return summary

    current_modified = str(summary["data"].get("modificationTime", ""))
    cached_modified = entry.get("ndex_modified", "")
    is_stale = current_modified != cached_modified

    return {
        "status": "success",
        "data": {
            "network_uuid": network_uuid,
            "is_stale": is_stale,
            "cached_modified": cached_modified,
            "ndex_modified": current_modified,
            "is_dirty": bool(entry.get("is_dirty")),
        },
    }


@mcp.tool()
def delete_cached_network(network_uuid: str) -> dict:
    """Remove a network from the local cache (does not affect NDEx).

    Args:
        network_uuid: UUID of the network to remove.
    """
    store = _get_store()
    entry = store.get_catalog_entry(network_uuid)
    if entry is None:
        return {"status": "error", "message": f"Network {network_uuid} not in cache"}
    store.delete_network(network_uuid)
    return {"status": "success", "message": f"Removed {network_uuid} from cache"}


# ── Entry point ──────────────────────────────────────────────────────


def main():
    global _store, _ndex
    parser = argparse.ArgumentParser(description="Local Store MCP Server")
    parser.add_argument(
        "--profile",
        default=None,
        help="NDEx profile from ~/.ndex/config.json for network sync.",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Cache directory (default: ~/.ndex/cache/).",
    )
    args = parser.parse_args()

    # Initialize local store
    _store = LocalStore(cache_dir=args.cache_dir)

    # Initialize NDEx client (optional — cache-only mode if no credentials)
    try:
        config = load_ndex_config(profile=args.profile)
        if has_credentials(config):
            _ndex = NDExClientWrapper(config)
            user = config.username
        else:
            user = "anonymous (cache-only)"
    except (ValueError, FileNotFoundError):
        user = "no config (cache-only)"

    print(
        f"Local Store MCP server started — user={user}, "
        f"cache={_store.cache_dir}",
        file=sys.stderr,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
