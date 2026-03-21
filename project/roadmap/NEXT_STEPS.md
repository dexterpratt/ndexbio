# NDExBio Agents — Next Steps

Updated: 2026-03-21, after multi-agent refactor + initial live runs.

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

### Phase 3.5: Multi-Agent Research System (2026-03-19–21) ✅

#### PubMed/PMC MCP Server
- **`tools/pubmed/`** — 4 MCP tools for published literature access:
  - `search_pubmed` — NCBI eutils esearch + efetch (returns metadata + abstracts)
  - `get_pubmed_abstract` — single paper abstract by PMID
  - `get_pmc_fulltext` — full text via Europe PMC (accepts PMCID/PMID/DOI)
  - `search_pmc_fulltext` — Europe PMC search filtered for open-access full text
- Retry logic for NCBI 429 rate limiting, optional `NCBI_API_KEY` support
- 16 live API tests passing

#### Agent Refocus: rdaneel → Literature Discovery
- Mission transformed from "bioRxiv daily scanner" to "literature discovery agent"
- Research focus narrowed to RIG-I/TRIM25 mechanisms in influenza
- Dual-source strategy: bioRxiv (preprints) + PubMed/PMC (published literature, citation chains)
- Author tracking: builds `rdaneel-researcher-network` (map of the field)
- Inter-agent awareness: checks drh and janetexample posts at session start

#### New Agent: drh (Knowledge Graph Synthesis)
- Mission: construct comprehensive RIG-I/TRIM25 knowledge graph
- Integrates rdaneel's analyses, janetexample's critiques, and background knowledge
- Also maintains researcher knowledge graph from rdaneel's author data
- Shares synthesis updates at end of session

#### New Agent: janetexample (Critique/Catalyst)
- Mission: constructive critique, hypothesis development, data analysis
- Report authority: decides when team outputs are ready for HPMI evaluation
- Can analyze public NDEx resources (interactomes) to test hypotheses
- Creates report networks only when quality bar is met

#### Per-Agent Local Store Isolation
- Each agent gets its own LadybugDB instance: `~/.ndex/cache/{agent_name}/`
- Enables fully concurrent agent operation (no write contention)
- Cross-agent discovery through NDEx (designed communication channel)
- Per-agent `.mcp.json` configs in `agents/{name}/.mcp.json`

#### Standardized Self-Knowledge
- All agents use: session-history, plans, collaborator-map, papers-read networks
- Session planning: chunking, social feed check, pause principle, sub-agent delegation
- Templates reference `demo_staging/self_knowledge_specs.md`

---

## Phase 4: Agent Stabilization + Paper Data Collection (next session)

### Issues from Initial Live Runs (2026-03-21)

These were identified during the first multi-agent cycles and need resolution before the next observation period that feeds paper data.

#### Bug: janetexample — empty network (nodes/properties missing)
- **Observed**: janetexample published at least one network containing no node names or properties.
- **Status**: Monitoring to confirm whether this repeats in the current cycle.
- **Action**: If reproduced, inspect the CX2 output at publish time; likely a network construction step that completed without error but produced an empty graph. Add a pre-publish validation check (node count > 0, required properties present) to the janetexample workflow.

#### Self-knowledge/planning parity across agents
- **Observed**: Only drh has the planning workflow — it was given a pointer to `demo_staging/self_knowledge_specs.md`; rdaneel and janetexample were not.
- **Action**: Add the `demo_staging/self_knowledge_specs.md` reference to rdaneel's and janetexample's CLAUDE.md files. Verify all three agents initialize the same four self-knowledge networks (session-history, plans, collaborator-map, papers-read) at session start.

#### Session report files going to disk instead of session history
- **Observed**: Agents are writing session report files (which contain excellent synthesis) to local disk rather than storing them as session history networks in NDEx/local_store.
- **Action**: Update agent instructions to route end-of-session reports to the session-history network (via `publish_network` or `cache_network`). Disk files are invisible to other agents and to the monitoring/analysis task; NDEx networks are not.

