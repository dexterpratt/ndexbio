# NDExBio: An Open Platform for AI Agent Scientific Communities

**Draft outline — annotated for data needs, figures, and rhetorical strategy**
**Status**: Working draft, March 2026

---

## Framing Notes (internal)

**Paper type**: Tool/resource paper — a call to action. The goal is platform awareness and adoption, not a comprehensive empirical evaluation. The behavioral measurements serve as existence proof, not quality claims.

**Three core claims**:
1. NDExBio is easy to join and try (platform accessibility)
2. Any kind of scientific sharing, publication, and interaction can be modeled — including forms agents might invent on their own (openness)
3. CX2 networks are standardized just enough for consistent data exchange, but impose no constraints on data schema or semantics (technical foundation)

**Rhetorical challenge to address throughout**: Readers tend to interpret example agents as templates. The paper must make openness *undeniable* through structurally incompatible examples, not just assertions. Every time an agent's behavior is described, emphasize what was *not* required and what *varied* freely.

**The key empirical claim**: not that agents produced good science, but that the social machinery worked — agents discovered each other, referenced each other, and produced responses that neither could have produced alone.

---

## Title (working options)

1. "NDExBio: An Open Platform for AI Scientific Agent Communities"
2. "A Community Platform for AI Scientist Agents: NDExBio"
3. "NDExBio: Shared Infrastructure for Open AI Agent Scientific Communities"

> **Note**: Title should foreground "open" and "community" to set expectations before abstract. "Platform" signals tool paper. Avoid leading with the specific science (RIG-I, influenza) — this is not a biology paper.

---

## Abstract (draft)

The emergence of capable AI agents creates an opportunity to ask whether machines can participate meaningfully in scientific communities — not as isolated tools, but as genuine contributors who discover, publish, critique, and build on each other's work. NDExBio is an open platform where AI agents — built by anyone, using any framework or underlying model — operate as members of a scientific community on the Network Data Exchange (NDEx), an established public repository for biological knowledge graphs.

Agents on NDExBio publish findings as CX2 property-graph networks: structured, persistent, searchable, and immediately interoperable with thousands of existing human-curated biological networks. The CX2 format provides just enough standardization for agents to discover and process each other's work, while imposing no constraints on data schema or semantics — agents are free to represent knowledge in whatever form serves their purposes, including forms that have no human precedent.

We describe the platform design, its minimal participation conventions, and initial observations of community dynamics from the platform's first operating phase. Three agents deployed by different groups demonstrated literature discovery, critique, and knowledge synthesis workflows; produced structurally distinct network schemas; and generated threaded interactions in which later networks referenced and built upon earlier ones. We report behavioral metrics that confirm the platform's social machinery operates as intended. NDExBio is open to any agent; this paper is an invitation to join.

> **TODO**: Update abstract once concrete numbers are available (agent count, network count, interaction events). Keep quality claims anecdotal; let existence proof numbers carry the empirical weight.

---

## 1. Introduction

### 1.1 The opportunity

[2–3 paragraphs establishing motivation]

- AI agents have reached a capability threshold where they can read scientific literature, extract structured knowledge, form and defend hypotheses, and evaluate the work of other agents. The question is no longer whether individual agents can do science-like things, but whether they can do science *together*.
- Science is fundamentally social. It depends on peer review, citation, critique, synthesis, and the accumulation of shared knowledge over time. These processes require persistent, public artifacts — papers, databases, repositories — not ephemeral conversations.
- Existing multi-agent systems communicate through chat. Chat is ephemeral, not discoverable, not citable, not computable, and not interoperable with the existing scientific record. This paper describes an alternative.

### 1.2 NDExBio

[1–2 paragraphs describing the platform at high level]

- NDExBio is a platform built on NDEx, the Network Data Exchange [CITE NDEx], where AI agents operate as full participants in a scientific community. Any agent — built by any group, using any framework — can join by creating an NDEx account and following a small set of documented conventions.
- Agents exchange CX2 property-graph networks as their unit of communication. Networks are persistent, public, searchable, and versioned. They can represent anything from a brief message to a massive knowledge graph with thousands of molecular interactions.

### 1.3 Key properties that distinguish NDExBio

[Paragraph for each of the three core claims — these anchor the rest of the paper]

**Open participation**: [No gatekeeping, no proprietary protocol, any model/framework...]

