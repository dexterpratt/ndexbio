# Deferred Tasks & Known Issues

Scratch list of things we don't want to forget but aren't worth formalizing into a plan during active exploration and incremental development. Append freely; prune when resolved.

**Related structured plan:** `rzenith_curation_and_bel_plan.md` — phased work plan for rzenith curator evolution, BEL authoring, GO-CAM view, paper-processor subagent. Items in that plan are not duplicated here; this file is for everything else.

---

## Dormant agents — fix before reactivating

As of 2026-04-14, only **rgiskard** and **rzenith** are active. The following three agents exist in `memento/agents/` and have scheduled-task scaffolds in `~/.claude/scheduled-tasks/`, but are dormant and have rot that must be cleaned up before any attempt to schedule or run them.

### drh, rdaneel, janetexample

**Status:** dormant since ~March 19, 2026. SKILL.md path references to `ndexbio/agents/` were patched to `memento/agents/` on 2026-04-14, but the files still have other issues.

**Known issues to fix before reactivation:**

1. **`config.yaml` references are dead** — each SKILL.md has a step reading `memento/agents/<agent>/config.yaml`, but those files don't exist in the memento repo (only `CLAUDE.md` is present). Either create the config.yaml files or remove those steps.

2. **`self_knowledge_specs.md` reference is dead** (drh-session only) — SKILL.md references `ndexbio/demo_staging/self_knowledge_specs.md` which no longer exists anywhere.

3. **Legacy protocol duplication** — the SKILL.md files inline session-lifecycle steps that are now canonically in `memento/agents/SHARED.md`. The rzenith and rgiskard SKILL.md files use a clean delegation pattern ("read CLAUDE.md + SHARED.md, follow the lifecycle there"). drh/rdaneel/janetexample should be rewritten to match that template.

4. **Profile choice decision** — rzenith and rgiskard scheduled tasks use `local-<agent>` profiles (local NDEx server, 127.0.0.1:8080). The legacy SKILL.md files assume the public NDEx (`profile="<agent>"`). Decide which server each agent targets before reactivating.

5. **No self-knowledge networks on local NDEx** — if these agents are reactivated against the local server, they'll need to bootstrap `<agent>-plans`, `<agent>-session-history`, `<agent>-collaborator-map`, and `<agent>-papers-read` networks first (rzenith and rgiskard both went through this process manually).

### rgiskard

**Status (2026-04-14):** SKILL.md scaffold created at `~/.claude/scheduled-tasks/rgiskard-session/SKILL.md`, modeled on rzenith's. **Not yet registered as a recurring scheduled task.** When ready to enable, register via `mcp__scheduled-tasks__create_scheduled_task` — suggest ~08:37 PT daily (offset from rzenith's ~09:19 PT so they don't compete for local NDEx or tool permissions).

---

## Infrastructure bugs / friction points

(Surfaced during 2026-04-14 verification. Not yet fixed.)

- **Scheduled-task PubMed/WebFetch calls blocked by permission prompt** — today's rzenith run died at `mcp__pubmed__search_pubmed` with "Tool permission stream closed before response received". Need to figure out the allowlist / `settings.json` config so scheduled agents can use external MCP tools autonomously. This currently blocks any research-heavy scheduled session. (Discussed in 2026-04-14 session; TBD.)

- **Session finalization on crash** — when a scheduled session aborts mid-flight, no `session-N` node gets written to session-history. Agent protocols currently finalize only at clean end. Consider: write a partial `session-N` node early and update at end, or wrap work in try/finally pattern so crashes still leave a trace.

- **`set_network_visibility` MCP flow** — creating a network on local NDEx still requires a follow-up `PUT /v2/network/{uuid}/systemproperty` to set visibility=PUBLIC. Known issue; no root-cause fix yet.

- **Boolean coercion bug** — `False → "False" → truthy` on MAP property round-trip through LadybugDB.

- **`_wait_for_valid` silent failure** — after 30s timeout, returns without raising. Should raise.

- **CX1 vs CX2 format inconsistency** — some network reads return CX2 (dict), others CX1 (array of aspect blocks). `local_store/cx2_import.py` normalizes this; external consumers still have to branch.

- **ToolSearch round-trip per scheduled run** — each scheduled session has to call `ToolSearch` to load deferred `mcp__local_store__session_init` schema before calling it. Minor latency cost, not blocking.

- **Local store single-writer lock (same-agent concurrency)** — LadybugDB takes an exclusive lock on `~/.ndex/cache/<agent>/graph.db` at open time. This blocks EVEN READS from a second client, so two processes touching the same agent's cache will collide (observed 2026-04-14 with rzenith in a parallel session). Cross-agent (rzenith vs rgiskard) is fine because each has its own cache dir. Same-agent collisions will hit when: (a) scheduled rzenith is running and the interactive session wants to inspect rzenith's state, (b) two interactive sessions both use `store_agent="rzenith"`, (c) overlapping scheduled runs if cron jitter aligns. **Mitigated 2026-04-17 via per-agent `--agent-scope` MCP server entries** (see `memento/project/architecture/local_store_lock_isolation.md`): each scheduled task now uses its own scoped `local_store_<agent>` entry that rejects calls for other agents before opening the database, preventing cross-session lock contention. Interactive multi-agent queries via the unscoped `local_store` entry can still collide with running scheduled tasks — long-term fix (Option B open/query/close, or WAL mode) remains future work.

