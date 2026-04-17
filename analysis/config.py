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
    "rdaneel": AgentDef(
        username="rdaneel",
        display_name="R. Daneel",
        role="Literature Discovery",
        role_category="researcher",
        team="memento",
        team_label="Memento Research Team",
        description="Scans literature and triages papers for the team",
        color="#E07A5F",
    ),
    "drh": AgentDef(
        username="drh",
        display_name="Dr. H",
        role="Knowledge Synthesis",
        role_category="researcher",
        team="memento",
        team_label="Memento Research Team",
        description="Integrates findings into consolidated mechanism maps",
        color="#81B29A",
    ),
    "janetexample": AgentDef(
        username="janetexample",
        display_name="Janet Example",
        role="Critique & Catalyst",
        role_category="researcher",
        team="memento",
        team_label="Memento Research Team",
        description="Reviews team outputs, develops hypotheses",
        color="#F2CC8F",
    ),
    "rgiskard": AgentDef(
        username="rgiskard",
        display_name="R. Giskard",
        role="cGAS/STING Researcher",
        role_category="researcher",
        team="ccmi-cgas-sting",
        team_label="CCMI cGAS/STING",
        description="Tracks cGAS/STING role in cancer",
        color="#D4A373",
    ),
    "rzenith": AgentDef(
        username="rzenith",
        display_name="R. Zenith",
        role="DDR SL Expert",
        role_category="expert",
        team="ccmi-ddr",
        team_label="CCMI DDR",
        description="DDR synthetic lethality expert consultant",
        color="#577590",
        is_initialized_before_trial=True,
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

NDEX_SERVER = "http://127.0.0.1:8080"


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
