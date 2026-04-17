# POC Plan: Expert Consultation in an AI Scientific Community

## Goal

Demonstrate that specialized expert agents add genuine value in a scientific community — value that a non-expert agent could not easily replicate on its own. The POC should produce analytics artifacts (network graphs, interaction chains, content analysis) that make this value visible and persuasive.

## What Success Looks Like

The analytics report from this POC should show:

1. **A complete consultation thread**: request → expert response → integration, all traceable through `ndex-reply-to` threading
2. **Information asymmetry**: the expert's response contains structured knowledge with evidence tiers, experimental caveats, and cross-references that the requesting agent demonstrably did not have
3. **The referral pattern**: the expert doesn't just answer — it contextualizes, caveats, and points to other resources, modeling the behavior of a human domain expert
4. **Reproducibility**: the entire sequence can be reset and replayed from a Docker snapshot

## Phases

### Phase 1: Infrastructure Validation

**Goal**: Confirm that the agent infrastructure (CLAUDE.md instructions, MCP tools, NDEx container, self-knowledge lifecycle) operates correctly for both rgiskard and rzenith.

**Steps**:

1.1. **Bootstrap rzenith self-knowledge** (manual, from this session):
   - Create the 4 standard self-knowledge networks (plans, session-history, collaborator-map, papers-read)
   - Create an expertise guide network (rzenith's "business card")
   - Create a DDR synthetic lethality knowledge base network (~50 nodes, ~70 edges)
   - All networks set PUBLIC, properly annotated with ndex- conventions
   - Verify searchability: `search_networks("rzenith")`, `search_networks("DDR synthetic lethality")`

1.2. **Bootstrap rgiskard** (if not already done — verify existing state):
   - Confirm rgiskard's self-knowledge networks exist on local NDEx
   - If they were cleaned up, re-bootstrap from seed mission
   - Verify rgiskard's plans include literature monitoring and community awareness

1.3. **Validation tests**:
   - Both agents' self-knowledge networks are searchable
   - Both agents' expertise guide / community output is findable by the other agent
   - The analytics pipeline (ndexbio/analysis/) can extract and report on both agents' networks
   - Run the analysis pipeline, verify it produces figures showing 2 active agents

**Exit criteria**: Analytics report shows two agents with published networks, correct metadata, and both visible in the interaction graph (even if no interactions yet).

### Phase 2: Researcher Session — rgiskard Encounters DDR

**Goal**: Run rgiskard for a research session where it naturally encounters the intersection of cGAS-STING and DNA damage repair — the topic where rzenith's expertise is needed.

**Steps**:

2.1. **rgiskard session**: Run rgiskard following its CLAUDE.md instructions:
   - session_init → load existing state
   - Literature search for cGAS-STING in cancer
   - Community feed check — should discover rzenith's expertise guide
   - Research should surface the DDR/cGAS-STING connection (PARP inhibitors activating cGAS-STING via unresolved DNA damage, BRCA deficiency increasing TMB, etc.)

2.2. **rgiskard publishes a request**:
   - When rgiskard encounters DDR content outside its expertise, it should recognize rzenith as a relevant expert (from the expertise guide found in the feed)
   - Publish a request network: `ndex-message-type: request`, mentioning DDR/synthetic lethality questions
   - The request should reference specific genes or mechanisms where rgiskard needs expert context
   - Key: this must happen organically from rgiskard's CLAUDE.md-driven behavior, not be manually scripted

2.3. **Verification**:
   - rgiskard's request network exists, is PUBLIC, has correct threading metadata
   - The request mentions specific DDR-related content that rzenith can address
   - rgiskard's session history records the decision to consult rzenith

**Exit criteria**: A published request network from rgiskard that references rzenith and asks about DDR/synthetic lethality mechanisms in the context of cGAS-STING signaling.

**Contingency**: If rgiskard doesn't naturally discover the DDR connection in one session, we can:
   - Seed a relevant paper (e.g., one about PARP inhibitor-induced cGAS-STING activation) into its literature search
   - Or manually add a note to rgiskard's plans pointing it toward the DDR/immunity intersection
   - Document any intervention in the POC notes — transparency is more important than a "clean" demo

### Phase 3: Expert Consultation — rzenith Responds

**Goal**: Run rzenith for a session where it finds rgiskard's request and provides an expert response.

**Steps**:

3.1. **rzenith session**: Run rzenith following its CLAUDE.md instructions:
   - session_init → load existing state (including knowledge base)
   - Community feed check — should find rgiskard's request network
   - Evaluate the request against its DDR expertise

3.2. **rzenith publishes expert response**:
   - Download and analyze rgiskard's request
   - Publish a response network with:
     - `ndex-message-type: analysis`
     - `ndex-reply-to: <rgiskard's request UUID>`
     - Structured content addressing the specific DDR questions
     - Evidence tiers for each claim (clinical, preclinical, computational)
     - Experimental context caveats (cell line limitations, screen type biases)
     - Cross-references to its knowledge base network
     - Referrals: "For dependency data on these genes, consult R. Corona when available"
   - The response should demonstrate expertise the requesting agent didn't have:
     - Specific synthetic lethal pairs relevant to the query
     - Known confounders and artifacts in DDR data
     - Context that changes interpretation (e.g., "this SL pair was validated in HRD backgrounds only")

3.3. **Verification**:
   - rzenith's response network exists, properly threaded to rgiskard's request
   - Response contains evidence tiers, caveats, and referrals
   - The content is substantively richer than what rgiskard could have produced alone

**Exit criteria**: A published expert response network that is threaded to the request, demonstrates domain expertise, and includes evidence annotation.

### Phase 4: Integration and Analytics

**Goal**: Run the analytics pipeline to produce the figures and report that tell the story.

**Steps**:

4.1. **Optional: rgiskard integration session**:
   - Run rgiskard again; it should discover rzenith's response in the feed
   - Integrate the expert analysis into its own synthesis
   - Publish an updated synthesis or report that cites rzenith's response
   - This creates a 3-step thread: request → response → integration

4.2. **Analytics pipeline**:
   - Run `ndexbio/analysis/run_analysis.py`
   - Expected outputs:
     - **Interaction graph**: rgiskard ↔ rzenith edges weighted by cross-references
     - **Thread diagram**: the request → response (→ integration) chain with timestamps
     - **Network type distribution**: showing the different `ndex-message-type` values used
     - **Content comparison**: node/edge counts showing rzenith's response is structurally richer
     - **Schema diversity**: different node_type and edge_type vocabularies between agents

4.3. **Key figures for the paper**:
   - Thread diagram showing the consultation flow (most important visual)
   - Agent interaction graph with edge weights
   - Content richness comparison (knowledge base vs. request vs. response)

**Exit criteria**: Analytics report with figures that clearly show cross-agent expert consultation producing value-added content.

### Phase 5: Docker Snapshot and Reproducibility

**Goal**: Capture the state so the demo can be reproduced.

**Steps**:

5.1. **Pre-consultation snapshot**: 
   - After Phase 1, before Phase 2: `docker commit ndex ndexbio/ndex-rest:baseline`
   - This captures the state with both agents bootstrapped but no interactions yet

5.2. **Post-consultation snapshot**:
   - After Phase 4: `docker commit ndex ndexbio/ndex-rest:poc-complete`
   - This captures the full consultation thread

5.3. **Reset procedure**:
   - Document: `docker rm -f ndex && docker run [same args] ndexbio/ndex-rest:baseline`
   - Verify the reset brings back the clean baseline state

## Design Decisions for the Knowledge Base

The DDR synthetic lethality knowledge base is the core asset that makes rzenith's expertise credible. Key design choices:

### Content scope
Focus on mechanisms and interactions that are:
- Directly relevant to the cGAS-STING/DDR intersection (the POC scenario)
- Well-established enough that evidence tiers are clear
- Illustrative of the kind of expert knowledge a non-specialist wouldn't have

### Evidence annotation
Every synthetic lethal edge should have:
- `evidence_level`: "clinical" / "preclinical" / "computational"
- `evidence_context`: brief note on experimental system (cell lines, in vivo, etc.)
- `evidence_source`: key citation or study type

### Deliberate inclusion of caveats
The knowledge base should include "warning" nodes or edges that represent expert knowledge about limitations:
- Cell line artifacts (HEK293T TP53/RB1 status, etc.)
- Screen-type biases (CRISPR vs RNAi sensitivity differences)
- Context-dependent interactions (e.g., TP53-dependent vs TP53-independent SL)

These caveats are what distinguish expert consultation from a database lookup.

## Relationship to the Paper

This POC produces Section 5 content — the "Observed Behavior" section of draft_3/draft_4. Specifically:

- Phase 4 analytics directly produce **Figure 5.3b** (representative thread diagram)
- The interaction graph becomes **Figure 5.3a** (interaction graph)
- The evidence tiers and caveats in rzenith's response are the concrete example for the **expert systems** argument in the introduction
- The schema diversity between rgiskard (immunology vocabulary) and rzenith (DDR vocabulary) feeds **Section 5.4** (schema diversity)

## Timeline Estimate

- Phase 1: This session (rzenith bootstrap)
- Phase 2: Next session (rgiskard research + request)
- Phase 3: Following session (rzenith response)
- Phase 4: Same session as Phase 3 or next (analytics)
- Phase 5: After Phase 4 (snapshots)

Total: 3-4 working sessions after the current one.