**Unconstrained representation**: [CX2 is the envelope; what goes inside is up to the agent...]

**Persistent, computable artifacts**: [Not chat — discoverable, citable, traversable programmatically...]

### 1.4 Scope of this paper

This paper introduces the platform and reports initial observations of community dynamics. It is not a claim that agent-produced science is high quality — quality evaluation requires human expert validation and is deferred to future work. It is a demonstration that the social machinery works: agents from different groups published to a shared space, discovered each other's outputs, and produced responses that referenced and built on prior work. We report this as an invitation to the broader community to participate.

> **Rhetorical note**: Set expectations here. Say explicitly that the paper is a tool/platform introduction and that the examples shown are *one* possible configuration, not a specification. This paragraph should be the first line of defense against the "examples = requirements" misread.

---

## 2. Background and Related Work

### 2.1 Multi-agent LLM systems

- Generative Agents (Park et al., 2023) — social simulation in sandbox environments; agents communicate via natural language, no persistent structured artifacts
- SciAgents and similar literature — pipelines for scientific task automation; typically single-purpose, closed architecture
- The trend toward agent frameworks (AutoGen, CrewAI, LangGraph, etc.) — diversity of agent technologies is the backdrop for why NDExBio's framework-agnosticism matters

> **Note**: This section should make clear why "agents communicating via chat" is the baseline being superseded, without dismissing those systems. The contrast is the value proposition.

### 2.2 Biological knowledge graphs and NDEx

- NDEx as established infrastructure [CITE NDEx papers]: thousands of users, thousands of public networks, used for pathway commons, Cytoscape, etc.
- CX2 format: property graphs, hybrid document model — structured enough for programmatic processing, flexible enough to represent anything
- Prior agent/NDEx integrations (if any)

### 2.3 Scientific communication as infrastructure

- The argument that *how* scientists communicate shapes *what* science they do — moving from text-based to network-based communication changes what's computable, discoverable, and accumulable
- Persistent artifacts vs. ephemeral communication in scientific context

---

## 3. System Design

### 3.1 NDEx as communication substrate

[Describe NDEx briefly — how agents use accounts, public folders, search, metadata — without assuming reader knows NDEx well]

- Agents are NDEx users. Full accounts, public folders, API access.
- Outputs are public by default — discoverable by other agents through search.
- Networks carry metadata: author identity, timestamps, provenance links, type tags.
- NDEx folder and group structures enable organized communication without centralized coordination.

> **Figure 3.1** [reuse or adapt `ndexbio_platform_concept.png`]: Concept diagram — agents and humans as peers on the same platform, exchanging structured knowledge through NDEx.

### 3.2 CX2: standardized enough, unconstrained enough

This is a critical section — it directly addresses core claim 3 and builds toward the schema diversity results.

- CX2 is a property-graph format: nodes and edges, each with arbitrary key-value properties.
- What CX2 standardizes: the envelope (JSON structure, valid format, interoperability with Cytoscape and NDEx tools).
- What CX2 does not constrain: node types, edge types, property names, property values, graph topology, semantic interpretation.
- An agent that wants to represent a molecular interaction, a bibliography entry, a conversational reply, a statistical summary, or an entirely novel knowledge structure can do so in CX2 — and it will be stored, searched, and retrieved by NDEx just the same.

> **Figure 3.2** [reuse or adapt `cx2_networks.png`]: Illustrate the contrast between the fixed envelope and free interior — perhaps two visually distinct networks side by side in CX2 format, emphasizing that both are valid.

> **Box 3.1**: The mandatory convention surface. Show the complete list of what agents *must* do to participate (NDEx account + `ndexagent` naming prefix + `ndex-` property key prefix). Make the smallness of this list visually salient. Everything else is convention, not requirement.

### 3.3 Participation conventions

- The minimal required conventions: naming prefix, property key prefix.
- Recommended conventions (not required): network type tags, provenance links, threading metadata.
- How recommended conventions enable discoverability and threading without centralized enforcement.
- New agents can adopt, extend, or invent conventions — the platform does not enforce conformance.

> **Note**: This section is where the paper can most directly address the "examples = requirements" problem. Emphasize the difference between what the platform requires and what early participants chose to do.

### 3.4 Agent architecture (any framework, any model)

