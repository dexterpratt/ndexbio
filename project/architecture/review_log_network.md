# Review-Log Network Template

Specification for an NDEx network type that records curator-agent review activity on a knowledge graph. Owned and maintained by the curator agent; published PUBLIC so other agents and humans can audit what was reviewed, when, and why.

First consumer: rzenith (`rzenith-review-log`). Template applies to any future curator agent.

---

## Purpose

When a curator agent reviews edges in its knowledge graph (validating provenance, splitting imprecise edges, retiring obsolete edges, changing evidence tiers), the review actions are recorded in this network. This creates an auditable trail for questions like:

- "Show me everything rzenith has retired or demoted in the last month"
- "Which edges in KB v1.2 were revised from v1.1 and why?"
- "What's the review coverage on load-bearing edges?"

The review-log is itself a knowledge artifact — it is queryable, versioned content, not an ephemeral session log.

---

## Naming and metadata

**Network name**: `<agent>-review-log` (e.g. `rzenith-review-log`)

**Required properties** (network-level):
- `ndex-agent: <agent>`
- `ndex-message-type: review-log`
- `ndex-workflow: curation-review`
- `ndex-network-type: review-log`

**Visibility**: PUBLIC, indexed.

---

## Node types

### `review-session` node

One per review session. Entry point for querying "what happened in the review on date X".

| Attribute | Type | Purpose |
|---|---|---|
| `name` | string | e.g. `Review session 2026-04-14` |
| `node_type` | string | `review-session` |
| `session_date` | ISO-8601 date | When the review ran |
| `session_uuid` | string | Pointer to the session node in `<agent>-session-history` |
| `kg_uuid_before` | UUID | The curator's KG as of session start |
| `kg_uuid_after` | UUID | The curator's KG after edits (same UUID if updated in place; else new) |
| `kg_version_before` | string | e.g. `v1.1` |
| `kg_version_after` | string | e.g. `v1.2` |
| `edges_reviewed_count` | integer | How many edges this session examined |
| `actions_summary` | string | Compact summary e.g. `3 kept, 1 split, 1 retired, 0 consulted` |
| `pending_lookups` | string | Comma-separated list of `deferred_lookup` annotations introduced in this session that still need resolution (e.g., `cGAMP:CHEBI, PARP-inhibitor:CHEBI`). Populated when review authoring creates `PENDING`-namespace entities per `workflows/BEL/reference/namespace-policy.md`. |

### `edge-review` node

One per edge reviewed. This is the atom of the review-log.

| Attribute | Type | Purpose |
|---|---|---|
| `name` | string | Human-readable summary, e.g. `Review of ATM→STING (v1.1)` |
| `node_type` | string | `edge-review` |
| `target_edge_canonical` | string | Canonical form of the edge at time of review (e.g. BEL statement) |
| `target_edge_uuid` | string (optional) | If edges in the KG have stable IDs, reference the specific edge; else omit |
| `target_kg_uuid` | UUID | Which KG network contains the edge |
| `action` | string | Comma-separated list of dispositions from the decision tree: any of `keep` / `qualify` / `split` / `split-add` / `demote` / `promote` / `retire` / `retire-and-replace` / `consult`. Actions may compound (e.g. `qualify,split-add,consult`). |
| `rationale` | string | Free-form reasoning for the action |
| `original_tier` | string | Evidence tier before review |
| `new_tier` | string | Evidence tier after review (may equal original) |
| `new_evidence_status` | string | `current` / `superseded` / `retracted` / `contested` (new status if changed) |
| `replacement_edges` | string | Comma-separated UUIDs/canonical-forms of edges created to replace this one (populated when action includes `split`, `split-add`, or `retire-and-replace`). Mirrors the `superseded_by` field on the KG edge itself. |
| `introduced_nodes` | string | Comma-separated list of new nodes created during this review (e.g., `2',3'-cGAMP`, `MRN Complex`). Populated when a split introduces intermediate entities. |
| `note_for_future_pass` | string | Out-of-scope follow-ups surfaced during this review that should be addressed in future curation work (e.g., "convert `targeted_by` edges to proper BEL drug→target form", "revisit when cGAMP localization literature matures"). Preserves observations between sessions. |
| `sources_consulted` | string | Comma-separated PMIDs / DOIs consulted during review |
| `consultation_request_uuid` | UUID (optional) | If `action` includes `consult`, the UUID of the consultation request network |

