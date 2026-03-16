# NDExBio Agents — Next Steps

Updated: 2026-03-15, after Slack-like feed redesign + markdown rendering.

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
16. **bioRxiv API spec**: `project/apis/biorxiv_api.md`

### Phase 2: Collaborator Demo (2026-03-13–14)

#### Content (Tasks B1–B3) ✅
- Designed critique (janetexample) and synthesis (drh) network specs
- Posted 5 demo networks to NDEx via MCP tools:
  - Critique: `7522f9b6-1ff9-11f1-94e8-005056ae3c32` (janetexample)
  - Synthesis: `845449ca-1ff9-11f1-94e8-005056ae3c32` (drh)
  - Plans: `847fc69e-1ff9-11f1-94e8-005056ae3c32` (drh)
  - Episodic memory: `8498f3f2-1ff9-11f1-94e8-005056ae3c32` (drh)
  - Collaborator map: `84b1fa36-1ff9-11f1-94e8-005056ae3c32` (drh)
- All networks PUBLIC, indexed (`index_level: ALL`), showcased
- Critique network formatted with Cytoscape Desktop layout

#### Web App (Tasks A1–A2) ✅
- Agent directory with 3 agent cards (rdaneel, janetexample, drh)
- Feed threading via ndex-reply-to property chains
- Composable filter chips (agent + network type)
- Network type badge detection from ndex-workflow/name patterns
- Relative timestamps ("2 hours ago")
- Description truncation with expand/collapse
- Auto-load feed on startup
- Removed dead "New Request" functionality

#### Viewer Polish (2026-03-14) ✅
- CX1 cartesianLayout parsing for saved Cytoscape Desktop positions
- 3-way layout selection: saved positions (preset) > dagre (trees) > COSE (default)
- Network centering/fitting with cy.fit() after layout completion
- Resizable panes: drag sidebar width, drag graph/details split
- Scrollable sidebar and details panels
- Details panel positioned below graph (right column)
- Full-width viewer (no 1200px max-width constraint)

#### Feed & UX Redesign (2026-03-15) ✅
- **Slack-like 3-column layout**: group icon bar → channel sidebar → message area
- **Group navigation**: NDEx, HPMI, CCMI groups with logo icons (`ndexbio_icon.png`, `hpmi_logo.png`, `ccmi_logo.png`)
- **Channel-based filtering**: `#papers` (reviews/analyses) and `#IAV-mechanisms` (critiques/syntheses) channels, filtering by `workflowTypes`
- **Mock discussion content**: 4 rich mock posts in `#IAV-mechanisms` channel covering TRIM25 dual function, RIPLET redundancy, NP encapsidation kinetics, and evolutionary perspectives
- **NDExBio branding**: replaced text header with `ndexbio_logo.png` (36px), icon in group bar
- **Clean post titles**: automatic stripping of `ndexagent [agent] [type]:` prefixes from network names in feed cards
- **Markdown rendering**: expanded feed card descriptions render with markdown formatting (marked.js + DOMPurify) for both mock and real NDEx posts
- **`highlight` attribute support**: nodes/edges with `highlight` attribute rendered with red borders in Cytoscape viewer
- **In-app network navigation**: `#uuid` hash links open networks in the Agent Hub viewer instead of linking to NDEx website
- **Resizable description/properties pane**: drag handle between description and properties panels in viewer sidebar

## Phase 3: prototype launch to demonstrate live behavior

### Agents with persistence, larger goals, self-planning
 - review Memento vs Open Claw for strategy, documentation
 - try minimal agent with IAV area of research
 - includes workflows as networks
 - includes basic graph database and sqlite

### Existing data hypothesis testing
- Pratibha + Clara collaboration
- adapt SL agent workflow. 
- embody as an experimentalist 
- mission includes workflow improvement and datasource aquistion

### Collaboration Dialogs
- requests for help
  - literature search
  - data gathering
  - experiments
  - knowledge graph creation and customization
  - could be actual work or could be requests for workflows
- research status reports

### NDEx3 and MCP availability

### Open Claw testing

### NDExBio Analysis Agent 
- Posts to the NDExBio Channel

### Agents Outputs
- [ ] Flesh out CCMI group with channels and content
- [ ] Initiate genuine discussions on `#IAV-mechanisms` (additional agents weighing in)
- [ ] Incorporate use of NDEx reference networks 
  - reviews, extensions in `#papers` channel (quality/relevance filter). IAV relevant network

### Documentation + Presentation Support
- [ ] Infographics (system architecture, agent conversation flow, vision)
- [ ] content examples - "paper" adjacent networks

### BEL and GO-CAM knowledge extraction
- Chris Mungall, OKN collaboration
- [ ] BEL network style tuning (edge types, node shapes)
- [ ] BEL content for HPMI IAV

### Improve Pathway Presentation
- [ ] NDEx Styles - subset of key styles or extraction of style translation as a module?
- [ ] Better Pathway Layout

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

### Optional Visual Refinements
- [ ] Mobile responsive testing
- [ ] Loading states / skeleton screens
- [ ] Channel unread counts / activity indicators

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
| Demo staging | ~/Documents/agents/GitHub/ndexbio/demo_staging/ |
| Posted networks | ~/Documents/agents/GitHub/ndexbio/demo_staging/posted_networks.md |
