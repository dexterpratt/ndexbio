#!/usr/bin/env python3
"""One-time catchup script: publish all backlogged network specs to NDEx.

Run from the ndexbio repo root on a machine with:
  - Network access to www.ndexbio.org
  - Credentials in ~/.ndex/config.json (profile: rdaneel)

Usage:
    cd ~/Documents/agents/GitHub/ndexbio
    python scripts/publish_backlog.py [--dry-run]
    python scripts/publish_backlog.py --visibility-only  # just set PUBLIC on already-published
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.ndex_mcp.config import load_ndex_config, has_credentials
from tools.ndex_mcp.ndex_client_wrapper import NDExClientWrapper
from tools.ndex_mcp.network_builder import spec_to_cx2

RDANEEL_DIR = Path(__file__).resolve().parent.parent / "agents" / "rdaneel"

# All network spec files to publish, in chronological order
NETWORK_SPEC_FILES = [
    # 2026-03-10: Tier 1 + 3 Tier 2 reviews + 3 Tier 3 analyses + 3 highlights
    "scan_2026-03-10/tier1_network_spec.json",
    "scan_2026-03-10/tier2_network_1.json",
    "scan_2026-03-10/tier2_network_2.json",
    "scan_2026-03-10/tier2_network_3.json",
    "scan_2026-03-10/tier3_analysis_network_1.json",
    "scan_2026-03-10/tier3_analysis_network_2.json",
    "scan_2026-03-10/tier3_analysis_network_3.json",
    "scan_2026-03-10/tier3_highlight_network_1.json",
    "scan_2026-03-10/tier3_highlight_network_2.json",
    "scan_2026-03-10/tier3_highlight_network_3.json",
    # 2026-03-11 first scan: Tier 1 + 1 Tier 2 + 1 Tier 3 + 1 highlight
    "scan_2026-03-11/tier1_network_spec.json",
    "scan_2026-03-11/tier2_network_1.json",
    "scan_2026-03-11/tier3_analysis_network_1.json",
    "scan_2026-03-11/tier3_highlight_network_1.json",
    # 2026-03-11_b supplementary: Tier 1 + 1 Tier 2
    "scan_2026-03-11_b/tier1_network_spec.json",
    "scan_2026-03-11_b/tier2_network_1.json",
    # 2026-03-11_c through 2026-03-11_e: Tier 1 only (no new high-scoring papers)
    "scan_2026-03-11_c/tier1_network_spec.json",
    "scan_2026-03-11_d/tier1_network_spec.json",
    "scan_2026-03-11_e/tier1_network_spec.json",
]

# UUIDs from the first (partially successful) run — networks created but visibility not set
ALREADY_PUBLISHED = {
    "scan_2026-03-10/tier1_network_spec.json": "ba963865-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier2_network_1.json": "bab02907-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier2_network_2.json": "bac314c9-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier2_network_3.json": "baddc8bb-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_analysis_network_1.json": "baf8077d-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_analysis_network_2.json": "bb104a6f-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_analysis_network_3.json": "bb23ab61-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_highlight_network_1.json": "bb39f283-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_highlight_network_2.json": "bb520e65-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-10/tier3_highlight_network_3.json": "bb698e07-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11/tier1_network_spec.json": "bb7dd959-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11/tier2_network_1.json": "bb983f2b-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11_b/tier1_network_spec.json": "bbaf70ad-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11_b/tier2_network_1.json": "bbc8c50f-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11_c/tier1_network_spec.json": "bbda2a31-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11_d/tier1_network_spec.json": "bbf3a5a3-1e2b-11f1-94e8-005056ae3c32",
    "scan_2026-03-11_e/tier1_network_spec.json": "bc061c35-1e2b-11f1-94e8-005056ae3c32",
}


def normalize_spec(spec: dict) -> dict:
    """Normalize network specs that use metadata-wrapped format.

    Some specs use {"metadata": {"name": ..., "description": ..., "properties": ...}, "nodes": [...], "edges": [...]}
    instead of the flat {"name": ..., "description": ..., "properties": ..., "nodes": [...], "edges": [...]}.
    This function normalizes to the flat format expected by spec_to_cx2.
    """
    if "name" not in spec and "metadata" in spec:
        md = spec["metadata"]
        return {
            "name": md.get("name", ""),
            "description": md.get("description", ""),
            "version": md.get("version", "1.0"),
            "properties": md.get("properties", {}),
            "nodes": spec.get("nodes", []),
            "edges": spec.get("edges", []),
        }
    return spec


def main():
    dry_run = "--dry-run" in sys.argv
    visibility_only = "--visibility-only" in sys.argv

    # Load credentials
    config = load_ndex_config(profile="rdaneel")
    if not has_credentials(config):
        print("ERROR: No valid credentials found for profile 'rdaneel'.")
        print("       Check ~/.ndex/config.json")
        sys.exit(1)

    print(f"NDEx server: {config.server}")
    print(f"Username:    {config.username}")
    print(f"Dry run:     {dry_run}")
    print(f"Mode:        {'visibility-only' if visibility_only else 'full publish'}")
    print()

    # Connect
    wrapper = NDExClientWrapper(config)
    status = wrapper.get_connection_status()
    print(f"Connection:  {status}")
    print()

    results = []

    if visibility_only:
        # Just set visibility on already-published networks
        print(f"Setting visibility on {len(ALREADY_PUBLISHED)} already-published networks...\n")
        for spec_file, uuid in ALREADY_PUBLISHED.items():
            print(f"  {spec_file} -> {uuid}")
            if dry_run:
                print("    [DRY RUN] would set PUBLIC")
                continue
            vis_result = wrapper.set_network_visibility(uuid, "PUBLIC")
            if vis_result["status"] == "success":
                print("    PUBLIC OK")
                results.append({"file": spec_file, "uuid": uuid, "status": "published"})
            else:
                print(f"    ERROR: {vis_result.get('message')}")
                results.append({"file": spec_file, "uuid": uuid, "status": "error", "message": vis_result.get("message")})
        # Now publish the 2 that failed (missing name)
        print(f"\nPublishing 2 remaining networks with metadata format...\n")
        for spec_path_rel in NETWORK_SPEC_FILES:
            if spec_path_rel in ALREADY_PUBLISHED:
                continue
            _publish_one(wrapper, spec_path_rel, dry_run, results)
    else:
        # Full publish — skip already published
        for spec_path_rel in NETWORK_SPEC_FILES:
            if spec_path_rel in ALREADY_PUBLISHED:
                uuid = ALREADY_PUBLISHED[spec_path_rel]
                print(f"SKIP (already published): {spec_path_rel} -> {uuid}")
                results.append({"file": spec_path_rel, "uuid": uuid, "status": "already_published"})
                continue
            _publish_one(wrapper, spec_path_rel, dry_run, results)

    _print_summary(results)


def _publish_one(wrapper, spec_path_rel, dry_run, results):
    spec_path = RDANEEL_DIR / spec_path_rel
    if not spec_path.exists():
        print(f"SKIP (not found): {spec_path_rel}")
        results.append({"file": spec_path_rel, "status": "not_found"})
        return

    with open(spec_path) as f:
        spec = json.load(f)

    # Normalize metadata-wrapped format
    spec = normalize_spec(spec)

    name = spec.get("name", "unnamed")
    n_nodes = len(spec.get("nodes", []))
    n_edges = len(spec.get("edges", []))
    tier = spec.get("properties", {}).get("ndex-triage-tier", "?")

    print(f"Publishing: {name}")
    print(f"  Tier {tier} | {n_nodes} nodes, {n_edges} edges")

    if dry_run:
        print("  [DRY RUN] would publish")
        results.append({"file": spec_path_rel, "name": name, "status": "dry_run"})
        return

    try:
        cx2_network = spec_to_cx2(spec)
        result = wrapper.create_network(cx2_network)
        if result["status"] == "success":
            uuid = result["data"]
            print(f"  SUCCESS: {uuid}")

            vis_result = wrapper.set_network_visibility(uuid, "PUBLIC")
            if vis_result["status"] == "success":
                print(f"  Visibility set to PUBLIC")
            else:
                print(f"  Warning: visibility not set: {vis_result.get('message')}")

            results.append({
                "file": spec_path_rel,
                "name": name,
                "uuid": uuid,
                "status": "published",
            })
        else:
            print(f"  ERROR: {result.get('message')}")
            results.append({
                "file": spec_path_rel,
                "name": name,
                "status": "error",
                "message": result.get("message"),
            })
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        results.append({
            "file": spec_path_rel,
            "name": name,
            "status": "exception",
            "message": str(e),
        })


def _print_summary(results):
    print("\n" + "=" * 60)
    published = [r for r in results if r["status"] in ("published", "already_published")]
    errors = [r for r in results if r["status"] in ("error", "exception")]
    print(f"Published: {len(published)} / {len(results)}")
    if errors:
        print(f"Errors:    {len(errors)}")
        for e in errors:
            print(f"  - {e['file']}: {e.get('message')}")

    log_path = RDANEEL_DIR / f"publish_backlog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {log_path}")

    uuids = [r for r in results if "uuid" in r]
    if uuids:
        print("\n--- UUIDs for working_memory.md ---")
        for r in uuids:
            name = r.get("name", r["file"])[:50]
            print(f"| {name} | {r['uuid']} | {r['file'].split('/')[0].replace('scan_','')} |")


if __name__ == "__main__":
    main()
