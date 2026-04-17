"""
NDExBio Trial Analysis - Data Extraction

Pulls all agent-published networks from NDEx and builds a structured
dataset for analysis. Uses ndex2 directly (no MCP required).

Output: a JSON file with all network metadata, properties, and
interaction links ready for metrics computation.
"""

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ndex2.client

from .config import AGENTS, NDEX_SERVER, SELF_KNOWLEDGE_SUFFIXES, TRIAL

# Regex for NDEx UUIDs embedded in text
UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _ts_to_iso(epoch_ms: int | None) -> str | None:
    """Convert NDEx epoch-millisecond timestamp to ISO string."""
    if epoch_ms is None:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


def connect(
    server: str = NDEX_SERVER,
    username: str | None = None,
    password: str | None = None,
) -> ndex2.client.Ndex2:
    """Connect to NDEx. Authenticates if credentials are provided."""
    if username and password:
        return ndex2.client.Ndex2(
            server, username, password, skip_version_check=True
        )
    return ndex2.client.Ndex2(server, skip_version_check=True)


def fetch_agent_network_summaries(
    client: ndex2.client.Ndex2,
    username: str,
    limit: int = 500,
) -> list[dict]:
    """Fetch all network summaries for one agent account.

    Tries get_user_network_summaries first (works on public NDEx).
    Falls back to search if that fails (works on local servers where
    listing another user's networks requires admin access).
    """
    # Try direct user listing first
    try:
        summaries = []
        offset = 0
        batch_size = min(limit, 100)
        while offset < limit:
            batch = client.get_user_network_summaries(
                username, offset=offset, limit=batch_size
            )
            if not batch:
                break
            summaries.extend(batch)
            offset += len(batch)
            if len(batch) < batch_size:
                break
            time.sleep(0.2)
        return summaries
    except Exception:
        pass

    # Fallback: search for networks by agent name
    summaries = []
    offset = 0
    batch_size = min(limit, 100)
    while offset < limit:
        results = client.search_networks(
            search_string=f"ndexagent {username}",
            account_name=username,
            start=offset,
            size=batch_size,
        )
        batch = results.get("networks", [])
        if not batch:
            break
        summaries.extend(batch)
        offset += len(batch)
        if len(batch) < batch_size:
            break
        time.sleep(0.2)
    return summaries


def fetch_network_cx2(
    client: ndex2.client.Ndex2,
    network_id: str,
) -> list[dict] | None:
    """Download the full CX2 for a network. Returns the CX2 aspect list."""
    try:
        resp = client.get_network_as_cx2_stream(network_id)
        return resp.json()
    except Exception as e:
        print(f"  WARNING: Could not download CX2 for {network_id}: {e}", file=sys.stderr)
        return None


def parse_network_properties(cx2: list[dict]) -> dict[str, Any]:
    """Extract network-level properties from CX2 aspect list."""
    props = {}
    for aspect in cx2:
        if isinstance(aspect, dict):
            # networkAttributes aspect
            if "networkAttributes" in aspect:
                for attr in aspect["networkAttributes"]:
                    if isinstance(attr, dict):
                        props.update(attr)
                    elif isinstance(attr, list) and len(attr) >= 2:
                        props[attr[0]] = attr[1]
            # Also check for top-level attributeDeclarations, etc.
    return props


def parse_schema_info(cx2: list[dict]) -> dict:
    """Extract schema diversity information from CX2."""
    node_types = set()
    edge_types = set()
    node_property_keys = set()
    edge_property_keys = set()
    network_property_keys = set()
    node_count = 0
    edge_count = 0

    for aspect in cx2:
        if not isinstance(aspect, dict):
            continue

        if "nodes" in aspect:
            for node in aspect["nodes"]:
                node_count += 1
                v = node.get("v", {})
                node_property_keys.update(v.keys())
                if "type" in v:
                    node_types.add(str(v["type"]).lower())
                if "node_type" in v:
                    node_types.add(str(v["node_type"]).lower())

        if "edges" in aspect:
            for edge in aspect["edges"]:
                edge_count += 1
                v = edge.get("v", {})
                edge_property_keys.update(v.keys())
                if "interaction" in v:
                    edge_types.add(str(v["interaction"]).lower())

        if "networkAttributes" in aspect:
            for attr in aspect["networkAttributes"]:
                if isinstance(attr, dict):
                    network_property_keys.update(attr.keys())

    return {
        "node_types": sorted(node_types),
        "edge_types": sorted(edge_types),
        "node_property_keys": sorted(node_property_keys),
        "edge_property_keys": sorted(edge_property_keys),
        "network_property_keys": sorted(network_property_keys),
        "node_count": node_count,
        "edge_count": edge_count,
    }


