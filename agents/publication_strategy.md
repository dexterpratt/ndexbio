# Publication Strategy: NDEx Agent Scientific Community

## Paper 1: arXiv Preprint (target: rapid)

### Working Title
"Scientist Agents on Shared Infrastructure: Emergent Scientific Community Dynamics via Persistent Knowledge Artifacts on NDEx"

### Pitch
We demonstrate that LLM-based scientist agents, operating autonomously on a shared biological network platform (NDEx), self-organize into a productive community — extracting structured knowledge from papers, publishing discoverable networks, citing and critiquing each other's work, and developing shared norms. Unlike prior multi-agent systems that communicate through chat, our agents exchange persistent, public, structured knowledge artifacts on existing scientific infrastructure, making their outputs immediately interoperable with thousands of human-curated biological networks.

### Scope (keep it tight)
- 5–10 agents, each processing a small set of papers from different biological subfields
- Agents publish networks to NDEx, discover each other's work, and produce critiques
- Run for enough cycles to observe emergent patterns (norm convergence, citation structure, community formation)

### Evaluation (Tier 1 only — no external benchmarks)
1. **Community network topology**: Analyze the citation/communication graph. Does it exhibit properties of real scientific communities (clustering, preferential attachment, subfield structure)?
2. **Norm emergence**: Track whether agents converge on shared quality standards for network extraction, consistent property usage, critique format conventions.
3. **Milestone completion**: What % of agents complete each workflow stage (read → extract → publish → discover peer work → critique → revise)?
4. **Knowledge accumulation**: Network count, citation density, provenance chain length over time.
5. **Artifact quality proxies**: Valid CX format, property completeness, provenance metadata coverage.

### What the paper does NOT need
- Ground truth expert annotations (save for Paper 2)
- Novel hypothesis discovery claims (save for Paper 3)
- Comprehensive benchmark suites
- Comparison against other multi-agent frameworks

### Structure
1. Introduction — the vision + why structured artifacts on shared infrastructure matter
2. Related work — Park et al. lineage, SciAgents, agent communication protocols
3. System design — NDEx as communication substrate, agent architecture, conventions
4. Experimental setup — agents, papers, activity cycles
5. Results — community dynamics, norm emergence, milestone completion, sample interactions
6. Discussion — what emerged, what didn't, limitations, roadmap
7. Conclusion — invitation to the community to deploy agents on NDEx

### Key argument
The shift from chat-based to artifact-based agent communication changes what's possible: persistent, public, structured, interoperable, citable outputs that accumulate into a knowledge commons. This is closer to how real science works than anything in the multi-agent chat literature.

---

## Paper 2: Follow-up (target: 3–6 months after Paper 1)

### Focus
Deeper evaluation with expert ground truth. One biologist curates reference networks for N papers. Measure precision/recall of agent-extracted networks. Assess whether critiques improve quality. Qualitative case studies of interesting emergent interactions.

### New evaluation elements
- Expert-annotated ground truth comparison
- Critique impact measurement (does revision improve quality?)
- Detailed case studies of multi-agent knowledge synthesis
- Scale to 50+ agents, 100+ papers

---

## Paper 3+: Emergent topics (6+ months)

Candidate directions — let the system's behavior determine which are most compelling:
- Novel hypothesis generation across subfields
- Contradiction detection between published findings
- Living knowledge graphs that evolve with new evidence
- Open participation: other groups deploy agents, community grows organically
- Comparison of agent community dynamics to real scientific community dynamics (e.g., using bibliometric data)

---

## Strategic Notes

**Speed over perfection for Paper 1.** The goal is to plant the flag — show the concept works, the infrastructure exists, and interesting things happen. The community will be drawn by the vision and the open platform, not by exhaustive benchmarks.

**The NDEx differentiator is the paper's core contribution.** Every other multi-agent system uses chat. We use a real scientific data platform. This is not incremental — it changes what agents can do (discover, cite, extend, critique structured knowledge) and what evaluation looks like (network topology, norm emergence, knowledge accumulation).

**Avoid the evaluation trap.** The literature shows that elaborate evaluation frameworks often delay publication without proportionally increasing impact. Tier 1 metrics are sufficient for a well-positioned arXiv preprint. Deeper evaluation strengthens Paper 2.

**Citation anchors**: Park et al. 2023 (generative agents), Cheng et al. 2025 (emergent social networks), SciAgents 2025 (scientific agent workflows), Architecture-Aware Metrics 2026 (evaluation philosophy).
