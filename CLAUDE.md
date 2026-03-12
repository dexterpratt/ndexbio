# NDExBio Agents

## Project Overview

This repository implements AI agent infrastructure for biological research using NDEx (Network Data Exchange) as a shared knowledge platform. Agents operate as NDEx users — discovering papers, extracting structured knowledge, publishing findings as networks, and collaborating through shared data resources.

See `tools/ndex_mcp/project_description.md` for the full vision.

## Repository Structure

```
agents/                     # Agent definitions
  rdaneel/                  # Primary research agent
    config.yaml             # Behavioral parameters and triage config
    CLAUDE.md               # Agent identity and guidelines
    working_memory.md       # Persistent state across sessions

tools/                      # MCP tool servers
  ndex_mcp/                 # NDEx database operations (15 tools)
  biorxiv/                  # bioRxiv paper discovery (4 tools)

workflows/                  # Multi-step agent workflows
  biorxiv_triage/           # 3-tier paper triage pipeline
    tier1_scan.py           # High-volume keyword scan
    tier2_review.py         # Focused full-text review
    tier3_analysis.py       # Deep analysis with literature context
```

## Key Conventions

- **Network naming**: Use `ndexagent` prefix (no hyphen) for searchable names
- **Property keys**: Use `ndex-` prefix for structured metadata
- **All outputs are NDEx networks**: papers, reviews, analyses, messages
- See `tools/ndex_mcp/conventions.md` for the complete convention reference

## Running

```bash
pip install -e ".[dev]"

# NDEx MCP server (with agent profile)
python -m tools.ndex_mcp.server --profile rdaneel

# bioRxiv MCP server
python -m tools.biorxiv.server

# Tests
pytest -v
```

## Agent Workflow

The primary workflow is the bioRxiv triage pipeline described in `workflows/biorxiv_triage/README.md`. Agent rdaneel periodically scans bioRxiv for papers relevant to host-pathogen molecular interactions (currently focused on influenza), triages them through three levels of increasing depth, and publishes findings to NDEx.
