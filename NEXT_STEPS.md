# NDExBio Agents — Next Steps

Written: 2026-03-12, end of initial setup session.

## What Was Accomplished

1. **Repo setup**: Copied `agents/` and `tools/ndex_mcp/` from critique_agent to ndexbio. Fixed imports for standalone use.
2. **bioRxiv tool**: Created `tools/biorxiv/` MCP server (client.py + server.py, 4 tools).
3. **3-tier triage workflow**: Created `workflows/biorxiv_triage/` with tier1_scan.py, tier2_review.py, tier3_analysis.py.
4. **Agent rdaneel configured**: Updated config.yaml with HPMI focus, keyword groups, per-tier model preferences.
5. **MCP servers running locally**: Both ndex and biorxiv MCP servers configured in Claude Desktop, using a Python 3.12 venv with PYTHONPATH set.
6. **Scheduled task**: `rdaneel-biorxiv-triage` runs every 4 hours via Cowork scheduled tasks.
7. **Permissions**: `~/.claude/settings.json` created with `mcp__ndex__*` and `mcp__biorxiv__*` auto-approved.
8. **NDEx credentials**: `~/.ndex/config.json` in multi-profile format, profile `rdaneel`.
9. **Backlog published**: 17 networks from scans a-g published to NDEx and set PUBLIC.
10. **Scan h successful**: First fully MCP-based triage run completed. 6 new networks published (1 daily scan, 3 tier2 reviews, 1 tier3 analysis, 1 highlight).
11. **Deployment cookbook**: `NDExBio_Agents_Deployment_Cookbook.docx` created in repo root.

## Immediate Next Steps

### 1. Integrate literature search tools from critique_agent
- Check `critique_agent/tools/` for any existing literature search implementations beyond what's in ndexbio
- Specifically look for: Europe PMC client, Semantic Scholar client, PubMed/Entrez tools
- These would serve as fallbacks for full-text retrieval (see issue #3 below)

### 2. bioRxiv full-text access issue
- Cloudflare protection blocks JATS XML and HTML full-text downloads from www.biorxiv.org
- The metadata API (api.biorxiv.org) works fine
- **Recommended fix**: Add Europe PMC as a fallback full-text source in `tools/biorxiv/client.py`
- Alternative: bioRxiv S3 bucket (`s3://biorxiv-src-monthly`) for bulk access (requires AWS account)
- The `jatsxml` URLs returned by the API are valid but Cloudflare-protected

### 3. Safety classifier issue
- Agent was blocked mid-run when synthesizing findings about respiratory virus mechanisms
- Reframed task prompt to use "biomedical literature curation" / "knowledge graph construction" language
- Scan h succeeded with the reframed prompt, but the issue may recur
- If it does: pivot to cancer signaling pathways as the curation focus (collaborators work in that field)
- Document the issue for Anthropic feedback

### 4. Refactor tier1_scan.py to load keywords from config
- Currently keywords are hardcoded in tier1_scan.py AND in agents/rdaneel/config.yaml
- Should load from config.yaml at runtime so it's a single source of truth
- Deferred until after initial testing period

### 5. Working memory cleanup
- working_memory.md has grown large with scan logs from a-g (pre-MCP era)
- Consider archiving old scan logs to a separate file
- Keep only the published networks table and most recent 2-3 scan logs in working memory

### 6. Network quality review
- Review the 23 published networks on NDEx (https://www.ndexbio.org, search for user rdaneel)
- Check that interaction networks have correct node/edge structure
- Verify properties and metadata are searchable
- Consider adding visual styles (CX2 visual properties) for better display in NDEx

## Key File Locations

| What | Where |
|------|-------|
| Repo | ~/Documents/agents/GitHub/ndexbio |
| Critique agent repo | ~/Documents/agents/GitHub/critique_agent |
| Claude Desktop config | ~/Library/Application Support/Claude/claude_desktop_config.json |
| NDEx credentials | ~/.ndex/config.json |
| MCP permissions | ~/.claude/settings.json |
| Scheduled task | ~/Documents/Claude/Scheduled/rdaneel-biorxiv-triage/ |
| Python venv | ~/Documents/agents/GitHub/ndexbio/.venv/ |

## Key Configuration (for reference in new sessions)

**Claude Desktop config** needs these MCP servers:
```json
{
  "mcpServers": {
    "ndex": {
      "command": "/path/to/ndexbio/.venv/bin/python3",
      "args": ["-m", "tools.ndex_mcp.server", "--profile", "rdaneel"],
      "cwd": "/path/to/ndexbio",
      "env": { "PYTHONPATH": "/path/to/ndexbio" }
    },
    "biorxiv": {
      "command": "/path/to/ndexbio/.venv/bin/python3",
      "args": ["-m", "tools.biorxiv.server"],
      "cwd": "/path/to/ndexbio",
      "env": { "PYTHONPATH": "/path/to/ndexbio" }
    }
  }
}
```

**Scheduled task** (`rdaneel-biorxiv-triage`): Runs every 4 hours. Uses MCP tools for all API calls. Task prompt is in the Cowork scheduled tasks system.
