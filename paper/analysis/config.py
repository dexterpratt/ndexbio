"""
NDExBio Trial Analysis - Configuration

Agent definitions, team mappings, and trial parameters.
Edit this file to match the actual agents deployed in each trial.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Agent roster
# ---------------------------------------------------------------------------

@dataclass
class AgentDef:
    """Definition of one NDExBio agent."""
    username: str                   # NDEx username
    display_name: str               # e.g. "R. Solar"
    role: str                       # short role label for figures
    role_category: str              # researcher | expert | analyst | editor
    team: str                       # team identifier
    team_label: str                 # human-readable team name
    description: str                # one-line mission summary
    color: str                      # hex color for figures
    is_initialized_before_trial: bool = False  # experts pre-loaded


# Palette: warm tones for researchers, cool for experts, neutral for analysts/editors
AGENTS: dict[str, AgentDef] = {
    # --- HPMI Viral Cancer Team (3 agents) ---
    "rsolar": AgentDef(
        username="rsolar",
        display_name="R. Solar",
        role="Literature Discovery",
        role_category="researcher",
        team="hpmi-viral-cancer",
        team_label="HPMI Viral Cancer Team",
        description="Scans literature for oncogenic host-pathogen mechanisms",
        color="#E07A5F",
    ),
    "rvernal": AgentDef(
        username="rvernal",
        display_name="R. Vernal",
        role="Critique & Catalyst",
        role_category="researcher",
        team="hpmi-viral-cancer",
        team_label="HPMI Viral Cancer Team",
        description="Reviews team outputs, develops hypotheses, decides report readiness",
        color="#F2CC8F",
    ),
    "rboreal": AgentDef(
        username="rboreal",
        display_name="R. Boreal",
        role="Knowledge Synthesis",
        role_category="researcher",
        team="hpmi-viral-cancer",
        team_label="HPMI Viral Cancer Team",
        description="Integrates findings into consolidated mechanism maps",
        color="#81B29A",
    ),

    # --- CCMI cGAS/STING Researcher ---
    "rbaslat": AgentDef(
        username="rbaslat",
        display_name="R. Baslat",
        role="cGAS/STING Researcher",
        role_category="researcher",
        team="ccmi-cgas-sting",
        team_label="CCMI cGAS/STING",
        description="Tracks cGAS/STING role in cancer, seeks cross-domain connections",
        color="#D4A373",
    ),

    # --- Domain Experts (pre-initialized) ---
    "rzenith": AgentDef(
        username="rzenith",
        display_name="R. Zenith",
        role="DDR Synthetic Lethality Expert",
        role_category="expert",
        team="ccmi-ddr",
        team_label="CCMI DDR",
        description="Expert consultant on DNA damage repair synthetic lethality",
        color="#577590",
        is_initialized_before_trial=True,
    ),
    "rsolstice": AgentDef(
        username="rsolstice",
        display_name="R. Solstice",
        role="HPMI Network Data Expert",
        role_category="expert",
        team="hpmi-data",
        team_label="HPMI Data",
        description="Expert on host-pathogen interaction networks in NDEx",
        color="#4D908E",
        is_initialized_before_trial=True,
    ),

    # --- Analysis Service Agents ---
    "rcorona": AgentDef(
        username="rcorona",
        display_name="R. Corona",
        role="DepMap/GDSC Analyst",
        role_category="analyst",
        team="service-depmap",
        team_label="DepMap/GDSC Service",
        description="Queries DepMap and GDSC databases, provides analysis and caveats",
        color="#90BE6D",
    ),
    "rnexus": AgentDef(
        username="rnexus",
        display_name="R. Nexus",
        role="Gene Set Enrichment Analyst",
        role_category="analyst",
        team="service-enrichment",
        team_label="NDEx Enrichment Service",
        description="Performs pathway enrichment via NDEx IQuery, interprets results",
        color="#F9C74F",
    ),

    # --- Newsletter Editor ---
    "rlattice": AgentDef(
        username="rlattice",
        display_name="R. Lattice",
        role="Newsletter Editor",
        role_category="editor",
        team="ccmi-newsletter",
        team_label="CCMI Newsletter",
        description="Curates and publishes highlights from CCMI agent activity",
        color="#F94144",
    ),
}

# Convenient groupings
TEAMS = {}
for agent in AGENTS.values():
    TEAMS.setdefault(agent.team, []).append(agent.username)

ROLE_CATEGORIES = {}
for agent in AGENTS.values():
    ROLE_CATEGORIES.setdefault(agent.role_category, []).append(agent.username)


# ---------------------------------------------------------------------------
# NDEx connection
# ---------------------------------------------------------------------------

NDEX_SERVER = "https://www.ndexbio.org"


# ---------------------------------------------------------------------------
# Trial parameters
# ---------------------------------------------------------------------------

@dataclass
class TrialConfig:
    """Parameters for a single trial run."""
    trial_id: str = "trial_001"
    # Set these before running
    observation_start: Optional[str] = None   # ISO date, e.g. "2026-04-10"
    observation_end: Optional[str] = None
    # How many scheduled cycles the most-frequent agents ran
    max_cycles: Optional[int] = None
    # Output directory (relative to this file or absolute)
    output_dir: str = "output"


TRIAL = TrialConfig()


# ---------------------------------------------------------------------------
# Network annotation keys (from SHARED.md conventions)
# ---------------------------------------------------------------------------

# Required on every agent-published network
REQUIRED_PROPERTIES = {
    "ndex-agent",
    "ndex-message-type",
}

# Common optional properties
OPTIONAL_PROPERTIES = {
    "ndex-workflow",
    "ndex-reply-to",
    "ndex-references",
    "ndex-source",
    "ndex-interest-group",
    "ndex-data-type",
    "ndex-in-reply-to",
}

# All convention properties (union of required + known optional)
CONVENTION_PROPERTIES = REQUIRED_PROPERTIES | OPTIONAL_PROPERTIES

# Self-knowledge network name patterns
SELF_KNOWLEDGE_SUFFIXES = [
    "session-history",
    "plans",
    "collaborator-map",
    "papers-read",
    "researcher-network",
    "metrics-baseline",
]


# ---------------------------------------------------------------------------
# Figure styling
# ---------------------------------------------------------------------------

FIGURE_DPI = 300
FIGURE_FORMAT = "png"
# Role category colors for grouped charts
ROLE_CATEGORY_COLORS = {
    "researcher": "#E07A5F",
    "expert": "#577590",
    "analyst": "#90BE6D",
    "editor": "#F94144",
}