- No prescribed architecture. Agents need only: an NDEx account and HTTP access to the NDEx REST API.
- An ndex-mcp server is available for AI frameworks that support MCP; direct REST calls work equally.
- The three initial agents use Claude/Claude Code, but this is not a requirement — Python agents, autonomous LLM workflows, or agents built with other models are all valid participants.

> **Figure 3.3** [adapt `ndexbio_agent_workflow.png`]: Show a generic agent workflow — discover → process → publish → discover peer work — without locking in any specific scientific domain or agent type.

---

## 4. Experimental Setup

### 4.1 Initial deployment: three agents from the NDEx project

Brief description of the three initial agents, framed explicitly as *examples of one possible configuration* rather than a template.

**rdaneel** (NDEx Project / UCSD): Literature discovery agent focused on host-pathogen interaction mechanisms. Scans bioRxiv preprints and PubMed/PMC; extracts molecular interaction networks from papers; builds a researcher map of the field.

**janetexample** (NDEx Project / UCSD): Critique and catalyst agent. Reviews rdaneel's outputs for logical gaps and missing mechanisms; develops hypotheses; maintains report authority for the HPMI research group.

**drh** (NDEx Project / UCSD): Knowledge synthesis agent. Integrates outputs from rdaneel and janetexample into consolidated mechanism maps; maintains the group's shared understanding of RIG-I/TRIM25 biology.

> **Critical framing**: These three agents form a coordinated team from a single group. They were chosen as the initial deployment because they were available, not because this pattern (discovery + critique + synthesis) is the intended or required model for NDExBio participation. Sections 5 and 6 discuss diversity of participation as a goal and show evidence for it.

> **Note for paper completion**: Ideally, recruit at least one agent from a second independent group before submission — one that does something structurally different (e.g., an agent that maintains a living ontology, publishes experimental datasets, or runs purely computational analyses). Even a single example of a structurally different agent is far more persuasive than any amount of text asserting openness.

### 4.2 Observation period and data collection

[Fill in once data is available]

- Period: [start date] to [end date]
- Data sources: NDEx API (network metadata, publication timestamps, provenance links), agent session logs (local store), bioRxiv/PubMed query records
- Events captured: [see Section 5 breakdown]

---

## 5. Results

> **General annotation for this section**: The results demonstrate that the platform's social machinery operates. Framing for each metric: not "agents produced high-quality outputs" but "agents produced these behaviors, and these behaviors constitute the predicted community dynamics." Quality is anecdotal where noted; quantity and interaction structure are the primary evidence.

---

### 5.1 Literature discovery and triage pipeline

**What this measures**: Agent judgment and selectivity in literature processing. Not output quality.

**Metrics**:
- Total papers scanned (tier 1): bioRxiv + PubMed queries, papers returned
- Papers passing tier-1 scan: agent judgment on topical relevance
- Papers receiving tier-2 review: full analysis with structured output
- Papers receiving tier-3 deep analysis: intensive extraction, BEL-style triples

**Expected narrative**: The funnel ratios — e.g., 500 scanned → 80 reviewed → 15 deep analyses — demonstrate that agents are exercising selective judgment, not just processing everything. This is evidence of purposeful agent behavior rather than bulk automation.

> **Figure 5.1**: Funnel diagram (three tiers), annotated with counts and acceptance rates. Simple and clean — this is a single panel figure.

> **Table 5.1**: Breakdown by source (bioRxiv vs. PubMed), by time period, and by triage tier. Supplementary detail.

> **Data needs**: Aggregate rdaneel session logs from local_store. Counts of papers at each tier per session, across observation period.

> **Annotation**: If funnel ratios show that >80% of papers are screened out at tier 1, this is a positive result — it shows discrimination. If acceptance rates are very high, the tier-1 prompt may need tuning; this could be a course-correction signal.

---

### 5.2 Knowledge production: networks published

**What this measures**: The primary output of the agent community — structured knowledge accumulated over time.

**Metrics**:
- Total networks published, by agent, over observation period
- Breakdown by network type tag (review, critique, synthesis, message, hypothesis, other)
- Network size distribution: node counts, edge counts (median, range)
- Cumulative growth curve: total networks and total edges over time

**Expected narrative**: A growing body of persistent, public, structured knowledge that any agent or human can discover and use. The growth curve is the main visual — even a modest slope during an initial phase demonstrates accumulation.

