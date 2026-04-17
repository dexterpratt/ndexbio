# rzenith Curator Evolution + BEL / GO-CAM Integration Plan

Written 2026-04-14. Captures the design decisions and work sequence emerging from the session on infrastructure verification → curator policy → BEL representation. Not a rigid roadmap — a durable reference so work does not get lost across sessions or when context runs out mid-session.

Cross-references:
- `ndexbio/project/deferred_tasks.md` — lighter-weight running list
- `memento/workflows/BEL/SKILL.md` — the BEL authoring skill (new)
- `memento/workflows/BEL/bel_prompt.md` — the legacy BEL extraction prompt (reference, not authoritative)
- `memento/agents/rzenith/CLAUDE.md` — rzenith's behavioral instructions (target of several revisions below)
- `memento/agents/SHARED.md` — shared agent protocols (target of smaller revisions)

---

## Core design decisions (session output)

These are the decisions we want to preserve regardless of what gets built first.

### 1. Curator / researcher division of labor

- **rzenith is the curator agent**: evolves the current best synthesis of what's known. It validates, scope-qualifies, splits, retires, and adds provenance to edges. It does literature search in support of curation.
- **rgiskard (and future researcher agents) conduct and hypothesize**: novel synthesis, mechanism discovery, hypothesis generation.
- The line is not "no hypotheses in rzenith" — every mechanistic edge has embedded assumptions. The line is: **rzenith adjudicates existing evidence; it does not conduct new synthesis or pursue research questions.**
- When review surfaces a genuinely research-worthy open problem, rzenith publishes a consultation request to a researcher agent (same pattern as Phase 2-3 POC, reverse direction). Consultation is an escape hatch, not a standard step — expected usage is ~1 per 10-20 reviewed edges.

### 2. Curation policy / provenance discipline

Every edge in rzenith's knowledge graph carries:

- `evidence_quote` — brief verbatim quote (<40 words) from the source
- `pmid` or `doi` — the source paper
- `supporting_analysis_uuid` — UUID of an agent-authored analysis network that covers the source, if one exists (version-pinned, not "latest")
- `scope` — qualifier (cell type, in vitro / in vivo, n, etc.)
- `evidence_tier` — `established` / `supported` / `tentative` / `contested`
- `last_validated` — ISO date
- `reviewed_in` — link to the review-session node in the review-log network

Edges without full provenance are treated as backlog for curation review, not as finished knowledge.

### 3. Review protocol

- Incremental, prioritized, sample-based. Target: 3-5 edges per review session.
- Priority signals (roughly ordered):
  1. Rot risk — oldest `last_validated`
  2. Load-bearing — high inbound reference count from other networks
  3. Evidence-tier mismatch — candidates for promotion or demotion
  4. Internal contradictions — pairs of edges disagreeing within the KG
  5. Adjacent to recently-added literature
- Per edge, the decision tree: keep + provenance, keep + scope-qualify, split, demote tier, retire to `superseded`, consult a researcher. First four are the common path; consultation is rare.
- **Never delete.** Retire to `evidence_status: superseded` (or `retracted`, `contested`, `current`) so `ndex-reply-to` links into the KG don't break.

### 4. Review artifacts

Every review session produces:
- Edits to the KG (new / modified / retired edges with provenance)
- A review-log network (new, to be designed) — one node per reviewed edge per session, with outcome and rationale
- A KG version bump when the delta is non-trivial (e.g., v1.1 → v1.2)
- Optional consultation request networks for research-worthy gaps

### 5. Knowledge representation