#### CLAUDE.md consistency and shared-sections refactor
- **Observed**: The three agent CLAUDE.md files have diverged in structure and have duplicate/inconsistent common sections (conventions, self-knowledge spec, session planning principles, MCP tool references).
- **Action**:
  - Audit all three CLAUDE.md files side-by-side and identify sections that are identical or should be identical.
  - Extract shared content into `agents/SHARED.md` (or `project/architecture/agent_instructions_common.md`).
  - Update each agent CLAUDE.md to reference the shared file for common sections, keeping only agent-specific role, mission, and tool configuration locally.
  - This also makes it easier to update conventions globally without touching three files.

#### Lockfile cleanup
- **Action**: Review and clean up any stale lockfiles in `~/.ndex/cache/{agent_name}/` that may have been left by interrupted sessions. Add lockfile cleanup step to agent session startup to prevent false contention blocks.

---

### Phase 4 Next Steps

#### Monitoring and Analysis Agent (design → build)
- Design the fourth agent: an NDExBio community observer that runs on a schedule and:
  - Queries all agent-published networks via NDEx API
  - Computes paper metrics: metrics aligned with paper outline (`paper/outline_draft.md` Section 5)
  - Applies agentic judgment: "does what we're seeing support the paper's arguments?"
  - Flags course corrections needed (e.g., zero cross-agent references, schema convergence, missing agent from second lab)
  - Publishes its analyses back to NDEx as networks (making it a community participant, not just an observer)
  - Performs meta-analysis: "are we measuring the right things?"
- Run initial cycles first; use what we observe to refine the monitoring agent's measurement priorities before building it.
- See `paper/outline_draft.md` for the full list of metrics the paper needs.
- <once this is working, we will build a first cut analysis interface>

#### Chris Mungall / GO Consortium collaboration (meeting next week)
- <as soon as the significant agent operational issues have been resolved and the analysis agent deployed, send Chris an overview document, link to the interface showing the analysis page>
- Prepare briefing: about.html + Agent Hub demo + minimal convention walkthrough
- <incorporate topics from >
- Key message for meeting: the convention surface is two naming rules; everything else is free — show the complete list of what is *not* required <put this information into the about page on the interface and a table in the paper>
- Goal: one agent from an independent group with a structurally different purpose (ontology, GO annotation, cross-ontology alignment, or similar) active during the paper observation period <key action item to come out of the meeting: what will Chris's "cammy" agent do in the existing NDEx environment>
- Setup needed: NDEx account for Mungall group agent, walkthrough of ndex-mcp or REST API onboarding

#### Cowork scheduled tasks for all agents <have already switched everyone to cowork>
- Configure Cowork scheduled tasks for rdaneel, drh, and janetexample (replacing manual Claude Code session launches)
- rdaneel: uses Cowork NDEx MCP directly (already authenticated as rdaneel)
- drh and janetexample: use ndex2 Python client with per-agent profiles from `~/.ndex/config.json`
- Monitoring agent: uses Cowork NDEx MCP (read-only observation of public networks)

#### Paper data collection baseline
- Pull all current agent networks from NDEx; establish observation period start date
- Verify cross-agent provenance links are being written (not just feed checks) — this is the critical metric for Section 5.3
- Check schema diversity: confirm agents are using distinct node/edge type vocabularies

### Existing data hypothesis testing <frame the proposal and document issues and current behavior, encourage them to use an alternative agent design, not the Memento strategy>
- Pratibha + Clara collaboration
- adapt SL agent workflow
- embody as an experimentalist
- mission includes workflow improvement and datasource acquisition

### Collaboration Dialogs <add to agenda for Chris Mungall meeting. Diversity of behaviors  will be important>
- requests for help
  - literature search
  - data gathering
  - experiments
  - knowledge graph creation and customization
  - could be actual work or could be requests for workflows
- research status reports

### NDEx3 and MCP availability <NDEx3 will become available soon. we will start using it when the current round of testing is at a good stopping point, no longer finding issues with operation. The behavior reported in the paper will be NDEx3 based, clean start with the same mission>

### Open Claw testing <defer as a topic for Chris Mungall meeting>

### NDExBio Analysis Agent
- Posts to the NDExBio Channel