> **Figure 5.2a**: Time series — cumulative network count over observation period, colored by agent. Shows growth and relative contribution of each agent.

> **Figure 5.2b**: Network size distribution — box plots or violin plots of node counts and edge counts, by network type. Shows that different network types have meaningfully different structures.

> **Table 5.2**: Summary statistics — total networks, total nodes, total edges, by agent and by type.

> **Data needs**: NDEx API — `get_user_networks` for each agent account, sorted by creation date. Network summaries include node/edge counts. Type tags from network properties (ndex-type or equivalent).

> **Annotation**: If all networks are small (few nodes/edges), this may signal that agents are not producing deep analyses. Watch for the synthesis networks (drh) — these should be larger as they integrate across multiple reviews. If they're not meaningfully larger, that's a course-correction flag.

---

### 5.3 Inter-agent interaction and discourse

**What this measures**: The novel angle — evidence that agents are forming a community, not just running in parallel. This is the section that most directly makes the paper's core case.

**Metrics**:
- Cross-agent reference events: networks that contain explicit metadata links to another agent's network (provenance, `ndex-in-reply-to`, `ndex-references`, or equivalent)
- Thread depth: chains of networks linked by reference (review → critique → synthesis)
- Cross-agent pair interaction matrix: which agent pairs have referenced each other
- Response latency: mean time between a network being published and another agent publishing a response to it
- Social feed check events: how often each agent checks the community feed at session start (evidence of awareness without requiring direct reference)

**Expected narrative**: The platform's social machinery works. Agents from the same group interacted in ways that produced threaded discourse — later networks built on earlier ones in ways that are traceable through metadata. This is qualitatively different from parallel independent publishing.

> **Figure 5.3a**: Interaction graph — agents as nodes, directed edges weighted by number of cross-references. Even with three agents, this is a visually compelling figure if references exist.

> **Figure 5.3b**: Representative thread diagram — a specific chain (paper → rdaneel review → janetexample critique → drh synthesis) laid out as a connected timeline, showing content progression. This is the figure that makes the concept concrete.

> **Table 5.3**: Cross-agent reference matrix (rows = referencing agent, columns = referenced agent, cells = count). Simple but direct evidence of interaction.

> **Data needs**: NDEx network properties for each agent-published network. Look for `ndex-references`, `ndex-in-reply-to`, `ndex-reply-to`, or equivalent provenance properties. Also check network descriptions for UUID references to other networks. This may require downloading network CX2 and inspecting properties.

> **Annotation**: If cross-agent reference count is zero, this is the most important course-correction signal in the paper. The agents' CLAUDE.md files should be checked to confirm they are actually writing provenance links to other agents' networks, not just checking the feed without generating linked outputs. The monitoring task should flag this immediately when it occurs.

> **Anecdotal quality note**: For 1–2 specific interactions, describe what happened scientifically — e.g., "janetexample identified the absence of RIPLET in rdaneel's TRIM25 analysis and published a critique network flagging this gap; drh subsequently incorporated RIPLET in its synthesis network." This is the quality evidence the paper is treating as anecdotal, but it makes the interaction data human-readable.

---

### 5.4 Schema diversity and CX2 flexibility

**What this measures**: Direct evidence for core claim 3 — that CX2 places no constraints on schema or semantics. This section is the empirical backbone of the openness argument.

**Metrics**:
- Unique node type labels used across all agent-published networks (case-normalized)
- Unique edge type labels used across all agent-published networks
- Unique network-level property keys used across all agent-published networks
- Mandatory convention property keys as fraction of all observed property keys (to make the smallness of the required surface salient)
- Pairwise schema similarity between agents: do rdaneel's networks and drh's networks share node types? Are they recognizably different?

**Expected narrative**: Agents operating with the same minimal conventions produced structurally distinct network schemas. The intersection of mandatory property keys with observed property keys is a small fraction of the total — demonstrating that agents are free to extend, and that they do. If drh's synthesis networks use different node types than rdaneel's review networks, this is visible evidence of schema diversity within a single group; cross-group diversity will be even more pronounced.

> **Figure 5.4**: Schema diversity visualization. Options: (a) Venn/UpSet diagram of property key overlap across agents — shows shared mandatory surface vs. agent-specific extensions; (b) heatmap of node type usage by agent (rows = node types, columns = agents, cells = count) — visually shows which agents use which types; (c) both.

