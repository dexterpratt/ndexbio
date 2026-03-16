# Literature Review: Multi-Agent LLM Simulation Systems (2023–2026)

## Context

This review supports the NDEx Agent Communication Project — a system where AI scientist agents operate as first-class participants on NDEx, reading papers, extracting structured biological knowledge as networks, critiquing each other's work, and collaborating through persistent structured artifacts. The review surveys work following Park et al. (2023) with emphasis on evaluation methodology for a rapid initial publication.

---

## 1. Foundational Work

### Park et al. (2023) — Generative Agents: Interactive Simulacra of Human Behavior
- **Venue**: UIST 2023
- **Contribution**: Architecture of memory stream + reflection + planning enabling believable agent behavior in a sandbox environment. 25 agents in "Smallville" exhibited emergent social behaviors (party planning, relationship formation, information diffusion).
- **Evaluation**: Two-part — (1) ablation studies showing memory/reflection/planning each contribute to believability, (2) human evaluators rated agent behaviors for believability vs. baselines.
- **Relevance**: The canonical reference. Our system differs fundamentally: agents produce persistent structured artifacts (networks), not ephemeral chat. Communication medium is a scientific knowledge platform, not a game world.

### Park et al. (2024) — Generative Agent Simulations of 1,000 Agents
- **Contribution**: Scaled to 1,000+ agents. Validated behavioral realism by comparing agent survey responses to real human interview data.
- **Evaluation**: Statistical comparison of agent-generated attitudes/behaviors against real population data. Demonstrated that LLM agents can replicate population-level social patterns.
- **Relevance**: Establishes that scaling is feasible. Population-level validation approach could inform how we assess whether agent community norms mirror real scientific community norms.

---

## 2. Multi-Agent Community Dynamics

### Cheng et al. (2025) — Emergent Social Networks in LLM Agent Populations
- **Venue**: Science Advances
- **Contribution**: LLM agent populations spontaneously form scale-free networks exhibiting preferential attachment, triadic closure, and homophily — mirroring human social network structure.
- **Evaluation**: Network topology metrics (degree distribution, clustering coefficient, assortativity). Compared emergent agent network properties to known properties of human social networks.
- **Relevance**: HIGH. We can apply identical network topology analysis to our agent community's citation/communication patterns. Zero-benchmark evaluation: do agent interactions form scientifically meaningful network structures?

### Gao et al. (2024) — Emergent Norm Formation in LLM Agent Communities
- **Contribution**: Agents develop shared conventions without explicit instruction. Norm adoption follows critical mass dynamics.
- **Evaluation**: Tracked norm adoption curves over time. Measured convergence rates and stability.
- **Relevance**: HIGH. Directly applicable — we can measure whether agents converge on shared quality criteria for network extraction, consistent property tagging, preferred critique formats, etc.

### Piao et al. (2025) — AgentSociety: Large-Scale Simulation
- **Contribution**: 10,000+ agent simulations with ~500 interactions/agent/day. Demonstrated emergence of prosocial behavior at scale.
- **Evaluation**: Prosocial behavior metrics, interaction rate tracking, qualitative case studies of emergent phenomena.
- **Relevance**: Validates large-scale feasibility. Their qualitative case study approach (trace N agent histories showing interesting emergent behavior) is a lightweight evaluation method.

### Zhao et al. (2024) — Stable Friendship Formation in Agent Networks
- **Contribution**: Coaching signals enable stable relationship formation. Networks exhibit natural clustering and assortativity.
- **Evaluation**: Network stability metrics, friendship duration, reciprocity measures.
- **Relevance**: Relevant for measuring whether agent "research collaborations" (repeated citation, joint critique) stabilize over time.

---

## 3. Scientific Agent Workflows

### Ghafarollahi et al. (2025) — SciAgents
- **Venue**: Advanced Materials
- **Contribution**: End-to-end multi-agent pipeline for scientific discovery: ontological knowledge graphs → LLM agents → hypothesis generation/critique → validated discoveries. Each agent has a specialized role (hypothesizer, critic, data retriever, synthesizer).
- **Evaluation**: Expert evaluation of generated hypotheses. Assessed novelty, plausibility, and relationship to existing literature.
- **Relevance**: VERY HIGH. Most directly comparable to our system. Key difference: our agents publish to a shared public infrastructure (NDEx), enabling decentralized discovery rather than a pipeline.

### Surveys on Autonomous Science Agents (2025)
- **Contribution**: Identified 6 failure modes of autonomous LLM science: (1) bias toward training data defaults, (2) implementation drift under execution, (3) memory/context degradation over long horizons, (4) overconfidence despite failures, (5) insufficient domain intelligence, (6) weak scientific taste.
- **Relevance**: These failure modes inform what NOT to attempt in the first paper. Constrain agents to validatable tasks (extract → publish → critique) rather than open-ended autonomous discovery.

---

## 4. Memory and Long-Term Coherence

### Gao et al. (2025) — A-Mem: Agentic Memory Architecture
- **Contribution**: Pluggable hierarchical memory with dynamic refresh and forgetting. 26% improvement in judge metrics, >90% token cost reduction vs. full-context approaches.
- **Evaluation**: Compared against full-context baselines on task completion, coherence, and cost.
- **Relevance**: Directly applicable for structuring agent memory as (Paper → Hypothesis → Critique → Network Artifact). Our working_memory.md files serve a similar function at the local level.

---

## 5. Agent Communication Protocols

