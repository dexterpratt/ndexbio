"""
NDExBio Trial Analysis - Main Runner

Executes the full pipeline:
  1. Extract all agent networks from NDEx
  2. Compute metrics
  3. Generate matplotlib figures
  4. Draft the Observations section and supplementary materials

Cytoscape figures (interaction graph, thread narrative) are NOT
generated here. They require interactive use of the Cytoscape MCP
by the analyst agent. See cytoscape_workflow.md.

Usage:
    cd ndexbio/paper
    python -m analysis.run_analysis [--trial-id TRIAL_001] [--output-dir output]

    # Or skip extraction if you already have data:
    python -m analysis.run_analysis --from-extracted output/extracted_trial_001.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(
    trial_id: str = "trial_001",
    output_dir: str = "output",
    from_extracted: str | None = None,
    skip_cx2: bool = False,
):
    """Run the full analysis pipeline."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig_dir = out / "figures"
    fig_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ---------------------------------------------------------------
    # Step 1: Extract
    # ---------------------------------------------------------------
    if from_extracted:
        print(f"\n{'='*60}")
        print(f"Loading pre-extracted data from {from_extracted}")
        print(f"{'='*60}")
        with open(from_extracted) as f:
            dataset = json.load(f)
    else:
        print(f"\n{'='*60}")
        print(f"STEP 1: Extracting data from NDEx")
        print(f"{'='*60}")
        from .extract import extract_all
        from .config import TRIAL
        TRIAL.trial_id = trial_id

        dataset_path = out / f"extracted_{trial_id}_{timestamp}.json"
        dataset = extract_all(
            download_cx2=not skip_cx2,
            output_path=str(dataset_path),
        )

    n_networks = len(dataset.get("networks", []))
    n_agents = len(dataset.get("agents", {}))
    print(f"\nExtracted {n_networks} networks from {n_agents} agents")

    if n_networks == 0:
        print("\nWARNING: No networks found. Check that agents have published to NDEx.")
        print("The pipeline will continue but all metrics will be empty.")

    # ---------------------------------------------------------------
    # Step 2: Compute metrics
    # ---------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"STEP 2: Computing metrics")
    print(f"{'='*60}")
    from .metrics import compute_all

    metrics = compute_all(dataset)

    metrics_path = out / f"metrics_{trial_id}_{timestamp}.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"Metrics written to {metrics_path}")

    # Print key stats
    activity = metrics.get("activity", {})
    interactions = metrics.get("interactions", {})
    print(f"\n  Total networks: {activity.get('total_networks', 0)}")
    print(f"  Content networks: {activity.get('total_content_networks', 0)}")
    print(f"  Cross-agent references: {interactions.get('total_cross_references', 0)}")
    print(f"  Reply interactions: {interactions.get('total_reply_interactions', 0)}")
    print(f"  Cross-team replies: {interactions.get('cross_team_replies', 0)}")
    print(f"  Max thread depth: {interactions.get('max_thread_depth', 0)}")
    print(f"  Cross-team chains: {interactions.get('cross_team_chains', 0)}")

    schema = metrics.get("schema_diversity", {}).get("global", {})
    print(f"  Unique node types: {schema.get('total_node_types', 0)}")
    print(f"  Unique edge types: {schema.get('total_edge_types', 0)}")
    print(f"  Unique property keys: {schema.get('total_property_keys', 0)}")

    # ---------------------------------------------------------------
    # Step 3: Generate figures
    # ---------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"STEP 3: Generating figures")
    print(f"{'='*60}")
    from .figures import generate_all as generate_figures

    figure_paths = generate_figures(metrics, str(fig_dir))
    print(f"\nGenerated {len(figure_paths)} figures")

    # ---------------------------------------------------------------
    # Step 4: Draft report
    # ---------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"STEP 4: Drafting Observations section")
    print(f"{'='*60}")
    from .report import generate_observations_section

    report = generate_observations_section(metrics, dataset, str(out))

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"\nOutputs in {out}/:")
    print(f"  Data:    extracted_*.json, metrics_*.json")
    print(f"  Figures: figures/*.png")
    print(f"  Report:  observations_draft.md")
    print(f"  Suppl:   supplementary_draft.md")
    print(f"\nNEXT STEPS FOR ANALYST AGENT:")
    print(f"  1. Review observations_draft.md — fill in [AGENT: ...] placeholders")
    print(f"  2. Follow cytoscape_workflow.md to create:")
    print(f"     - Interaction graph figure (Figure A)")
    print(f"     - Thread narrative diagram (Figure B — hero figure candidate)")
    print(f"  3. Review all figures for publication quality")
    print(f"  4. Select best anecdotes for narrative sections")

    return {
        "dataset_path": str(dataset_path) if not from_extracted else from_extracted,
        "metrics_path": str(metrics_path),
        "figure_paths": figure_paths,
        "observations_path": str(out / "observations_draft.md"),
        "supplementary_path": str(out / "supplementary_draft.md"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="NDExBio Trial Analysis Pipeline"
    )
    parser.add_argument(
        "--trial-id", default="trial_001",
        help="Identifier for this trial run (default: trial_001)"
    )
    parser.add_argument(
        "--output-dir", default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--from-extracted", default=None,
        help="Skip extraction; load from this JSON file instead"
    )
    parser.add_argument(
        "--skip-cx2", action="store_true",
        help="Skip downloading CX2 (faster but no schema/reference analysis)"
    )
    args = parser.parse_args()

    run(
        trial_id=args.trial_id,
        output_dir=args.output_dir,
        from_extracted=args.from_extracted,
        skip_cx2=args.skip_cx2,
    )


if __name__ == "__main__":
    main()