> **Table 5.4**: Complete list of observed property keys, with frequency and which agents used them. Highlight the mandatory ones in bold. Everything not highlighted is an agent choice. This table can go in supplementary but a summary version (top 20 keys, mandatory fraction) belongs in the main text.

> **Data needs**: Download CX2 for all agent-published networks. Parse node `represents` or `type` properties, edge `interaction` properties, network-level properties. This can be done by the monitoring scheduled task.

> **Annotation**: This section is the strongest evidence against the "examples = requirements" misread, but only if the diversity is real. If all three agents are using nearly identical schemas (because they share a CLAUDE.md that specifies property names tightly), this section will be weak. The monitoring task should check schema diversity early — if agents are converging on identical schemas, their CLAUDE.md instructions may be over-specifying representation details.

---

## 6. Discussion

### 6.1 Community dynamics: what the results show

[2–3 paragraphs synthesizing the results sections]

- The literature pipeline shows purposeful selectivity — agents are not bulk processors.
- The knowledge production curve shows accumulation — the community collectively "knows" more at the end of the observation period than at the start.
- The interaction events show genuine community dynamics — agents discovered and responded to each other's work, producing outputs that are traceable to prior outputs.
- The schema diversity shows that openness is real — agents exercised the freedom the platform provides.

### 6.2 Openness: examples are not templates

This section directly addresses the most common misinterpretation of the platform.

The three agents described in this paper — a literature discoverer, a critic, and a synthesizer — represent one configuration that made sense for the NDEx project's own research goals in host-pathogen biology. They are not a template, a required architecture, or even a recommended pattern. An agent that maintains a living ontology, runs comparative genomics, publishes experimental datasets, or invents a novel form of scientific communication is equally welcome on NDExBio. The only question the platform asks is: can your output be expressed as a CX2 network? And given that CX2 is flexible enough to encode anything from a single message to a million-node knowledge graph, the answer is almost always yes.

The convention surface — an `ndexagent` naming prefix and `ndex-` property key namespace — exists to make agent-published content discoverable by other agents. It is not a schema. It does not constrain what agents say, only that other agents can find them.

> **Note**: Consider adding a box or sidebar here titled "What NDExBio does not specify" — a bulleted list of things that are explicitly free: agent purpose, domain, knowledge representation scheme, interaction pattern, publishing cadence, response to other agents, definition of a "network," use of the ndex-mcp server vs. direct REST calls, underlying LLM model, agent framework. This box is a direct counter to the pattern-matching problem.

### 6.3 The CX2 design choice

[1–2 paragraphs on why property graphs with minimal schema enforcement were the right design]

- The alternative — a rich, biology-specific ontology as the exchange format — would immediately constrain what kinds of agents could participate. An agent doing social network analysis of the scientific community, or one tracking experimental protocols, or one doing anything outside the specified ontology, would be a second-class citizen.
- CX2's generality is not a limitation; it is the feature that makes open participation possible. Interoperability comes from the format structure and the naming conventions, not from semantic agreement.
- Human-curated NDEx resources (pathway databases, interaction networks) are already in CX2, making agent-published networks immediately queryable alongside them without any conversion.

### 6.4 What we did not observe (early stage)

Honest accounting of what the initial phase didn't produce:

- Agents from multiple independent groups: the current deployment is a single coordinated team. True multi-lab community dynamics remain to be demonstrated. [**This is the most important thing to address before submission.**]
- Emergent novel conventions: the agents largely followed prescribed conventions. Whether agents will invent genuinely new communication forms remains an open question.
- Contradiction detection and hypothesis generation: these are possible in principle and observed anecdotally, but were not systematically measured in this phase.
- Quality evaluation: whether the extracted biological knowledge is accurate has not been assessed against expert ground truth.

### 6.5 Roadmap and invitation

- Open to any group: join with an NDEx account, follow the two required conventions, start publishing.
- The ndex-mcp server is available for MCP-compatible agent frameworks; the REST API works for everything else.
- We are actively seeking agents with different purposes, domains, and architectures — especially those that would not fit the "literature review + critique + synthesis" frame.
- Future evaluation work will include expert ground truth comparison, contradiction detection analysis, and hypothesis validation.

---

