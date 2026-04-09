# Cytoscape Figure Workflow

These figures require the Cytoscape Desktop MCP. The analyst agent
should follow these steps interactively, reviewing each image and
adjusting until the figure is publication-ready.

The input for both figures comes from the metrics JSON produced by
`metrics.py`. The agent reads the relevant sections and constructs
CX2 network specs to send to Cytoscape.

---

## Figure A: Agent Interaction Graph (potential hero figure)

**Purpose:** Show the community structure — agents as nodes, interactions
as weighted directed edges. This is the visual proof that agents form a
community, not just run in parallel.

**Data source:** `metrics.interactions.reference_matrix`

### Steps

1. **Build the CX2 network spec** from the reference matrix:
   - One node per agent that has any interactions (skip isolates, or
     include them dimmed to show the full roster)
   - Node attributes: `name` (display name), `role_category`, `team`,
     `color` (from config.py), `network_count` (from activity metrics)
   - One directed edge per non-zero cell in the reference matrix
   - Edge attributes: `weight` (reference count), `is_cross_team` (boolean)
   - Set edge width proportional to weight

2. **Send to Cytoscape** via `create_network`

3. **Apply layout:**
   - Start with `force-directed` or `cose` layout
   - If agents cluster by team, that's good — keep it
   - If the layout is messy, try `circular` and manually assess

4. **Apply visual style:**
   - Node size proportional to `network_count` (bigger = more productive)
   - Node color from agent config colors
   - Node labels: display name + role (two lines if possible)
   - Edge width proportional to weight
   - Edge color: dark for cross-team, light gray for within-team
   - Edge arrows showing direction of reference
   - Consider adding edge labels with count for the most important edges

5. **Review and adjust:**
   - Export image, review for clarity
   - Are labels readable? Increase font if needed
   - Is the cross-team vs within-team distinction visible?
   - Are there overlapping nodes? Adjust layout manually if needed
   - Is the figure too dense? Consider removing self-knowledge references
     or low-weight edges (weight < 2)

6. **Export final image** at high DPI (300+), save as
   `output/figures/fig_interaction_graph.png`

### Visual goals
- The HPMI viral cancer team (Solar/Vernal/Boreal) should visually cluster
- Cross-team edges (especially any from Baslat, Corona, Nexus to the
  research teams) should be visually prominent — these are the paper's
  strongest evidence
- Service agents (Corona, Nexus) might have a distinctive shape (diamond?)
  to distinguish them from researchers
- If Lattice (newsletter editor) has edges, those show a unique role

---

## Figure B: Thread Narrative Diagram (hero figure candidate)

**Purpose:** Show the best cross-team interaction chain step by step.
This is the figure that makes the concept concrete and vivid. It should
be readable without the main text.

**Data source:** `metrics.interactions.thread_chains` (sorted by
interestingness — cross-team chains first, then by length and agent count)

### Steps

1. **Select the best chain:**
   - Pick the first chain in `thread_chains` that spans multiple teams
   - If no cross-team chains exist, pick the longest within-team chain
   - The chain should have at least 3 steps to tell a story

2. **Build a timeline/sequence CX2 network:**
   - Nodes represent steps in the chain (one per network in the chain)
   - Node attributes: `agent` (display name), `message_type`, `name`
     (network name, shortened), `creation_time`, `step_number`
   - Edges connect sequential steps: step 1 → step 2 → step 3
   - Edge attribute: `latency` (time between steps, for annotation)
   - Add agent identity nodes connected to their step nodes (optional,
     for showing who did what)

3. **Apply layout:**
   - Use a hierarchical or left-to-right layout to show temporal flow
   - Steps should progress left-to-right or top-to-bottom
   - If using hierarchical: root = first step, leaves = final outputs

4. **Apply visual style:**
   - Step nodes colored by agent (using config colors)
   - Step nodes shaped by message type (rectangle for analysis, diamond
     for critique, hexagon for synthesis, etc.)
   - Labels should show: agent name, abbreviated action, key detail
   - Edge labels: latency (e.g., "2.3 hours later")
   - Add a brief text annotation on 2-3 key steps explaining what
     happened scientifically (e.g., "Discovered paper on viral
     oncogene X" → "Flagged missing STING connection" → "Queried
     DepMap for dependency data")

5. **Review and adjust:**
   - Is the story clear from the figure alone?
   - Are the annotations readable but not overwhelming?
   - Does the temporal flow read naturally?
   - Would a reader understand what happened without reading the paper?

6. **Export final image** at high DPI, save as
   `output/figures/fig_thread_narrative.png`

### Visual goals
- This should look like a story, not a graph
- The cross-team moment (when an agent from a different team enters the
  chain) should be visually marked — maybe a vertical dashed line or a
  color boundary
- Keep it to one "best example" — don't try to show all chains
- If the best chain is short (2 steps), consider showing 2-3 short
  chains side by side as a composite figure

---

## Figure C: Convention Surface Diagram (sidebar/cartoon)

**Purpose:** Visual argument that the mandatory convention surface is
tiny. Not a data figure — a conceptual cartoon.

### Steps

1. **Build a simple CX2 network with two zones:**
   - A small cluster of nodes representing the convention surface:
     `ndexagent prefix`, `ndex-agent`, `ndex-message-type`
   - A much larger open area representing everything else agents can do
   - Annotate the small cluster: "Required" (3 items)
   - Annotate the large area: "Free" (with examples: schema, vocabulary,
     network structure, interaction patterns, publishing cadence...)

2. Or simply create this as a styled rectangle diagram in Cytoscape:
   - Small colored border = conventions
   - Large open interior = agent freedom

3. **Export** as `output/figures/fig_convention_surface.png`

This figure works best as a sidebar or inset, not a full figure.

---

## Notes for the analyst agent

- Always use `export_image` after layout to review before finalizing
- The Cytoscape MCP supports: `create_network`, `apply_layout`,
  `set_visual_style`, `export_image`, `select_nodes`, `get_network_info`
- Iterate: send network → layout → export → review → adjust → re-export
- For publication quality, ensure labels don't overlap and edges are
  distinguishable
- Save Cytoscape session files (.cys) alongside exported images for
  future editing
