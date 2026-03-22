# Demo Task Prompts

Five episodic tasks, designed to run one at a time via Cowork scheduled tasks.
Each task does one logical chunk, writes its outputs, and stops.

## Agent Account Mapping

| Role | NDEx username | Display name |
|------|--------------|--------------|
| Literature reviewer | `rdaneel` | R. Daneel |
| Critique / pathway expert | `janetexample` | Janet (critique agent) |
| Synthesizer / integrator | `drh` | DRH (synthesis agent) |

**Prerequisite (done):** User has repurposed existing NDEx accounts
`janetexample` and `drh`. These need to be added to `~/.ndex/config.json`
profiles before Tasks B2/B3.

---

## Task B1: Design critique and synthesis network content ✅ COMPLETE

**Output files:**
- `demo_staging/critique_spec.md` — janetexample's critique (9 nodes, 9 edges)
- `demo_staging/synthesis_spec.md` — drh's synthesis (16 nodes, 18 edges)
- `demo_staging/self_knowledge_specs.md` — drh's 3 self-knowledge networks

**Status:** Complete.

---

## Task B2: Post demo networks to NDEx ✅ COMPLETE

**Goal:** Take the specs from B1 (reviewed by user), post them to NDEx using
the MCP tools. Record all UUIDs.

**Prerequisite:** User has added `janetexample` and `drh` profiles to
`~/.ndex/config.json`. User has reviewed and approved the specs in demo_staging/.

**Prompt:**

```
You are posting demo content networks to NDEx. The network specs have already
been designed and reviewed — your job is to execute the posting.

AGENT ACCOUNT MAPPING:
- janetexample = Critique agent (posts critique network)
- drh = Synthesizer agent (posts synthesis + 3 self-knowledge networks)
- rdaneel = Literature reviewer (existing networks, no new posting needed)

CONTEXT:
- Read demo_staging/critique_spec.md — contains janetexample's critique network JSON spec
- Read demo_staging/synthesis_spec.md — contains drh's synthesis network JSON spec
- Read demo_staging/self_knowledge_specs.md — contains drh's 3 self-knowledge networks
- Read project/architecture/conventions.md for conventions

IMPORTANT: The MCP server authenticates as one profile at a time. Check which
profile is active using get_connection_status. You can only post networks for
the currently authenticated user.

STEPS:
1. get_connection_status — confirm which NDEx user you're authenticated as
2. If authenticated as rdaneel: you can only verify existing networks, not post
   as janetexample/drh. In this case, write the network specs as JSON files in
   demo_staging/ and document that the user needs to post them manually using
   the appropriate profiles. STOP here.
3. If authenticated as janetexample: post the critique network
4. If authenticated as drh: post the synthesis + 3 self-knowledge networks
5. For each network posted:
   - Record the UUID
   - Set visibility to PUBLIC
   - Set index_level to ALL (should happen automatically via create_network)
6. After posting the critique network, update the synthesis spec to replace
   CRITIQUE_UUID with the actual UUID, then post the synthesis
7. Write demo_staging/posted_networks.md with a table of all UUIDs, names,
   and which account owns each

NOTE: This task may need to run twice (once per profile) if the MCP server
can only authenticate as one user at a time. That's fine — record partial
progress in posted_networks.md and the next run picks up where this left off.

STOP CONDITIONS:
- If authentication fails for any profile, stop and report which profiles work
- If a network spec has issues (missing name, malformed JSON), stop and report
- If you can only authenticate as rdaneel, write the ready-to-post JSON files
  and stop with clear instructions for the user
```

---

## Task B3: Configure demo network visibility and showcase ✅ COMPLETE

**Goal:** Ensure all demo networks are PUBLIC, indexed, and showcased on
their respective agent profiles.

**Prerequisite:** B2 complete. demo_staging/posted_networks.md exists with UUIDs.

**Prompt:**

```
You are finalizing the visibility and discoverability of demo networks on NDEx.

CONTEXT:
- Read demo_staging/posted_networks.md for the list of posted network UUIDs
- Each network needs to be: PUBLIC, index_level ALL, and showcase=true

STEPS:
1. For each network UUID in posted_networks.md:
   a. get_network_summary — verify it exists and check current visibility
   b. set_network_visibility — set to PUBLIC if not already
   c. set_network_system_properties — set {"index_level": "ALL", "showcase": true}
2. Also check rdaneel's existing analysis/review/highlight networks for the
   TenVIP-seq paper (UUIDs in demo_staging/):
   - e9cbd797-1e3b-11f1-94e8-005056ae3c32 (analysis)
   - 13bbe281-1e3b-11f1-94e8-005056ae3c32 (review)
   - f9678239-1e3b-11f1-94e8-005056ae3c32 (highlight)
   Verify these are PUBLIC and showcased.
3. Write demo_staging/network_status.md with final status of all demo networks

NOTE: This task may need to run multiple times if different profiles are needed
to update different networks. Each agent can only modify their own networks.

STOP CONDITIONS:
- If set_network_system_properties fails (e.g., wrong auth profile), report
  which networks couldn't be updated and which profile is needed
- If any network UUID is missing or invalid, stop and report
```

---

## Task A1: Web app — Agent directory and feed threading ✅ COMPLETE

**Goal:** Add agent directory section and conversation threading to the
Agent Hub web app.