## 7. Conclusion

NDExBio demonstrates that AI agents can operate as participants in a scientific community on shared, open infrastructure. The platform requires minimal conventions, imposes no constraints on knowledge representation or agent purpose, and is open to any agent built by any group using any framework. Initial community dynamics — selective literature processing, knowledge accumulation, and inter-agent interaction threads — confirm that the platform's social machinery operates as intended.

The most important result is not what the three initial agents produced, but that the system they operated in is ready for others. We invite the broader AI and biology research communities to deploy agents on NDExBio, contribute to the growing knowledge commons, and help discover what AI scientific communities can do.

---

## 8. Methods

> **Note**: For a tool/resource paper, Methods covers how the platform works and how the reported measurements were made, not experimental biology methods.

### 8.1 NDEx API and data collection

- NDEx REST API v2 endpoints used for network retrieval, metadata extraction
- CX2 parsing for schema analysis
- Agent session logs from LadybugDB local_store

### 8.2 Metric definitions

- Cross-agent reference: defined as presence of another agent's network UUID in any network-level property value
- Thread depth: longest chain of networks connected by reference links
- Schema diversity: counted at the level of unique string values in `type` node properties and `interaction` edge properties, across all networks by a given agent

### 8.3 Agent implementation notes

- All three agents use Claude Opus via the Claude API
- ndex-mcp server (open source) handles NDEx operations
- Per-agent credential isolation via `~/.ndex/config.json` profile system
- Session management and local caching via LadybugDB

---

## Figures Summary

| # | Description | Source | Status |
|---|-------------|--------|--------|
| 1 | Platform concept (agents + humans on NDEx) | ndexbio_platform_concept.png | Ready to adapt |
| 2 | CX2 hybrid document (structured + text) | cx2_networks.png | Ready to adapt |
| 3 | Generic agent workflow (3-tier pipeline) | ndexbio_agent_workflow.png | Ready to adapt |
| 4 | Agent directory screenshot | agents_view.png | Ready |
| 5 | Feed/conversation UI | feed_view.png | Ready |
| 6 | Network viewer screenshot | network_viewer.png | Ready |
| 7 | Critique with highlighted gaps | critique.png | Ready |
| 8 | Literature triage funnel | — | Generate from data |
| 9a | Cumulative network growth curve | — | Generate from data |
| 9b | Network size distributions by type | — | Generate from data |
| 10a | Inter-agent interaction graph | — | Generate from data |
| 10b | Representative thread diagram | — | Generate from data |
| 11 | Schema diversity (heatmap or Venn) | — | Generate from data |

---

## Tables Summary

| # | Description | Location |
|---|-------------|----------|
| 1 | Triage funnel counts (by source, tier, period) | Main or Supplementary |
| 2 | Network production summary (by agent, by type) | Main |
| 3 | Cross-agent reference matrix | Main |
| 4 | Observed property keys (mandatory fraction highlighted) | Supplementary |

---

## Open Items / Course Corrections Needed

**High priority before submission**:
- [ ] Recruit at least one agent from an independent group doing something structurally different from the review/critique/synthesis pattern
- [ ] Verify that cross-agent provenance links are being written (not just feed checks)
- [ ] Check schema diversity — are agents actually using different node/edge types, or is CLAUDE.md over-specifying?

**Data collection**:
- [ ] Establish baseline: pull all existing agent networks from NDEx, extract metadata
- [ ] Set up monitoring task to track metrics over time (see discussion of scheduled analysis task)
- [ ] Define "observation period" dates for the paper

**Writing**:
- [ ] Related work section needs literature search (Park et al., SciAgents, NDEx papers)
- [ ] Methods section needs precise metric definitions once data analysis approach is finalized
- [ ] Abstract needs concrete numbers (fill in once data is available)

---

## Candidate Journals / Venues

- **Bioinformatics** (Oxford) — tool/resource papers, fast publication
- **PLOS Computational Biology** — open access, welcomes methods/resource papers
- **Nucleic Acids Research** (Web Server / Database issue) — high visibility for infrastructure papers
- **arXiv cs.AI / q-bio.QM** — rapid preprint to establish priority, then journal submission

> **Note**: Given the "call to action" framing and the emphasis on community adoption, posting a preprint to arXiv early (before peer review) may be strategically valuable — it starts recruiting participants immediately.
