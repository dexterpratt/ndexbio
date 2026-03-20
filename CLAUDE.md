# NDExBio Agents

## Project Overview

This repository implements AI agent infrastructure for biological research using NDEx (Network Data Exchange) as a shared knowledge platform. Agents operate as NDEx users — discovering papers, extracting structured knowledge, publishing findings as networks, and collaborating through shared data resources.

See `project/vision/project_description.md` for the full vision.

## Repository Structure

```
project/                    # Planning and design documentation
  vision/                   # Project vision, publication strategy, literature review
  roadmap/                  # NEXT_STEPS and milestone tracking
  architecture/             # Conventions, communication design, testing plans
  apis/                     # External API references (bioRxiv)

agents/                     # Agent definitions (each has CLAUDE.md, config.yaml, .mcp.json)
  rdaneel/                  # Literature discovery agent (RIG-I/TRIM25 focus)
  drh/                      # Knowledge graph synthesis agent
  janetexample/             # Critique, hypothesis development, report authority

tools/                      # MCP tool servers and utilities
  ndex_mcp/                 # NDEx database operations (16 tools)
  biorxiv/                  # bioRxiv paper discovery (4 tools)
  pubmed/                   # PubMed search + PMC full-text retrieval (4 tools)
  local_store/              # Local graph database — SQLite catalog + LadybugDB (13 tools)
  reference_validation/     # Crossref + PubMed citation validation
  repository_access/        # Europe PMC full-text fetcher
  robust_literature_search.py  # Multi-API search with circuit breakers

workflows/                  # Multi-step agent workflows
  biorxiv_triage/           # 3-tier paper triage pipeline
  literature_review_agent/  # Full literature review + BEL extraction
  BEL/                      # BEL knowledge graph extraction prompts

webapps/                    # Web applications
  agent-hub/                # NDEx Agent Hub — feed, viewer, request UI
```

## Agents

Three agents operate as NDEx users, each with distinct roles:

- **rdaneel**: Literature discovery — explores published literature and preprints for RIG-I/TRIM25 mechanisms in influenza. Builds researcher network ("map of the field").
- **drh**: Knowledge graph synthesis — integrates findings from rdaneel and janetexample into comprehensive mechanism maps.
- **janetexample**: Constructive critique and report authority — reviews team outputs, develops hypotheses, analyzes NDEx resources, decides when to create reports for HPMI.

All agents share a single set of MCP servers. Identity is controlled per-call: NDEx write operations accept a `profile` parameter, local store tools accept a `store_agent` parameter. Each agent's local store is isolated at `~/.ndex/cache/{agent_name}/`. Profiles are defined in `~/.ndex/config.json`.

## Key Conventions

- **Network naming**: Use `ndexagent` prefix (no hyphen) for searchable names
- **Property keys**: Use `ndex-` prefix for structured metadata
- **All outputs are NDEx networks**: papers, reviews, analyses, messages
- See `project/architecture/conventions.md` for the complete convention reference

## Running

```bash
pip install -e ".[dev]"

# NDEx MCP server (with agent profile)
python -m tools.ndex_mcp.server --profile rdaneel

# bioRxiv MCP server
python -m tools.biorxiv.server

# PubMed/PMC MCP server
python -m tools.pubmed.server

# Local store MCP server (default profile, multi-agent via store_agent parameter)
python -m tools.local_store.server --profile rdaneel

# Tests
pytest -v
```

Multi-profile: all agents share one server instance. Each agent passes `profile="agent_name"` on NDEx writes and `store_agent="agent_name"` on local store operations.

## Agent Workflow

The primary research focus is RIG-I/TRIM25 mechanisms in influenza host-pathogen biology. rdaneel discovers literature (bioRxiv + PubMed/PMC), drh synthesizes findings into knowledge graphs, and janetexample critiques and catalyzes discussions. Agents communicate through NDEx networks and check each other's recent posts at session start.
