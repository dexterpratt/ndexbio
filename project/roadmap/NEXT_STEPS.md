# NDExBio Agents — Next Steps

Updated: 2026-03-16, after local store implementation + migration.

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

### Phase 2.5: Local Graph Database + Agent Persistence (2026-03-16) ✅

#### Implementation
- **`tools/local_store/`** — two-tier local store (SQLite catalog + LadybugDB graph DB)
  - `catalog.py` — SQLite metadata catalog
  - `graph_store.py` — LadybugDB graph schema and operations
  - `cx2_import.py` / `cx2_export.py` — CX2 ↔ graph DB conversion
  - `store.py` — `LocalStore` integrated API
  - `server.py` — MCP server with 13 tools
  - `migrate_working_memory.py` — migration from markdown working memory
- **79 tests** across T0–T7 + MCP tools, all passing
- **`real_ladybug`** v0.15.1 (LadybugDB, active fork of archived KuzuDB)

#### MCP Tools (13)
- Catalog: `query_catalog`, `get_cached_network`
- Graph queries: `query_graph`, `get_network_nodes`, `get_network_edges`, `find_neighbors`, `find_path`, `find_contradictions`
- NDEx sync: `cache_network`, `publish_network`, `check_staleness`
- Management: `delete_cached_network`

#### Migration
- 28 NDEx networks cached locally (all rdaneel triage outputs + demo networks)
- Session history network: 9 scan sessions as queryable graph
- Paper tracker network: 7 papers + 11 proteins + cross-references
- 30 total networks in local store

#### Key Design Decisions
- Global node IDs via blake2b hash of `(network_uuid, cx2_node_id)` — avoids PK collisions across networks
- CX2 JSON files remain canonical format; graph DB is a queryable cache
- Local-first, NDEx as publication venue
- `~/.ndex/cache/` as shared cache location
- Empty MAP workaround with `__empty__` sentinel key

## Phase 3: Prototype Launch — Live Agent Behavior

### Agent Integration with Local Store (active)

rdaneel's CLAUDE.md updated to use local store for:
- Caching networks it generates (triage outputs auto-cached before NDEx publish)
- Session history tracking (episodic memory as a graph network)
- Cross-network queries during Tier 3 analysis
- Paper deduplication via local catalog queries

**Next: test episode** — run rdaneel's triage pipeline with local store integration, verify it caches outputs and updates session history. Once confirmed, re-enable as Claude Cowork scheduled task.

### Agents with larger goals, self-planning
 - try minimal agent with IAV area of research
 - includes workflows as networks

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
- [x] Local graph database design (LadybugDB + SQLite catalog) — see `project/architecture/local_graph_database.md`
- [x] Memento evaluation — see `project/architecture/memento_analysis.md`
- [x] Local store implementation + MCP tools — see `tools/local_store/`
- [x] Working memory migration to local graph — see `tools/local_store/migrate_working_memory.py`
- [ ] Agent self-documentation on NDEx

### Cleanup
- [x] Working memory archival (scan logs a-g) — migrated to session history network
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
5. **LadybugDB empty MAP workaround**: Can't pass empty list parameters to Cypher. Uses `__empty__` sentinel key, cleaned automatically by `_clean_map()`.
6. **LadybugDB `nodes(path)` syntax**: List comprehension `[n IN nodes(path) | n.name]` not supported. Extract node names in Python instead.

## Key File Locations

| What | Where |
|------|-------|
| Repo | ~/Dropbox/GitHub/ndexbio |
| NDEx credentials | ~/.ndex/config.json |
| Local store cache | ~/.ndex/cache/ |
| MCP permissions | ~/.claude/settings.json |
| Python venv | .venv/ |
| Agent Hub web app | webapps/agent-hub/ |
