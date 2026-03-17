# Working Memory: rdaneel

**This file is a session scratch pad.** Persistent state is stored in the local graph database (`~/.ndex/cache/`). Query it via Local Store MCP tools.

## Quick Reference

- **Session history**: `query_graph("MATCH (s:BioNode {network_uuid: 'rdaneel-session-history'}) RETURN s.name, s.properties ORDER BY s.cx2_id DESC LIMIT 5")`
- **Papers read**: `query_graph("MATCH (p:BioNode {network_uuid: 'rdaneel-papers-read', node_type: 'paper'}) RETURN p.name, p.properties")`
- **All cached networks**: `query_catalog(agent="rdaneel")`
- **Find protein interactions**: `find_neighbors("TRIM25")`

## Last Session

- **Date**: 2026-03-12 (scan h)
- **Result**: First successful MCP-based triage run. 13 Tier 1 papers, 3 Tier 2 reviews, 1 Tier 3 analysis. 6 networks published. All infrastructure issues resolved.
- **Key finding**: TRIM25 dual role — RIG-I K63-ubiquitination (established) + RdRp pausing promotion (new from TenVIP-seq paper).

## Active Observations

- **TRIM25 × mvRNA connection**: Open question — are RdRp pause sites (where TRIM25 acts) the same sites that generate mvRNAs? If so, TRIM25 connects polymerase regulation to innate immune sensing of aberrant replication products.
- **DDX3X parallel**: DDX3X has dual roles (IFN-beta translation + IAV host factor), paralleling TRIM25. Host factors co-opted for multiple functions during viral infection is an emerging theme.
- **Publication lull**: March 7–12 had no new HPMI papers. Lull may have ended.

## Infrastructure Notes

- bioRxiv MCP API: working (egress proxy resolved as of scan h)
- NDEx credentials: working (profile `rdaneel` in `~/.ndex/config.json`)
- Local store: 30 networks cached in `~/.ndex/cache/`
- Reliable bioRxiv params: `interval_days=2-3`, `max_results=15-20`
