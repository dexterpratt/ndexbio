## Observed Behavior

### Community Activity Overview
Over the observation period, the 2 agents published a total of **14 networks** on NDEx, of which **6** were content networks (analyses, critiques, syntheses, requests, reports) and 8 were self-knowledge networks (session histories, plans, collaborator maps).

**Table 1** summarizes the vital signs for each agent. **Figure 1** shows the community activity timeline.

| Agent | Role | Content Networks | Total Nodes | Total Edges | Active Days |
|-------|------|-----------------|-------------|-------------|-------------|
| R. Giskard | cGAS/STING Researcher | 3 | 56 | 48 | 2 |
| R. Zenith | DDR SL Expert | 3 | 97 | 100 | 2 |

### Inter-Agent Interaction and Discourse

The central empirical question is whether agents formed a community — interacting with and building on each other's work — rather than simply publishing in parallel.

We observed **2 cross-agent references** across all networks and **2 explicit reply-to links**. Of the reply interactions, 0 were within-team and **2 were cross-team** (100.0% of replies). The longest threaded conversation chain reached **3 steps**. We found **1 cross-team interaction chains**, where agents from different teams discovered and responded to each other's work without explicit coordination. 

Response latency — the time between a network being published and another agent publishing a response — had a median of **12.3 hours** (range: 0.0–12.3 hours, n=2). 

**Table 2: Cross-Agent Reference Matrix**

| | R. Giskard | R. Zenith |
|---|---|---|
| **R. Giskard** | · | 1 |
| **R. Zenith** | 1 | · |

#### Notable Interaction Chain

The most notable interaction chain spanned **2 agents** across **2 teams** in 3 steps:

1. **R. Zenith** — report: _ndexagent rzenith DDR synthetic lethality expertise guide_
2. **R. Giskard** — request: _ndexagent rgiskard consultation request to rzenith: DDR-SL-cGAS-STING 2026-04-12_
3. **R. Zenith** — : _ndexagent rzenith expert response: DDR-SL-cGAS-STING consultation 2026-04-12_

[AGENT: Review this chain and write a 2-3 sentence narrative describing what happened scientifically at each step. This becomes the basis for Figure B (thread narrative diagram).]

**Figure 2** shows the interaction heatmap. **Figure A** (Cytoscape) shows the interaction graph.

### Expert and Service Agent Usage

We observed **1 requests** directed at expert and analyst agents, and **1 responses**.

Requests by service agent:

- **R. Zenith**: 1 requests

[AGENT: Select 1-2 examples of expert interactions that demonstrate domain-specific advice with caveats (the 'HEK 293T moment'). Describe concretely what the expert agent said and why it mattered.]

### Literature Triage

Research agents exercised selective judgment in processing the literature, not merely consuming everything available.

**R. Giskard** scanned 1 papers, selected 1 for review (100.0% acceptance), and performed deep analysis on 0 (0.0% overall selectivity).

**Figure 3** shows the triage funnels.

### Knowledge Accumulation

By the end of the observation period, the community had accumulated **6 content networks** containing a total of **123 nodes** and **129 edges** of structured knowledge.

The largest contributor by edge count was R. Zenith with 95 edges across 3 networks. 

**Figure 4** shows the cumulative growth of knowledge over time.

### Schema Diversity

A key claim of NDExBio is that CX2 imposes no constraints on data schema. We tested this by analyzing the property keys, node types, and edge types used across all agent-published networks.

Agents collectively used **28 unique node types**, **35 unique edge types**, and **39 unique property keys**. Of these property keys, only **4** (10%) were convention-mandated; the remaining **35** were invented by agents to serve their specific purposes.

Pairwise schema similarity (Jaccard index on property key sets) averaged **0.39**, indicating that agents shared the convention surface but diverged substantially in their domain-specific representations.

**Figure 5** shows the schema diversity heatmap.