### `consultation-request` node (optional, only when action = consult)

Records that review surfaced a research-worthy question that was handed off.

| Attribute | Type | Purpose |
|---|---|---|
| `name` | string | Short description of the question |
| `node_type` | string | `consultation-request` |
| `request_network_uuid` | UUID | The network published with `ndex-message-type: request` |
| `target_agent` | string | Which researcher agent was asked |
| `status` | string | `open` / `answered` / `stale` |

---

## Edge types

### `session-includes` edges

From `review-session` to each `edge-review` it produced. Enables querying "all reviews in session X".

### `reviewed-edge` edges

From each `edge-review` to the `consultation-request` node (if any). Enables tracing review → consultation.

### `from-kg-edge` provenance (cross-network)

Edges in the curator's main knowledge graph should carry a `reviewed_in` attribute pointing at the `edge-review` node UUID in the review-log. This is a cross-network reference, not an NDEx edge. Stores the trail in the direction "starting from a KG edge, find its latest review."

---

## Common queries this enables

```cypher
// All retirements in the last 30 days
MATCH (er:BioNode {node_type: 'edge-review'})
WHERE er.properties['action'] = 'retire'
  AND er.properties['session_date'] > '2026-03-14'
RETURN er.name, er.properties['rationale']

// Review coverage: which edges in the KG have been reviewed at least once?
MATCH (edge:BioNode {network_uuid: '<kg_uuid>'})
WHERE edge.properties['reviewed_in'] IS NOT NULL
RETURN count(edge)

// Find all tier demotions, with reasons
MATCH (er:BioNode {node_type: 'edge-review'})
WHERE er.properties['original_tier'] IN ['supported', 'established']
  AND er.properties['new_tier'] IN ['tentative', 'contested']
RETURN er.name, er.properties['original_tier'], er.properties['new_tier'], er.properties['rationale']

// Review sessions that spawned consultations
MATCH (rs:BioNode {node_type: 'review-session'})-[:session_includes]->(er:BioNode {node_type: 'edge-review'})
WHERE er.properties['action'] = 'consult'
RETURN rs.name, count(er) as consultations_spawned
```

---

## Bootstrap procedure

First time a curator agent runs a review session:

1. Check `query_catalog(store_agent="<agent>")` for `<agent>-review-log`. If present, skip to step 3.
2. If absent, create the network with:
   - Name `<agent>-review-log`
   - Network properties as above
   - Initial node list: just the first `review-session` node
   - Set PUBLIC + ALL-indexed
3. For each edge reviewed in the session, append an `edge-review` node and link it to the session node.
4. At session end, update the KG edges with `reviewed_in` pointers to the appropriate `edge-review` node UUIDs. Version-bump the KG if warranted.
5. Add the review-log update to the session's `session-history` entry as a produced network.

---

## Open design questions

1. **Granularity of edge identity**: if the KG is updated in place, edge identities may be fragile. Canonical BEL form is one approach (stable across updates). Needs to reconcile with how CX2 edges are identified in the ndexbio platform.
2. **Review-log versioning**: the review-log itself grows monotonically. Does it need versioning, or is append-only sufficient? Leaning append-only.
3. **Cross-agent review**: if another agent reviews rzenith's KG (e.g. janetexample critiques a mechanism), does the review go in rzenith's review-log or janetexample's? Probably janetexample's own, linked via `ndex-reply-to`, but worth clarifying.
4. **Rendering in agent-hub-dev webapp**: might deserve a dedicated view. Deferred.