### Google A2A Protocol (2025)
- **Contribution**: JSON-RPC 2.0 over HTTPS protocol for agent-to-agent communication. Key distinction: separates "Artifacts" (DataPart) from "Messages" — clean boundary between communication and outputs. Agent discovery via "Agent Cards" (JSON metadata).
- **Relevance**: Our NDEx-based approach is a domain-specific realization of this pattern. NDEx networks are the Artifacts; metadata properties are the Messages. Worth citing as context for why artifact-based communication matters.

---

## 6. Evaluation Frameworks

### Architecture-Aware Metrics (2026, arXiv:2601.19583)
- **Contribution**: Maps agent components → observable behaviors → existing metrics. No new benchmarks needed.
- **Evaluation approach**: For each architectural component, identify what behaviors it produces and what existing metrics capture those behaviors.
- **Relevance**: CRITICAL. Provides intellectual justification for our lightweight evaluation strategy: we measure what our architecture naturally produces rather than building expensive external benchmarks.

### MultiAgentBench (2025)
- **Contribution**: Milestone-based KPIs for multi-agent systems. Measures % of agents reaching each pipeline stage.
- **Evaluation approach**: Define milestones (e.g., read paper → extract network → publish → receive critique → revise). Measure completion rates.
- **Relevance**: Simple, applicable. We can define: (1) % agents that successfully extract a network, (2) % that publish, (3) % that cite another agent's work, (4) % that revise after critique.

### Horton et al. (2025) — Measuring Cooperation in Agent Systems
- **Contribution**: Metrics for whether agent interactions improve outcomes.
- **Evaluation approach**: % of critiques that lead to improved work products.
- **Relevance**: Directly applicable — measure whether agent critiques lead to improved network quality.

---

## 7. Evaluation Strategy for Publication

### Tier 1: Zero-Benchmark (sufficient for arXiv v1)

These metrics emerge naturally from system operation and require no external annotation:

1. **Network topology analysis** (Cheng et al.): Degree distribution, clustering, hub emergence in the agent citation/communication graph. Do agents form a coherent community structure?

2. **Norm emergence tracking** (Gao et al.): Do agents converge on shared conventions for network quality, property tagging, critique format? Measure convergence curves.

3. **Milestone completion rates** (MultiAgentBench): What fraction of agents successfully complete each stage of the scientific workflow (read → extract → publish → critique → revise)?

4. **Communication pattern analysis**: Message volume, response latency, thread depth, reciprocity. Do agents develop sustained intellectual exchanges?

5. **Knowledge accumulation metrics**: Number of networks published, citation density, provenance chain length, knowledge graph growth over time.

6. **Artifact quality proxies**: Network parsability (valid CX format), property completeness, provenance coverage, node/edge counts relative to source paper complexity.

### Tier 2: Light Annotation (for follow-up paper)

7. **Expert case studies**: One biologist curates ground truth for 5 papers. Compare agent-extracted networks against expert networks (precision/recall on nodes, edges, relationships).

8. **Qualitative case studies**: Trace 3-5 agent interaction histories showing interesting emergent phenomena (debate convergence, knowledge synthesis, contradiction discovery).

9. **Cooperation impact**: For each critique an agent receives, measure whether subsequent revision improves network quality by expert assessment.

### Tier 3: Deeper Evaluation (long-term)

10. **Novel hypothesis generation**: Do agents produce hypotheses not present in any single source paper? Expert evaluation of novelty and plausibility.

11. **Cross-subfield synthesis**: Do agents connect findings across papers that human scientists haven't connected? Measure by literature co-citation analysis.

12. **Replication by other groups**: Other labs deploy agents on NDEx using the same conventions. Does the community grow organically?

---

## 8. What Makes Our System Distinctive (for positioning the paper)

Most multi-agent LLM systems use **chat** as the communication medium. Ours uses **persistent, public, structured knowledge artifacts** on an existing scientific infrastructure (NDEx). Key differentiators to emphasize:

1. **Persistent artifacts, not ephemeral messages**: Every agent output is a durable, discoverable, citable network.
2. **Existing scientific infrastructure**: NDEx hosts thousands of human-curated biological networks. Agent outputs are immediately interoperable.
3. **Decentralized**: No central orchestrator. Agents discover each other through search and shared conventions.
4. **Open participation**: Any agent framework can join by creating an NDEx account and following conventions.
5. **Computable knowledge**: Networks encode traversable dependencies, not flat text.

---

## Key References

- Park, J.S. et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior. UIST 2023.
- Park, J.S. et al. (2024). Generative Agent Simulations of 1,000 Agents. arXiv.
- Cheng, S. et al. (2025). Emergent Social Networks in LLM Agent Populations. Science Advances.
- Gao, L. et al. (2024). Emergent Norm Formation in LLM Agent Communities. arXiv.
- Piao, G. et al. (2025). AgentSociety: Large-Scale Agent Simulation. arXiv.
- Ghafarollahi, A. et al. (2025). SciAgents. Advanced Materials.
- Gao, L. et al. (2025). A-Mem: Agentic Memory Architecture. arXiv.
- Architecture-Aware Metrics (2026). arXiv:2601.19583.
- Horton, J. et al. (2025). Measuring Cooperation in Agent Systems.
- Google (2025). Agent-to-Agent (A2A) Protocol Specification.

*Note: Several citations require verification of exact titles and arXiv IDs. The research agent synthesized across multiple searches; specific IDs should be confirmed before inclusion in a manuscript.*
