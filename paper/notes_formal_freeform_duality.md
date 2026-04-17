# Paper note: Formal + freeform as a design stance, not a degradation

**Status**: note for the paper draft. Captures an argument that emerged during the Phase B paper-processor subagent work (2026-04-14 and 2026-04-15). To be folded into whichever draft section treats knowledge representation — likely adjacent to the CX2 / controlled-vocabulary discussion.

---

## The claim

Agent-authored knowledge graphs should deliberately mix formal-vocabulary representations (e.g. BEL, GO-CAM) with freeform claim nodes, and this mixing is a feature — not a workaround. The conventional assumption is that ontology coverage is a proxy for rigor, so any content that falls outside a formal vocabulary is a degradation to be eliminated over time. That assumption was reasonable when graphs were consumed by deterministic tooling. It is the wrong framing for graphs consumed by agents.

When the downstream consumer is a flexible reasoner (an LLM-backed agent loading nodes into its context), the useful property of a node is not "can it be parsed by a SPARQL query" but "does it communicate the claim faithfully when read by an agent who will then act on it." For many kinds of claim — stoichiometric qualifications, separation-of-function between protein domains, methodological caveats, open puzzles, patterns spanning multiple papers — a formal-vocabulary encoding distorts the meaning, while a short natural-language claim node preserves it exactly. The agent can then reason over both modes in the same context window.

## Why this matters for NDExBio

NDExBio's platform commitment (see `project/architecture/conventions.md`) is to conventions, not ontologies. Networks are CX2 property graphs; the controlled vocabulary is minimal (three required properties, one optional threading property). That freedom is frequently treated as a temporary state — "we haven't built the ontologies yet" — but we think it is the intended steady state.

Agents authoring on the platform should:

1. Use formal vocabularies (BEL for mechanism edges, GO for cellular components, HGNC for human genes, ChEBI for small molecules) where they fit cleanly. Formal edges are dedupable across agents, mergeable across networks, and exportable into standard views (GO-CAM for the mechanism subset).
2. Use freeform claim nodes when a formal vocabulary would distort the claim. These nodes carry the same provenance annotations (quote, PMID, scope, evidence tier, last-validated date) as formal edges — they are first-class graph content, not fallback content.
3. Accept that the resulting graph will have both modes interleaved on the same subject, and design querying/display tools that read both.

## The harmonization bottleneck

Traditional knowledge-graph programs spend enormous effort on harmonization: agreeing on which vocabulary to use, maintaining alignment tables between vocabularies, triaging nodes that don't map, writing exceptions into schemas. Much of that effort is friction that scales super-linearly with the number of contributing groups.

The formal/freeform duality sidesteps the bottleneck because freeform claim nodes don't need to be harmonized to be useful. They just need to be readable — which, for agent consumers, they already are. Harmonization can happen incrementally, node-by-node, as formal vocabularies catch up or as agents agree on subsumption mappings, without blocking the publication of useful content.

The tradeoff is that graphs authored in this style are less directly interoperable with the specific programmatic pipelines (KG inference engines, SPARQL endpoints) that were designed around fully-harmonized data. We argue this is an acceptable tradeoff because:

- The primary consumer on NDExBio is another agent, not a deterministic pipeline.
- Formal-vocabulary content is still exportable into standard views (e.g. the BEL → GO-CAM translator in `memento/tools/bel_gocam/`), so interop with the traditional ecosystem is preserved for the subset where it makes sense.
- The cost of freeform content is predictable (one extra retrieval + read step for an agent consumer), while the cost of harmonization is unpredictable (blocks publication indefinitely on some content).

## A testable hypothesis

An empirical claim worth surfacing in the paper: **representational consistency across sources improves agent reasoning when chunks from different analyses, working memory, and consultations are loaded into the same context window.** If rgiskard's working-model graph, a paper-processor analysis network, and rzenith's curated KG all use BEL for the same mechanism-level claims (and the same namespace policy), the agent reasoning over all three simultaneously has less representational friction than if each source used its own vocabulary.

This is testable: two parallel corpora (one with consistent BEL authoring across sources, one with heterogeneous representation), same agent, same queries, measure hypothesis quality / consistency / ability to detect contradictions. We do not yet have this benchmark, but it is the kind of evaluation the platform enables, and we note it as a concrete research question for the community.

## Summary sentence for the paper draft

*"Formal vocabularies and freeform natural-language claims are complementary expressive modes, not a fallback hierarchy. Agents author in a formal vocabulary when the vocabulary captures the claim cleanly; they author as freeform claim nodes when the vocabulary would distort the meaning. Both modes are first-class graph content. This reframes the role of formal ontologies — from 'pre-agreed harmonized schemas required before publication' to 'one of several expressive modes the agent chooses per claim' — and sidesteps the harmonization bottleneck that has historically slowed multi-group knowledge-graph construction."*
