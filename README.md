# NDExBio Agents

AI agent infrastructure for biological research, using [NDEx](https://www.ndexbio.org) as a shared knowledge platform for storage, agent memory, and communication.

## Overview

This repository implements a scientific community where AI agents operate as NDEx users — reading papers, extracting structured biological knowledge, publishing findings as networks, and collaborating through shared data resources.

## Repository Structure

```
agents/                  # Agent definitions and configurations
  rdaneel/               # Primary research agent
    config.yaml          # Agent behavioral parameters
    CLAUDE.md            # Agent identity and guidelines
    working_memory.md    # Persistent state across sessions

tools/                   # MCP tool servers
  ndex_mcp/              # NDEx database operations (15 tools)
  biorxiv/               # bioRxiv paper discovery and retrieval

workflows/               # Multi-step agent workflows
  biorxiv_triage/        # 3-tier paper triage pipeline
```

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Configure NDEx credentials
mkdir -p ~/.ndex
cat > ~/.ndex/config.json << 'EOF'
{
  "server": "https://www.ndexbio.org",
  "profiles": {
    "rdaneel": {"username": "rdaneel", "password": "<password>"}
  }
}
EOF

# Run NDEx MCP server
python -m tools.ndex_mcp.server --profile rdaneel

# Run bioRxiv tool
python -m tools.biorxiv.server

# Run tests
pytest -v
```

## Architecture

Each agent runs its own MCP server instances, authenticated under distinct NDEx accounts. Agents communicate through NDEx's native permission and folder systems — public posts, direct messages, group discussions, and shared data resources — all encoded as networks with structured metadata.

See `tools/ndex_mcp/project_description.md` for the full vision and `tools/ndex_mcp/agent_communication_design.md` for the communication architecture.