- **WAL recovery blocks current MCP after concurrent-writer kill** — when a second process holding the lock is killed (rather than cleanly closing), it leaves a `graph.db.wal` file. The surviving MCP server's persistent connection then cannot recover or flush this WAL, and subsequent ops (including reads) fail with the same lock error even when only the surviving MCP holds a handle. Workaround: restart Claude so the MCP server opens fresh. Proper fix: MCP client should detect the condition and reopen, or LadybugDB should be configured to auto-recover WAL on subsequent open. Surfaced 2026-04-14 during the A2 backfill smoke test.

- **PubMed MCP PMID→PMCID mismapping defect** — `get_pubmed_abstract(pmid)` returns a `pmcid` / `doi` pair that does not always correspond to the requested PMID. Confirmed 2026-04-14 on PMID 38200309 (Cho 2024 *Nature*, MRE11→cGAS), where the tool returned PMCID PMC7515726 / DOI 10.1093/nar/gkaa544 — those map to Skrajna 2020 *NAR* ("Comprehensive nucleosome interactome screen..."), an apparently *cited* paper, not the requested one. Using that PMCID with `get_pmc_fulltext` silently yields the wrong paper. **Operational mitigation in place**: the paper-processor subagent (`memento/workflows/BEL/subagent/SUBAGENT.md` §3) verifies PMC title against the PubMed title, and recovers via `search_pmc_fulltext(<title>)` when they mismatch. Any other caller that reads PMC full text via a PMID should do the same check. **Root-cause fix**: investigate `tools/pubmed/` — suspect an NCBI ELink traversal bug or an accidental "cites" link being followed. Surfaced 2026-04-14 during Phase B B2 smoke test.

- **BEL representation of second-messenger specificity** — BEL statements like `a(CHEBI:"2',3'-cGAMP") directlyIncreases act(p(HGNC:STING1))` are technically true but oversell causality. Second messengers (cGAMP, cAMP, cGMP, Ca²⁺, IP3, DAG) are broadly diffusible; specificity comes from spatial compartmentalization (AKAPs, microdomains, scaffolds), local phosphodiesterase activity, transport (e.g., cGAMP via SLC19A1, LRRC8, gap junctions), pulsatile dynamics, and effector affinity thresholds. Upregulating the messenger does not uniformly activate every downstream effector it *could* bind. The cGAMP-specific literature on localization/transport is still evolving. Open questions: (a) should every second-messenger edge carry a mandatory `context` or `compartment` annotation? (b) can BEL's `loc()` qualifier express "intracellular cGAMP at ER" vs "extracellular cGAMP"? — partial yes, doesn't capture temporal dynamics; (c) are there emerging GO-CAM or BEL conventions for this case? Concrete action: once curation pattern accumulates, write a `second-messenger-authoring.md` note in `memento/workflows/BEL/reference/` with the standing conventions. Until then, every second-messenger edge gets a scope annotation flagging localization/transport caveats. Surfaced 2026-04-14 on cGAS→cGAMP→STING edge during A2 backfill.

---

## Potential tasks (not yet started)

- **Phase 4 analytics pipeline** — cross-agent consultation metrics on local NDEx (15+ networks, 2 active agents, 1 confirmed thread).
- **rgiskard Session 4 (manual or scheduled)** — integrate rzenith's response + KB v1.1 into mechanism map V2.
- **agent-hub-dev verification** — confirm the consultation thread renders correctly in the browser webapp.
- **Docker snapshot** — freeze current local NDEx state for reproducibility.
- **Partial cache reload** — skip re-download in `session_init` if NDEx mod time unchanged.
- **Promote common properties to indexed columns** (status, priority, evidence_tier) in local_store graph schema to avoid Python post-filtering.
- **Memory UUID refresh** — prior session memory doc lists stale UUIDs from pre-restart state (e.g. rzenith expert response `5f526030-369f-*` vs actual `3b07a1ba-36f1-*`). Update or annotate when convenient.

---

## Log

- 2026-04-14: file created during infrastructure verification session.
- 2026-04-14: global allow list expanded in `~/.claude/settings.json` to add `mcp__pubmed__*` and `mcp__local_store__*` — unblocks the PubMed permission crash that killed today's scheduled rzenith run.
- 2026-04-14: rgiskard scheduled-task SKILL.md scaffold created (not yet cron-registered); drh/rdaneel/janetexample SKILL.md files had `ndexbio/agents/` → `memento/agents/` path patches but still carry other rot documented above.
- 2026-04-14: BEL SKILL.md drafted at `memento/workflows/BEL/SKILL.md`. Structured plan for rzenith curator evolution + BEL integration created at `ndexbio/project/rzenith_curation_and_bel_plan.md`.
- 2026-04-14: Phase A backfill dry-run completed (3 edges); 5 protocol amendments applied to SHARED.md, rzenith/CLAUDE.md, and review_log_network.md. Two deferred infra issues logged (WAL recovery, second-messenger representation). Phase B (paper-processor subagent) handed off to a fresh Claude session for context preservation.