- **BEL is the internal authoring representation** for mechanism edges in rzenith's (and eventually other agents') knowledge graphs.
  - Rationale: expressive for PTMs, abundances, complexes, negative findings, contested claims. Small, compositional relation vocabulary. LLM-tractable (per Dexter's `textToKnowledgeGraph` paper).
  - Agents use BEL causal subset: `directlyIncreases`, `directlyDecreases`, `increases`, `decreases`, `positiveCorrelation`, `negativeCorrelation`, `association`, `causesNoChange`, plus structural: `hasComponent`, `hasComponents`, `hasMember`, `isA`, `subProcessOf`, `rateLimitingStepOf`.
  - Entity namespaces shared with GO-CAM where applicable (HGNC, UniProt, GO, ChEBI, DOID, EFO, HP, FPLX).
- **GO-CAM is a downstream view**, not the authoring format.
  - Rationale: collaboration with Chris Mungall + GO ecosystem interop matters, but GO-CAM's vocabulary-selection burden is wrong for agent authorship.
  - Lossy subset: PTM state, abundances, negative findings, contested claims degrade or drop in the GO-CAM view.
  - Tool to be built: deterministic BEL → GO-CAM translator with escape-hatch for unmapped constructs.
- **Degradation path**: when a claim cannot be expressed cleanly in BEL, author a freeform `node_type: "claim"` node with evidence annotations. Do not force bad BEL.

### 6. Agent architecture roles

- **Main agents (rzenith, rgiskard, etc.)**: own plans, persona, KG, consultation relationships.
- **Subagents** for context-hungry, well-specified, identity-neutral work:
  - Paper-processor subagent: PMID/DOI → structured BEL tuples + paper summary
  - (Later) GO-CAM audit subagent: periodic pass over a KG, reports GO-CAM renderability
- **Tools (MCP or scripts)** for deterministic transformations:
  - BEL → GO-CAM translator
  - Namespace-lookup (name → ID) — see deferred_tasks.md
  - Retraction-checker (periodic) — deferred

---

## Phased work plan

Order reflects a mix of blocking-dependency and value-per-effort. Pre-plan work, not committed sprint.

### Phase A — Foundation (unblocks everything else)

**A1. BEL SKILL.md scaffold** *(done 2026-04-14)*
- File: `memento/workflows/BEL/SKILL.md`
- Next: populate `reference/` subdirectory:
  - `bel-grammar.md` — condense from `bel_prompt.md` with the cleanups called out in session (remove `challenges`-as-relation, fix numeric-ID example, normalize `GO:` vs `GOBP:`)
  - `namespace-policy.md` — entity classes + fallback rules for unresolved IDs
  - `bel-examples.md` — 3-5 clean extraction examples, agent-authorship oriented
  - `bel-to-gocam-mapping.md` — initial mapping rules, marked as stub

**A2. Evidence-annotation schema fixed into agent writing practice**
- Update `memento/agents/SHARED.md` with the provenance field set from decision §2
- Update `memento/agents/rzenith/CLAUDE.md` with curation policy section (decisions §1-4)
- Test by having rzenith backfill provenance on 3 selected v1.1 KB edges (candidate: ATM → STING, MRE11 → PD-L1, one other)

**A3. Review-log network template**
- Define a CX2 template: nodes = reviewed edges, properties = original/updated state, rationale, action
- Document in `ndexbio/project/architecture/` (sibling to existing conventions doc)
- Bootstrap network `rzenith-review-log` on local NDEx

### Phase B — Paper-processor subagent

**This phase will be executed in a fresh Claude session to preserve context for continuing design discussion in the original session.** The context-isolated session picks up the plan from this document.

Agent-ready implementation of the BEL skill as a subagent.

**Kickoff context for the fresh session:**
- Prerequisites complete: BEL SKILL.md + all four reference files, SHARED.md provenance schema, rzenith/CLAUDE.md curation protocol, review-log architecture spec.
- Motivation: validated by 2026-04-14 backfill test — three reviewed edges required simultaneous paper-reading across multiple abstracts, confirming main-context pressure will bind at scale.
- No code exists yet for the subagent; start from scratch.

**B1. Subagent definition**
- Location: `memento/tools/paper_processor/` (new) or as a subagent markdown under `memento/workflows/BEL/subagent/`
- Input contract: `{paper_id, optional_focus_context}`
  - `paper_id`: PMID, DOI, or PMC ID
  - `optional_focus_context`: free-text hint like "focus on DDR-cGAS-STING mechanism claims" to guide extraction
- Behavior:
  1. Resolve paper_id → full-text URL (Europe PMC for open-access, abstract fallback for closed-access)
  2. Fetch full-text via `get_pmc_fulltext` or equivalent
  3. Apply `workflows/BEL/SKILL.md` protocol
  4. Return structured output
- Output contract (strict JSON):
  ```json
  {
    "paper_id": "...",
    "paper_summary": {
      "main_claims": [...],
      "methods": "...",
      "scope": "cell lines / in vivo / species / n",
      "limitations": [...]
    },
    "bel_statements": [
      {
        "bel": "...",
        "evidence": { "evidence_quote": "...", "pmid": "...", "scope": "...", "evidence_tier": "..." },
        "confidence": "high|medium|low"
      },
      ...
    ],
    "unresolved_entities": [
      {"label": "...", "suggested_namespace": "HGNC", "pending_lookup": true}
    ]
  }
  ```
- Subagent uses its own isolated context; main agent just passes paper_id and receives structured output

**B2. Integration smoke test**
- Pick a paper already encountered in the 2026-04-14 backfill test — e.g., Cho 2024 (PMID 38200309, MRE11 de-sequestration of cGAS). The review in Edge 2 produced one BEL statement from this paper; subagent output should match or improve on that.
- Invoke the subagent, compare its output to the manually-derived annotations from the backfill test
- Validate: output tuples well-formed, quotes match source text, HGNC/GO IDs correct (or properly flagged as `deferred_lookup`), scope populated
- Iterate on skill + subagent prompt until output quality is consistently acceptable

**B3. Wire into rzenith review protocol**
- Update rzenith's review protocol (in `memento/agents/rzenith/CLAUDE.md` step 2 "Check the literature") to invoke the paper-processor subagent when an edge's supporting paper isn't already covered by an existing analysis network
- Cache the subagent's output as an analysis network in NDEx — attach the UUID to both the KG edge's `supporting_analysis_uuid` field and rzenith's papers-read network
- Future review sessions can then reference the analysis UUID without re-reading the paper

**Handoff artifacts for the fresh session:**
- This plan file
- `memento/workflows/BEL/SKILL.md` + reference/*.md (the skill the subagent applies)
- `memento/agents/SHARED.md` (provenance schema the subagent output must conform to)
- `ndexbio/project/deferred_tasks.md` (for flagging any issues surfaced during B that should carry back to the original session)

### Phase C — BEL → GO-CAM translator

Deterministic tool, not a subagent.

**C1. Core mappings**
- Implement in `memento/tools/bel_gocam/` (new)
- Start with a dozen of the most common BEL patterns:
  - `act(p(X)) directlyIncreases act(p(Y))` → GO-CAM activity-edge with `RO:directly positively regulates`
  - `p(X, pmod(...)) directlyIncreases act(...)` → activity enabled by modified protein (with modification-state flag)
  - `complex(p(X), p(Y))` → GO-CAM complex node
  - `bp(GO:X)` → GO-CAM biological process
  - etc.
- For each input BEL statement, return `{gocam: <output>}` or `{unmapped: <reason>}`

**C2. CLI and test corpus**
- Unit tests on BEL-input / GO-CAM-output pairs
- Run over rzenith's current KG, produce renderability report

**C3. Document the mapping for Chris Mungall**
- `ndexbio/project/bel_to_gocam_mapping.md` or similar
- Purpose: make the architectural choice (BEL internal, GO-CAM view) legible to collaborators

### Phase D — Steady-state review operation

Once A + B are in place, rzenith's review sessions become routine.

**D1. First systematic review pass over KG v1.1**
- Enumerate v1.1 edges lacking full provenance
- For edges traceable to rgiskard's consultation response, backfill from there
- For pure-rzenith-latent-knowledge edges, rzenith does own literature work (using paper-processor subagent)
- Produce KG v1.2 with full provenance on all reviewed edges, retiring/splitting as needed

**D2. Cadence policy**
- rzenith's scheduled run (daily) spends part of each session on review
- 3-5 edges reviewed per session — over a month, gets through meaningful portion of a 60-80 edge KB
- High-priority edges (load-bearing, contested) cycled faster than peripheral ones

### Phase E — Later work (not blocking)

- GO-CAM audit subagent (periodic pass, produces audit report network)
- Namespace-lookup MCP (name → HGNC/GO/ChEBI/UniProt ID)
- Retraction-checking (periodic)
- KG version-pinning / snapshot discipline (formalize v1.1 → v1.2 delta reporting)

---

## Open design questions

These are not blocking but deserve attention at the right phase:

1. **Where does the review-log network live?** Owned by rzenith (most natural) or as a community-visible audit trail? Leaning rzenith-owned, PUBLIC.

2. **Version-pinning of supporting_analysis_uuid.** If rgiskard updates an analysis, does rzenith's edge silently track the new content (by UUID, which would stay stable if the network is updated in place) or is this a separate problem? Needs thought.

3. **Consultation-from-review output format.** Phase 2-3 POC used a request network with specific questions. When rzenith spawns a consultation from review, should it include the edge UUID being reviewed as context? Likely yes, but the threading convention needs to be explicit.

4. **Evidence-tier promotion criteria.** What does "supported" → "established" require? Minimum N sources? Must include in vivo? Define when we have more cases to look at.

5. **Handling of freeform-claim-nodes in the GO-CAM view.** They won't render. Do we carry them as out-of-scope notes in the export, or drop them silently?

6. **Skill invocation mechanics.** The harness skill system has certain trigger semantics. Need to verify the BEL SKILL.md frontmatter description matches what actually triggers it for agent sessions vs manual invocation.

---

## Status dashboard

| Item | Status | Notes |
|---|---|---|
| A1 SKILL.md scaffold | ✅ done | 2026-04-14 |
| A1 reference/bel-grammar.md | ✅ done | 2026-04-14 |
| A1 reference/namespace-policy.md | ✅ done | 2026-04-14 |
| A1 reference/bel-examples.md | ✅ done | 2026-04-14 |
| A1 reference/bel-to-gocam-mapping.md | ✅ done (stub) | 2026-04-14; real mapping is Phase C |
| A2 SHARED.md provenance schema | ✅ done (+ amendments) | 2026-04-14; added Edge Provenance Schema + Knowledge Representation; amended with `superseded_by` field and new-node provenance section after backfill test |
| A2 rzenith/CLAUDE.md curation policy | ✅ done (+ amendments) | 2026-04-14; added Curation Review Protocol; amended with compound actions, `split-add` / `retire-and-replace` dispositions, and pointers to pending_lookups / note_for_future_pass in review-log |
| A2 backfill test (dry-run) | ✅ done | 2026-04-14; 3 edges reviewed as dry-run (Option Y — NDEx read, no local-store writes due to concurrency lock). Surfaced 5 protocol amendments (applied) and validated Phase A protocol end-to-end. Proposed diffs captured in this session's transcript. |
| A2 commit backfill diffs to live KB | ⏳ pending | blocked on DB lock situation (Claude app relaunch needed); once unblocked, commit: 2 retires, 5 new edges, 1 new node, 3 edge-review entries bootstrapping `rzenith-review-log`, and 1 consultation request to rgiskard |
| A3 review-log network spec | ✅ done (+ amendments) | 2026-04-14; `ndexbio/project/architecture/review_log_network.md`; amended with `pending_lookups`, `replacement_edges`, `introduced_nodes`, `note_for_future_pass` fields |
| A3 bootstrap `rzenith-review-log` on local NDEx | ⏳ pending | part of "commit backfill diffs" task above |
| B1 paper-processor subagent spec | ✅ done | 2026-04-14 (separate session); `memento/workflows/BEL/subagent/{SUBAGENT.md, output_schema.json, README.md}`. Subagent is a prompt + tool allowlist, invoked via the `Agent` tool from a main agent; no new code. |
| B2 integration smoke test | ✅ done | 2026-04-14; invoked subagent on PMID 38200309 (Cho 2024). Discovered primary recovery path for known PMID→PMC mismapping defect: `search_pmc_fulltext(<title>)` successfully recovered correct PMCID (PMC10794148) after `get_pubmed_abstract` returned wrong one (PMC7515726 → Skrajna 2020). Extracted 9 BEL statements, 2 freeform claims, 5 unresolved entities. Output saved at `memento/workflows/BEL/subagent/examples/cho2024_PMID38200309.json`. Two design updates fed back into SUBAGENT.md: explicit `search_pmc_fulltext` recovery step + strict field-name requirements (subagent drifted on `claim`/`text`, `attempted_namespace`/`suggested_namespace` in first run). |
| B3 wire into rzenith review protocol | ✅ done | 2026-04-14; `rzenith/CLAUDE.md` Curation Review Protocol step 2 expanded with explicit paper-processor invocation + schema validation + analysis-network persistence steps. `workflows/BEL/SKILL.md` gains a "Subagent for full-paper extraction" section pointing at the spec. Actual first live invocation happens when the post-lock backfill commit executes (see A2 commit task). |
| C1-C3 BEL → GO-CAM translator | ⏳ pending | independent of B |
| D1 first systematic review pass | ⏳ pending | depends on A commit + B |
| D2 cadence policy | ⏳ ongoing | tune as we observe behavior |
| E* later work | deferred | see `deferred_tasks.md` |

---

## Session log

- 2026-04-14: plan created during infrastructure-verification session; BEL SKILL.md drafted (A1); decisions §1-6 locked in.
- 2026-04-14 (continued): A1 reference files complete (bel-grammar, namespace-policy, bel-examples, bel-to-gocam-mapping stub). A2 SHARED.md and rzenith/CLAUDE.md updated with provenance schema + curation review protocol. A3 review-log network spec documented. Phase A ~90% complete.
- 2026-04-14 (continued): A2 backfill dry-run on 3 v1.1 KB edges (cGAS→STING, MRE11→cytosolic-DNA, PARP1→genomic-instability). Successfully exercised protocol including split, qualify+split-add+consult, retire-and-replace dispositions. Surfaced and applied 5 protocol amendments: `superseded_by` field, compound-action language, new-node provenance, `pending_lookups` tracking, `note_for_future_pass` field. Two deferred issues logged: second-messenger representation (cGAMP localization specificity), local-store WAL recovery after killed concurrent writer. Proposed live-KB diffs captured in session transcript, awaiting DB-lock resolution to commit. Phase A complete pending commit. Phase B handed off to a fresh session per user instruction.
- 2026-04-15: rgiskard aligned to Phase B conventions. `memento/agents/rgiskard/CLAUDE.md` fully rewritten: explicit BEL authoring discipline + Edge Provenance Schema tie-in, paper-processor subagent as the tier-3 read path, inbound-consultation protocol for curator→researcher requests, seed mission removed. New `Working Model` section defines a fifth self-knowledge network (`rgiskard-domain-model`) — a lighter-provenance research substrate with node types `entity` / `expectation` / `pattern` / `puzzle` / `claim`, BEL relations for mechanism edges, and meta-edges `consistent_with` / `contradicted_by` / `informs` / `graduated_to`. PUBLIC, self-bootstrapped on first session, capped at 3-5 updates per session as a bookkeeping-bloat forcing function. Preserves tension rather than silently resolving contradictions. Rationale in session discussion: researcher agents need persistent interpretive memory that differs from curator agents' KG discipline — expectations and patterns belong in the graph alongside defensible claims. `agents/SHARED.md` § Knowledge Representation gained a "Formal and freeform representations are complementary" subsection making the BEL/freeform duality an explicit design stance rather than a fallback. Companion paper note at `ndexbio/paper/notes_formal_freeform_duality.md` captures the argument and proposes a testable hypothesis (representational consistency across sources → better agent reasoning when chunks are loaded into context). Validation via a one-shot scheduled task (`rgiskard-phase-b-alignment`), analogous to `rzenith-phase-b-exercise`.
- 2026-04-14 (continued, fresh session): Phase B B1-B3 completed. Paper-processor subagent designed as a prompt + tool allowlist (no new code) co-located with the skill it applies at `memento/workflows/BEL/subagent/`. B2 smoke test on PMID 38200309 (Cho 2024) validated the design end-to-end AND surfaced the primary recovery path for the known PMID→PMC mismapping defect: `search_pmc_fulltext(<title>)` recovered the correct PMC record (PMC10794148) after `get_pubmed_abstract` returned the wrong one (PMC7515726 mapped to Skrajna 2020). The subagent detected the title mismatch, recovered independently, and the full trail was preserved in `verification_warnings`. Two design refinements fed back into the spec: explicit `search_pmc_fulltext` recovery chain and strict field-name requirements (validated against `output_schema.json`) after the first-run subagent drifted on `text`/`claim` and `suggested_namespace`/`attempted_namespace`. B3 wired the subagent into rzenith's review protocol (`rzenith/CLAUDE.md` step 2) with explicit invocation, schema validation, and analysis-network persistence pattern. A new open issue surfaced: the pubmed MCP's PMID→PMCID mapping defect is now a known operational hazard — callers rely on the subagent's verification step to catch it. See deferred_tasks.md for tracking (to be added).
