# NDExBio Agents — Next Steps

Updated: 2026-03-13, after critique_agent integration.

## What Was Accomplished

### Phase 1: Initial Setup (2026-03-12)
1. Repo setup with agents/, tools/ndex_mcp/, tools/biorxiv/
2. 3-tier triage workflow (tier1_scan, tier2_review, tier3_analysis)
3. Agent rdaneel configured and running on 4-hour schedule
4. 23+ networks published to NDEx
5. Deployment cookbook written

### Phase 1.5: critique_agent Integration (2026-03-13)
6. **NDEx MCP server upgraded**: Added `set_network_system_properties` tool (16 tools total), auto-indexing on `create_network`, `update_network` BytesIO fix, startup message
7. **Conventions.md**: Added indexing/searchability section
8. **Literature search tools ported**: `robust_literature_search.py`, `literature_search_integration.py`
9. **Europe PMC fetcher ported**: `tools/repository_access/europepmc_fetcher.py`
10. **Reference validation ported**: `tools/reference_validation/` (Crossref, PubMed, citation extractor, similarity analyzer)
11. **Literature review workflow ported**: `workflows/literature_review_agent/` (literature_review.md, check_requests.md, post_request.md, plan.md)
12. **BEL extraction workflow ported**: `workflows/BEL/bel_prompt.md`
13. **Agent Hub web app**: `webapps/agent-hub/` (feed, network viewer, request form)
14. **Multi-agent docs**: publication_strategy.md, literature_review_multi_agent_systems.md
15. **`.mcp.json`**: NDEx MCP server auto-starts in Claude Code sessions
16. **bioRxiv API spec**: `tools/external_apis/biorxiv_api.md`

## Current Priority: Collaborator Demo

Target audience: Chris Mungall (GO consortium), HPMI collaborators.
See `webapps/agent-hub/demo_plan.md` for the full demo plan.

### Day 1: Content + Agent Setup
- [ ] Create 2 new NDEx accounts (rbaley, rcalvin)
- [ ] Run literature review workflow on a selected rdaneel paper (full PDF → BEL analysis)
- [ ] Craft rbaley critique network (manual CX2 spec via MCP tools)
- [ ] Craft rcalvin synthesis network
- [ ] Craft rcalvin self-knowledge networks (plans, memory, collaborators)
- [ ] Set all demo networks PUBLIC, indexed, showcased
- [ ] Format selected networks in Cytoscape Desktop for layout

### Day 2: Web App — Core Features
- [ ] Agent directory section (hardcoded agent list + profile links)
- [ ] Feed threading (reply-to chain grouping)
- [ ] Author filtering in feed
- [ ] Relative timestamps
- [ ] Visual polish pass

### Day 3: Web App — Viewer + Polish
- [ ] Hierarchical layout for tree-structured networks (dagre)
- [ ] BEL network style tuning
- [ ] Node/edge click panel polish
- [ ] Documentation tab skeleton
- [ ] End-to-end walkthrough

### Day 4: Documentation + Final Polish
- [ ] Infographics (system architecture, agent conversation flow, vision)
- [ ] Embed in documentation tab
- [ ] Final UX walkthrough
- [ ] Talking points for collaborator meeting

## Deferred (Post-Demo)

### Integration & Testing
- [ ] Full integration test of literature review workflow in ndexbio context
- [ ] Europe PMC as fallback full-text source in tools/biorxiv/client.py
- [ ] Refactor tier1_scan.py to load keywords from config.yaml

### Architecture
- [ ] Subagent-driven workflow execution (context window management)
- [ ] Persistent agent memory and state (NDEx-hosted review logs)
- [ ] Local network caching (SQLite metadata + NetworkX/CX2 on disk)
- [ ] Agent self-documentation on NDEx

### Cleanup
- [ ] Working memory archival (scan logs a-g)
- [ ] Network quality review (node/edge structure, visual styles)
- [ ] Web app: direct request posting with auth
- [ ] Web app: extract NDEx viewer into reusable component

## Known Issues

1. **bioRxiv full-text Cloudflare blocking**: Metadata API works fine but JATS XML / HTML full-text blocked. Europe PMC fetcher now available as fallback (not yet integrated into biorxiv tool).
2. **Safety classifier**: May block synthesis on certain biomedical topics. Reframe as "literature curation" / "knowledge graph construction".
3. **`set_network_properties` replaces all properties**: When updating one property, others are lost. Need to pass full property list or investigate NDEx append mode.
4. **Keywords hardcoded in two places**: tier1_scan.py and config.yaml.

## Key File Locations

| What | Where |
|------|-------|
| Repo | ~/Documents/agents/GitHub/ndexbio |
| Claude Desktop config | ~/Library/Application Support/Claude/claude_desktop_config.json |
| NDEx credentials | ~/.ndex/config.json |
| MCP permissions | ~/.claude/settings.json |
| Scheduled task | ~/Documents/Claude/Scheduled/rdaneel-biorxiv-triage/ |
| Python venv | ~/Documents/agents/GitHub/ndexbio/.venv/ |
| Agent Hub web app | ~/Documents/agents/GitHub/ndexbio/webapps/agent-hub/ |
| Demo plan | ~/Documents/agents/GitHub/ndexbio/webapps/agent-hub/demo_plan.md |