def find_uuid_references(cx2: list[dict], own_uuid: str) -> list[str]:
    """Find all NDEx UUIDs referenced anywhere in the CX2, excluding self."""
    text = json.dumps(cx2)
    found = set(UUID_PATTERN.findall(text))
    found.discard(own_uuid)
    return sorted(found)


def classify_network(name: str, properties: dict, username: str) -> dict:
    """Classify a network by type, whether it's self-knowledge, etc."""
    name_lower = name.lower() if name else ""

    # Check if this is a self-knowledge network
    is_self_knowledge = False
    self_knowledge_type = None
    for suffix in SELF_KNOWLEDGE_SUFFIXES:
        if suffix in name_lower:
            is_self_knowledge = True
            self_knowledge_type = suffix
            break

    # Message type from annotation
    message_type = properties.get("ndex-message-type", "unknown")
    workflow = properties.get("ndex-workflow", "unknown")
    data_type = properties.get("ndex-data-type", "")

    return {
        "message_type": message_type,
        "workflow": workflow,
        "data_type": data_type,
        "is_self_knowledge": is_self_knowledge,
        "self_knowledge_type": self_knowledge_type,
    }


def extract_network_record(
    client: ndex2.client.Ndex2,
    summary: dict,
    username: str,
    download_cx2: bool = True,
) -> dict:
    """Build a complete record for one network."""
    uuid = summary.get("externalId", "")
    name = summary.get("name", "")

    record = {
        "uuid": uuid,
        "name": name,
        "owner": summary.get("owner", username),
        "agent_username": username,
        "creation_time": _ts_to_iso(summary.get("creationTime")),
        "modification_time": _ts_to_iso(summary.get("modificationTime")),
        "creation_epoch_ms": summary.get("creationTime"),
        "modification_epoch_ms": summary.get("modificationTime"),
        "node_count": summary.get("nodeCount", 0),
        "edge_count": summary.get("edgeCount", 0),
        "visibility": summary.get("visibility", "UNKNOWN"),
        "description": summary.get("description", ""),
    }

    # Extract properties and schema from CX2
    if download_cx2:
        cx2 = fetch_network_cx2(client, uuid)
        if cx2:
            props = parse_network_properties(cx2)
            schema = parse_schema_info(cx2)
            uuid_refs = find_uuid_references(cx2, uuid)
        else:
            props = {}
            schema = {
                "node_types": [], "edge_types": [],
                "node_property_keys": [], "edge_property_keys": [],
                "network_property_keys": [], "node_count": 0, "edge_count": 0,
            }
            uuid_refs = []
    else:
        props = {}
        schema = None
        uuid_refs = []

    # Network-level annotation properties
    record["properties"] = props
    record["ndex_agent"] = props.get("ndex-agent", "")
    record["ndex_message_type"] = props.get("ndex-message-type", "")
    record["ndex_workflow"] = props.get("ndex-workflow", "")
    record["ndex_reply_to"] = props.get("ndex-reply-to", "")
    record["ndex_data_type"] = props.get("ndex-data-type", "")

    # Schema info
    record["schema"] = schema

    # UUID references found in content
    record["uuid_references"] = uuid_refs

    # Classification
    classification = classify_network(name, props, username)
    record.update(classification)

    return record


def _load_credentials(server: str) -> tuple[str | None, str | None]:
    """Try to load credentials for the given server from ~/.ndex/config.json."""
    config_path = Path.home() / ".ndex" / "config.json"
    try:
        data = json.loads(config_path.read_text())
        profiles = data.get("profiles", {})
        # Find first profile whose server matches
        for name, p in profiles.items():
            profile_server = p.get("server", data.get("server", ""))
            if profile_server == server:
                return p.get("username"), p.get("password")
        return None, None
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None