**Prompt:**

```
You are enhancing the NDEx Agent Hub web app for a collaborator demo.
The app is in webapps/agent-hub/ (index.html, app.js, ndex-api.js, style.css).

CONTEXT:
- Read webapps/agent-hub/demo_plan.md for the full demo plan
- Read all 4 web app files to understand current structure
- Read project/architecture/conventions.md for NDEx conventions (especially
  ndex-reply-to for threading)
- The app must work as static files (GitHub Pages) — no backend, no build step
- All data comes from the public NDEx API

AGENT ACCOUNT MAPPING (use these in the agent directory):
| Display Name | Username | Role |
|-------------|----------|------|
| R. Daneel | rdaneel | Literature reviewer — scans bioRxiv, extracts knowledge graphs |
| Janet | janetexample | Critique / pathway expert — reviews and extends analyses |
| DRH | drh | Synthesizer — integrates findings, maintains self-knowledge |

FEATURE 1 — Agent Directory:
Add a section (top of feed or separate tab) showing 3 agent cards.

Each card should show: agent name, role description, link to NDEx profile
(https://www.ndexbio.org/user/USERNAME), and a count or list of their
showcased networks (fetched via the NDEx API get_user_networks or search).

Hardcode the agent list in a config array in app.js — this is fine for demo.

FEATURE 2 — Feed Threading:
Currently the feed shows networks as a flat list. Add conversation threading:

- When loading networks, check for ndex-reply-to property (in network attributes)
- Group networks into threads: root network + all replies (direct and transitive)
- Display threads as groups in the feed:
  - Root network shown full-size
  - Replies shown indented underneath, with a visual connector
  - Thread sorted by most recent reply (newest threads first)
- Networks without ndex-reply-to remain as standalone items

Threading data model: ndex-reply-to contains the UUID of the parent network.
A thread is formed by following reply-to chains to the root.

IMPLEMENTATION NOTES:
- The NDEx API returns network attributes in the summary. Check the
  "properties" field of each network summary for ndex-reply-to.
- If properties aren't in the summary, you may need to fetch them separately
  via get_network_summary for each network. Consider performance: batch if
  possible, or fetch lazily on display.
- Keep the existing feed search/filter functionality working.

STOP CONDITIONS:
- If you discover the NDEx API doesn't return properties in user_network
  summaries (making threading expensive), document the issue and propose
  an alternative approach. Don't implement a workaround without approval.
- If the current app structure makes threading very complex (e.g., the feed
  rendering is tightly coupled), propose a refactoring plan and stop.
- Test your changes mentally against the demo scenario: 3 agents, ~5-8
  networks each, 1 thread of 3 (review → critique → synthesis). If the
  code wouldn't handle this correctly, explain why and stop.
```

---

## Task A2: Web app — Visual polish and layout ✅ COMPLETE

**Goal:** Add relative timestamps, author filtering, dagre layout for tree
networks, and general visual polish.

**Prerequisite:** A1 complete (directory and threading in place).

**Prompt:**

```
You are doing visual polish on the NDEx Agent Hub web app after the core
features (agent directory + feed threading) have been added.

CONTEXT:
- Read all files in webapps/agent-hub/ — they have been modified by Task A1
- Read webapps/agent-hub/demo_plan.md for demo requirements

AGENT ACCOUNT MAPPING:
- rdaneel = R. Daneel (reviewer)
- janetexample = Janet (critique)
- drh = DRH (synthesizer)

FEATURE 1 — Relative Timestamps:
- Network summaries include modificationTime (Unix epoch ms)
- Display as "2 hours ago", "3 days ago", etc. instead of raw dates
- Write a small utility function, not a library dependency

FEATURE 2 — Author Filtering:
- Click an agent name (in feed or directory) to filter the feed to that agent
- Show a "clear filter" button when filtered
- Filter by matching the ndex-agent property or the network owner username

FEATURE 3 — Dagre Layout for Tree Networks:
- Add dagre.js via CDN (https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js)
  and the cytoscape-dagre extension
- Detect tree/hierarchical networks: check for ndex-data-type property containing
  "plan" or "outline", OR detect DAG structure (no cycles, single root)
- Apply dagre top-down layout for detected trees
- Keep COSE layout as default for all other networks

FEATURE 4 — Visual Polish:
- Agent cards: subtle color coding or icons per agent role
- Feed cards: better spacing, typography, truncated descriptions with expand
- Network viewer: improve node label readability (font size, background, contrast)
- Mobile-responsive basics (the demo will likely be on a laptop but should
  look good at various window sizes)

IMPLEMENTATION NOTES:
- All changes are CSS + JS only. No build tools, no npm.
- Load dagre from CDN in index.html
- Test mentally: the demo has ~20 networks across 3 agents, 1 thread, and
  3 tree-structured self-knowledge networks from drh

STOP CONDITIONS:
- If Task A1's changes created structural issues that block these features,
  document what needs to be fixed and stop
- If dagre CDN is unavailable or the cytoscape-dagre integration is complex,
  implement the other features and note dagre as deferred
```

---

## Coordination Notes

- All five tasks (B1→B2→B3, A1→A2) are **COMPLETE**
- Posted network UUIDs recorded in `demo_staging/posted_networks.md`
- Remaining polish: network viewer centering/fitting, demo documentation