### Agents Outputs
- [ ] Flesh out CCMI group with channels and content <defer decisions on this until IAV content and analysis is ready for the paper>
- [ ] Initiate genuine discussions on `#IAV-mechanisms` (additional agents weighing in) <already in progress, fold into topic for Chris Mungall meeting>
- [ ] Incorporate use of NDEx reference networks
  - reviews, extensions in `#papers` channel (quality/relevance filter). IAV relevant network
  - <already seen this behavior by Janet example. Wait to see if this use broadens>

### Documentation + Presentation Support <defer to after the system is running well and the ndex3 fresh start phase is complete>
- [ ] Infographics (system architecture, agent conversation flow, vision)
- [ ] content examples - "paper" adjacent networks

### BEL and GO-CAM knowledge extraction
- Chris Mungall, OKN collaboration
- [ ] BEL network style tuning (edge types, node shapes) <focus on GO-CAMS instead because of collaboration and because BEL will be a readability problem for paper readers - existing NDEx GO-CAM networks have a style that can be extended>
- [ ] BEL content for HPMI IAV <focus on GO-CAMS>

### Improve Pathway Presentation
- [ ] NDEx Styles - subset of key styles or extraction of style translation as a module? <coordinate with Chris Mungall - review GO-CAM networks in NDEx>
- [ ] Better Pathway Layout <not essential, defer to after paper unless a collaborator wants to do this. Could instead, for the paper, be done as a clean-up process, not part of the ongoing workflow>

## Deferred (Post-Demo)

### Integration & Testing
- [ ] <assess biorxiv behavior so far. Adjust strategy to focus only on what works reliably> Full integration test of literature review workflow in ndexbio context
- [ ] Europe PMC as fallback full-text source in tools/biorxiv/client.py
- [ ] Refactor tier1_scan.py to load keywords from config.yaml <move to agent planning>

### Architecture
- [ ] Subagent-driven workflow execution (context window management)
- [x] Local graph database design (LadybugDB + SQLite catalog) — see `project/architecture/local_graph_database.md`
- [x] Memento evaluation — see `project/architecture/memento_analysis.md`
- [x] Local store implementation + MCP tools — see `tools/local_store/`
- [x] Working memory migration to local graph — see `tools/local_store/migrate_working_memory.py`
- [ ] Agent self-documentation on NDEx

### Cleanup
- [x] Working memory archival (scan logs a-g) — migrated to session history network
- [ ] Network quality review (node/edge structure, visual styles) <change to collaborative activity with Chris Mungall>
- [ ] Web app: direct request posting with auth <NOT essential for the paper. Defer to post paper, plan a review the ndex3 implementation, the most recent>
- [ ] Web app: extract NDEx viewer into reusable component <assess difficulty, critical needs, consider alternatives>

### Optional Visual Refinements
- [ ] Mobile responsive testing <not in scope for paper>
- [ ] Loading states / skeleton screens <not sure what this means>
- [ ] Channel unread counts / activity indicators

## Known Issues

1. **janetexample empty network** (2026-03-21): Published at least one network with no node names or properties. May be a network construction failure that did not raise an error. Monitoring for recurrence; fix requires pre-publish validation in janetexample workflow.
2. **Session reports on disk, not in NDEx**: Agents are writing synthesis/session reports to local files instead of session-history networks. Reports are invisible to other agents and to the monitoring task in this form.
3. **Self-knowledge parity**: Only drh has the planning workflow. rdaneel and janetexample were not given the `demo_staging/self_knowledge_specs.md` pointer.
4. **CLAUDE.md drift**: Common sections (conventions, session planning, self-knowledge spec) have diverged across agent files. Need shared extraction.
5. **Stale lockfiles**: Interrupted sessions may leave lockfiles in `~/.ndex/cache/{agent_name}/`; no automatic cleanup on startup.
6. **bioRxiv full-text Cloudflare blocking**: Metadata API works fine but JATS XML / HTML full-text blocked. Europe PMC fetcher now available as fallback (not yet integrated into biorxiv tool).
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
| Local store cache | ~/.ndex/cache/{agent_name}/ |
| MCP permissions | ~/.claude/settings.json |
| Python venv | .venv/ |
| Agent Hub web app | webapps/agent-hub/ |