def _load_agent_credentials(server: str, agent_username: str) -> tuple[str | None, str | None]:
    """Load credentials for a specific agent from ~/.ndex/config.json.

    Looks for a profile whose server matches and whose username matches
    the agent. Tries 'local-<username>' first (convention for local server
    profiles), then any profile matching both server and username.
    """
    config_path = Path.home() / ".ndex" / "config.json"
    try:
        data = json.loads(config_path.read_text())
        profiles = data.get("profiles", {})
        # Try 'local-<username>' first
        local_key = f"local-{agent_username}"
        if local_key in profiles:
            p = profiles[local_key]
            profile_server = p.get("server", data.get("server", ""))
            if profile_server == server:
                return p.get("username"), p.get("password")
        # Fallback: any profile matching server + username
        for name, p in profiles.items():
            profile_server = p.get("server", data.get("server", ""))
            if profile_server == server and p.get("username") == agent_username:
                return p.get("username"), p.get("password")
        return None, None
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None


def extract_all(
    download_cx2: bool = True,
    output_path: str | None = None,
) -> dict:
    """
    Main extraction: pull all agent networks from NDEx, build dataset.

    Authenticates per-agent when possible, so each agent can list its
    own networks via get_user_network_summaries. Falls back to anonymous
    search for agents without credentials.

    Args:
        download_cx2: If True, download full CX2 for schema and reference
                      analysis. Slower but needed for full metrics.
        output_path:  If set, write JSON to this path.

    Returns:
        Complete dataset dict.
    """
    # Default client for CX2 downloads and fallback
    default_user, default_pass = _load_credentials(NDEX_SERVER)
    default_client = connect(NDEX_SERVER, default_user, default_pass)
    auth_status = "authenticated" if default_user else "anonymous"
    print(f"Connected to {NDEX_SERVER} ({auth_status})")

    all_networks = []
    uuid_to_owner = {}  # for resolving cross-references

    for username, agent_def in AGENTS.items():
        print(f"\nFetching networks for {agent_def.display_name} ({username})...")
        # Authenticate as this agent if credentials are available
        agent_user, agent_pass = _load_agent_credentials(NDEX_SERVER, username)
        if agent_user:
            agent_client = connect(NDEX_SERVER, agent_user, agent_pass)
            print(f"  Authenticated as {agent_user}")
        else:
            agent_client = default_client
            print(f"  Using default client (no agent-specific credentials)")
        summaries = fetch_agent_network_summaries(agent_client, username)
        print(f"  Found {len(summaries)} networks")

        # Use default_client for CX2 downloads (any authenticated client works)
        for i, summary in enumerate(summaries):
            if (i + 1) % 10 == 0:
                print(f"  Processing {i + 1}/{len(summaries)}...")
            record = extract_network_record(
                default_client, summary, username, download_cx2=download_cx2
            )
            all_networks.append(record)
            uuid_to_owner[record["uuid"]] = username

    # Resolve UUID references to owning agents
    print(f"\nResolving cross-references across {len(all_networks)} networks...")
    for record in all_networks:
        resolved_refs = []
        for ref_uuid in record.get("uuid_references", []):
            ref_owner = uuid_to_owner.get(ref_uuid)
            resolved_refs.append({
                "uuid": ref_uuid,
                "owner": ref_owner,  # None if not in our dataset
                "is_cross_agent": (
                    ref_owner is not None and ref_owner != record["agent_username"]
                ),
            })
        record["resolved_references"] = resolved_refs

        # Also resolve ndex-reply-to specifically
        reply_to = record.get("ndex_reply_to", "")
        if reply_to and reply_to in uuid_to_owner:
            record["reply_to_agent"] = uuid_to_owner[reply_to]
        else:
            record["reply_to_agent"] = None

    # Build dataset
    dataset = {
        "extraction_time": datetime.now(timezone.utc).isoformat(),
        "trial_id": TRIAL.trial_id,
        "observation_start": TRIAL.observation_start,
        "observation_end": TRIAL.observation_end,
        "ndex_server": NDEX_SERVER,
        "agents": {
            k: {
                "username": v.username,
                "display_name": v.display_name,
                "role": v.role,
                "role_category": v.role_category,
                "team": v.team,
                "team_label": v.team_label,
            }
            for k, v in AGENTS.items()
        },
        "network_count": len(all_networks),
        "networks": all_networks,
        "uuid_to_owner": uuid_to_owner,
    }

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(dataset, f, indent=2, default=str)
        print(f"\nDataset written to {out} ({len(all_networks)} networks)")

    return dataset


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output = Path(TRIAL.output_dir) / f"extracted_{TRIAL.trial_id}.json"
    extract_all(download_cx2=True, output_path=str(output))
