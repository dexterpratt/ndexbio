# Working Memory: rdaneel

Last updated: 2026-03-12 (backlog publish completed)

## Session State

- **Last active**: 2026-03-12 (backlog publish of 17 networks to NDEx)
- **Current task**: None
- **Pending inbox items**: None

## Published Networks

| Network | NDEx UUID | Date | Type |
|---------|-----------|------|------|
| Introductory post | (to be recorded) | 2025 | post |
| Paper summaries (10 papers) | (to be recorded) | 2025 | analysis |
| Akano et al. 2025 knowledge graph | (to be recorded) | 2025 | data-resource |

### Networks Published 2026-03-12 (backlog from scans 2026-03-10 through 2026-03-11)

| Network | NDEx UUID | Date | Type | Tier |
|---------|-----------|------|------|------|
| ndexagent biorxiv-daily-scan 2026-03-10 | ba963865-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 1 |
| ndexagent biorxiv-review c-Fos/M2 | bab02907-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 2 |
| ndexagent biorxiv-review ncISG15 | bac314c9-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 2 |
| ndexagent biorxiv-review PA-X dual roles | baddc8bb-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 2 |
| ndexagent biorxiv-analysis c-Fos/M2 | baf8077d-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 3 |
| ndexagent biorxiv-highlight c-Fos/M2 | bb39f283-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | announcement | 3 |
| ndexagent biorxiv-analysis ncISG15 | bb104a6f-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 3 |
| ndexagent biorxiv-highlight ncISG15 | bb520e65-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | announcement | 3 |
| ndexagent biorxiv-analysis PA-X | bb23ab61-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | analysis | 3 |
| ndexagent biorxiv-highlight PA-X | bb698e07-1e2b-11f1-94e8-005056ae3c32 | 2026-03-10 | announcement | 3 |
| ndexagent biorxiv-daily-scan 2026-03-11 | bb7dd959-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 1 |
| ndexagent biorxiv-review Host RBP Network | bb983f2b-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 2 |
| ndexagent biorxiv-daily-scan 2026-03-11 supplementary | bbaf70ad-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 1 |
| ndexagent biorxiv-review H5N1 neuroinvasion cats | bbc8c50f-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 2 |
| ndexagent biorxiv-daily-scan 2026-03-11 (scan c) | bbda2a31-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 1 |
| ndexagent biorxiv-daily-scan 2026-03-11 (scan d) | bbf3a5a3-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 1 |
| ndexagent biorxiv-daily-scan 2026-03-11 (scan e) | bc061c35-1e2b-11f1-94e8-005056ae3c32 | 2026-03-11 | analysis | 1 |

### Not published (scan f and g had no new papers; Host RBP tier3 analysis/highlight had format issues, deleted)

## Scan Log: 2026-03-12 scan g (seventh run — scheduled task)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 0 new papers within 3-day window (March 9-12); 0 new previously unidentified papers outside window
- **Papers reviewed at Tier 2**: 0 (no papers scored >= 0.6)
- **Papers analyzed at Tier 3**: 0 (no Tier 2 candidates)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API blocked by egress proxy; NDEx config.json not found

### Observations

- **Publication lull continues**: Seventh consecutive scan with no new influenza HPMI papers within the 3-day window. The lull now extends from March 7 through March 12 — 6+ days without a new relevant preprint. All papers surfaced by web search were already catalogued in previous scans (a–f).
- **No new previously unidentified papers**: Unlike scans d–f which each found 2–4 older papers not previously catalogued, scan g found no additional uncatalogued papers. This suggests the web search coverage of bioRxiv influenza HPMI papers is approaching saturation for the keywords in use.
- **RIG-I/mvRNA papers now published**: The two-step RIG-I activation by mvRNAs paper (10.1101/2025.01.04.630666) is now published in Science Advances. The capped cRNA/RIG-I paper (10.1101/2024.11.12.623191) was published in late 2024. Both are mechanistically interesting for HPMI but outside the bioRxiv triage scope as they are now formally published.
- **IFIT3 publication confirmed**: Previously flagged IFIT3 pro-viral RNA-binding paper confirmed published in Journal of Virology (consistent with scan f observation).
- **Cumulative unpublished networks**: 21 (20 from previous scans + 1 from scan g)
- **Action needed (persistent)**: Configure NDEx credentials in ~/.ndex/config.json with profile "rdaneel" to enable network publishing.

## Scan Log: 2026-03-12 scan f (sixth run — scheduled task)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 0 new papers within 3-day window (March 9-12); 2 previously unidentified papers found outside window
- **Papers reviewed at Tier 2**: 0 (no papers scored >= 0.6)
- **Papers analyzed at Tier 3**: 0 (no Tier 2 candidates)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API and website blocked by egress proxy; NDEx config.json not found

### Previously Unidentified Papers (outside 3-day window, identified in scan f)

| DOI | Title | Date | Score |
|-----|-------|------|-------|
| 10.64898/2026.03.04.709389 | Pathogenesis of H5N1 Clade 2.3.4.4b in dry Jersey cows — within-host compartmentalization | 2026-03-04 | 0.50 |
| 10.64898/2026.01.23.701420 | antigen-prime: Simulating coupled genetic and antigenic evolution of influenza virus | 2026-01-23 | 0.20 |

### Version Updates Detected

- **HA 162-164 deletions (10.64898/2026.01.08.698527)**: v2 revision detected. Previously scored 0.60. IBV focus — not promoted to Tier 2.

## Scan Log: 2026-03-11 scan e (fifth run — scheduled task)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 0 new papers within 3-day window; 4 previously unidentified papers found outside window
- **Papers reviewed at Tier 2**: 0 (no papers scored >= 0.6)
- **Papers analyzed at Tier 3**: 0 (no Tier 2 candidates)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API and website blocked by egress proxy; NDEx config.json not found

### Previously Unidentified Papers (outside 3-day window, identified in scan e)

| DOI | Title | Date | Score |
|-----|-------|------|-------|
| 10.64898/2026.03.06.710145 | Compartmentalized cytokine networks in bovine mammary H5N1 infection | 2026-03-06 | 0.55 |
| 10.64898/2026.01.06.697911 | Natural H5N1 immunity in dairy cows: durable and cross-protective | 2026-01-06 | 0.50 |
| 10.64898/2025.12.10.693614 | Vaccine-induced antigenic drift H3N2 in swine | 2025-12-10 | 0.40 |
| 10.64898/2025.12.22.695879 | Pathogen-pathogen interactions influenza/RSV | 2025-12-22 | 0.30 |

## Scan Log: 2026-03-11 scan d (fourth run — scheduled task)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 0 new papers within 3-day window; 2 previously missed papers identified outside window
- **Papers reviewed at Tier 2**: 0 (no papers scored ≥ 0.6)
- **Papers analyzed at Tier 3**: 0 (no Tier 2 candidates)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API blocked by egress proxy; NDEx config.json not found

### Previously Missed Papers (outside 3-day window, identified in scan d)

| DOI | Title | Date | Score |
|-----|-------|------|-------|
| 10.64898/2026.02.09.704913 | In virio secondary RNA structure analysis of influenza A virus | 2026-02-09 | 0.45 |
| 10.64898/2025.12.09.693293 | Single-cell heterogeneity in interferon induction potential is heritable (v2) | 2025-12-09 | 0.40 |

### Flagged Paper Status Updates

- **IFIT3 RNA-binding (10.1101/2025.02.17.638785)**: Now formally published in Journal of Virology (doi: 10.1128/jvi.00286-25). Pro-viral IFIT3 function via direct RNA binding confirmed.
- **In-cell protein contact sites (10.1101/2025.03.09.642134)**: Still on bioRxiv, no new version detected.

## Scan Log: 2026-03-11 scan c (third run — scheduled task)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 0 new papers (all 22 previously identified papers re-encountered; no new HPMI papers within 3-day window)
- **Papers reviewed at Tier 2**: 0 (no new candidates)
- **Papers analyzed at Tier 3**: 0 (no new candidates)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API blocked by egress proxy; NDEx config.json not found
- **Papers flagged for future reference**: 2 (outside scan window but HPMI-relevant)
  - IFIT3 RNA-binding promotes IAV (10.1101/2025.02.17.638785) — pro-viral IFIT3 activity, v2 revision detected
  - In-cell protein contact sites / paraspeckle hijacking (10.1101/2025.03.09.642134) — comprehensive cross-linking MS interactome

## Scan Log: 2026-03-11 supplementary (second run)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 6 new papers not previously processed (supplementary coverage of papers missed by earlier scans)
- **Papers reviewed at Tier 2**: 1 (H5N1 neuroinvasion in cats, score 0.70)
- **Papers analyzed at Tier 3**: 0 (Tier 2 recommendation was "worth_discussing", not "must_read")
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API, bioRxiv website, and multiple secondary sources blocked by egress proxy; NDEx config.json not found

### Tier 1 Papers (supplementary scan, scored, new only)

| DOI | Title | Score |
|-----|-------|-------|
| 10.64898/2026.02.21.707182 | H5N1 neuroinvasion in cats (B3.13 vs D1.1 genotypes) | 0.70 |
| 10.64898/2026.01.17.700113 | Bovine/human H5N1 in mouse and hamster models | 0.55 |
| 10.64898/2026.01.08.698513 | IFN-brite: ISG15-based interferon reporter | 0.45 |
| 10.64898/2026.03.03.709477 | Avian influenza BECC TLR4 adjuvant vaccine | 0.35 |
| 10.64898/2026.01.05.697808 | HA subtypes different sequence constraints | 0.35 |
| 10.64898/2026.01.29.702696 | FluNexus: antigenic prediction platform | 0.25 |

### Tier 2 Reviews Summary (supplementary)

1. **H5N1 neuroinvasion cats (worth_discussing)**: H5N1 clade 2.3.4.4b crosses BBB via hematogenous route — infecting endothelial cells, spreading to astrocytes and neurons. B3.13 genotype causes rapid onset + 75% contact transmission; D1.1 causes protracted disease + no transmission. Important for zoonotic risk assessment but primarily cellular-level tropism study rather than molecular interaction discovery. Full text inaccessible.

## Scan Log: 2026-03-11 (first run)

- **Scan method**: Web search fallback (bioRxiv API and website blocked by egress proxy)
- **Papers found at Tier 1**: 8 new papers not previously processed (filtered against 2026-03-10 scan)
- **Papers reviewed at Tier 2**: 1 (top scorer with relevance >= 0.6)
- **Papers analyzed at Tier 3**: 1 (rated must_read)
- **Networks published to NDEx**: 0 (credentials still missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API and website blocked by egress proxy; NDEx config.json not found

### Tier 1 Papers (scored, new only)

| DOI | Title | Score |
|-----|-------|-------|
| 10.64898/2025.12.10.693272 | The Incoming Influenza Genome Assembles a Host RBP Network | 0.92 |
| 10.64898/2026.01.08.698527 | HA 162-164 deletions enhance influenza B/Victoria fitness | 0.60 |
| 10.64898/2026.02.07.704474 | Efficient replication of influenza D virus in human airway | 0.55 |
| 10.64898/2025.12.06.692757 | Innate antiviral readiness drives T stem cell memory | 0.55 |
| 10.64898/2026.03.03.709407 | Hybrid alphavirus-influenza pseudovirions | 0.45 |
| 10.64898/2026.02.10.704996 | H3N2 antigenic characterisation (positions 158, 189) | 0.40 |
| 10.64898/2026.01.17.700109 | Recombinant H5N1 reporter viruses | 0.35 |
| 10.64898/2026.03.03.709308 | H5 mRNA-LNP vaccine in dairy cows | 0.30 |

### Tier 2 Reviews Summary

1. **Host RBP Network (must_read)**: VIR-CLASP maps ~700 host RBPs recruited by incoming IAV genome. GMPS, TOP2A, SRRM2, SPEN identified as critical proviral factors at distinct replication stages. vRNA reframed as active scaffold for host machinery assembly.

### Tier 3 Analyses Summary

1 paper rated **high field impact**:
- Host RBP Network: 11 molecular interactions mapped, 12 network nodes. 4 novel proviral factors (GMPS, TOP2A, SRRM2, SPEN). Existing pharmacological inhibitors available for TOP2A and GMPS. Paradigm shift in understanding early IAV infection.

## Papers Read

| DOI | Title | Key Claims | Network |
|-----|-------|------------|---------|
| 10.64898/2026.03.05.709812 | c-Fos/M2 stabilization | c-Fos binds M2, prevents degradation, positive feedback via calcium | scan_2026-03-10/tier3_analysis_network_1.json |
| 10.64898/2026.01.15.699784 | ncISG15 restricts IAV | Novel ISG15 isoform inhibits polymerase, resists NS1 | scan_2026-03-10/tier3_analysis_network_2.json |
| 10.64898/2026.01.30.702929 | PA-X dual immune roles | IFN-lambda suppression, MHC I disruption, bystander ISG suppression | scan_2026-03-10/tier3_analysis_network_3.json |
| 10.64898/2025.12.10.693272 | Host RBP Network (VIR-CLASP) | ~700 RBPs recruited by incoming vRNA; GMPS, TOP2A, SRRM2, SPEN proviral | scan_2026-03-11/tier3_analysis_network_1.json |

## Active Threads

(No active threads — folder-based communication pending NDEx 3 folder API.)

## Notes and Observations

- **Emerging theme (continued)**: The Host RBP Network paper adds a fourth facet to the picture of IAV host manipulation strategies: (4) the incoming genome itself acts as a molecular scaffold that recruits and assembles host nuclear machinery before any viral proteins are made. This pre-protein phase of host co-option is striking — it means the virus begins reprogramming the host cell at the moment of nuclear import, using its genome as both template and organizer.
- **Cross-paper connection**: SRRM2 from the Host RBP paper splices the same M segment that produces M2 — the viral protein stabilized by c-Fos in the c-Fos/M2 paper (2026-03-10 scan). Together, these suggest a two-step host dependency: SRRM2 is needed to produce M2 via splicing, and c-Fos is needed to stabilize it post-translationally. Similarly, SRRM2 splices the NS segment to produce NS1 — the very protein that the ncISG15 isoform from the ncISG15 paper escapes antagonism by. This creates a coherent mechanistic narrative across multiple papers.
- **Methodological note**: This scan again used web search fallback due to bioRxiv API being blocked by egress proxy. Coverage remains limited. The IBV HA deletion paper (score 0.60) was borderline for Tier 2 but was not reviewed because full-text access was blocked and the paper focuses on influenza B rather than influenza A.
- **H5N1 zoonotic thread**: The supplementary scan picked up a cat neuroinvasion paper (H5N1 B3.13 vs D1.1) that complements the bovine H5N1 paper from the 2026-03-10 scan. Together with the H5N1 polymerase/ANP32 adaptation paper, these form a growing cluster of H5N1 cross-species adaptation studies. The cat paper is notable for defining the hematogenous route of CNS invasion and showing genotype-dependent transmission — the B3.13 genotype (which dominates in US dairy cattle) transmits efficiently between cats while D1.1 does not.
- **New leads (scan c)**: Two older HPMI-relevant papers not previously processed were flagged during web search: (1) IFIT3 RNA-binding promotes IAV infection — counterintuitive pro-viral role for an ISG family member, direct RNA interactions validated by EMSA; (2) In-cell cross-linking MS interactome during IAV infection — comprehensive protein contact map, paraspeckle disruption, new host factors. Both complement the Host RBP Network paper. Should be reviewed in next scan if they receive new versions or if expanding the scan window.
- **Action needed (persistent)**: Configure NDEx credentials in ~/.ndex/config.json with profile "rdaneel" to enable network publishing. There are now 17 unpublished network artifacts across four scans.
- **Cumulative unpublished networks**: 21 (10 from 2026-03-10, 4 from 2026-03-11 first scan, 2 from 2026-03-11 supplementary, 1 from 2026-03-11 scan c, 1 from 2026-03-11 scan d, 1 from 2026-03-11 scan e, 1 from 2026-03-12 scan f, 1 from 2026-03-12 scan g)
- **Scan d observation**: The bioRxiv HPMI publication rate for influenza appears to have slowed over the past 3 days (March 8-11). No new papers were posted within this window. The two previously missed papers found (RNA secondary structures, IFN heterogeneity) both scored below 0.6 — neither directly addresses host-pathogen molecular interactions at the protein level. The field may be in a brief lull between preprint waves.
- **Scan e observation**: Confirms the lull observed in scan d — still no new HPMI papers within the March 8-11 window after five independent scans. Four previously unidentified papers were found outside the window, all within the H5N1 dairy/zoonotic cluster or epidemiological focus. The bovine mammary H5N1 cytokine paper (March 6, score 0.55) adds immunological depth to the dairy H5N1 cluster but focuses on cytokine profiling rather than specific protein-protein interactions. The H5N1 dairy research cluster now includes 6 papers: bovine nasal epithelium replication, neuroinvasion in cats, mRNA vaccine, natural immunity, polymerase/ANP32 adaptation, and now mammary cytokine networks. Together these paint a comprehensive picture of H5N1 B3.13 cross-species biology, though most are at the immunological/cellular level rather than the molecular interaction level that HPMI triage prioritizes.
- **IFIT3 publication note**: The IFIT3 pro-viral RNA-binding paper (previously flagged) is now formally published in Journal of Virology. This validates the finding and removes it from the "pending review" list. The finding that an ISG family member acts pro-virally during IAV infection via RNA binding complements the Host RBP Network paper's identification of ~700 host RBPs recruited to viral RNA.
- **Scan f observation (2026-03-12)**: Sixth consecutive scan with no new HPMI papers within the 3-day window. The publication lull for influenza HPMI preprints has now extended from March 7 through March 12 — 6 days without a new relevant paper. Two previously unidentified papers were found outside the window: the H5N1 dry Jersey cows pathogenesis paper (March 4, score 0.50) expands the dairy H5N1 cluster to 7 papers — it demonstrates that dry cows are also highly susceptible to intramammary H5N1, recapitulating severe disease seen in lactating cows. The antigen-prime computational tool (January 23, score 0.20) is outside HPMI scope. The IBV HA deletions paper received a v2 revision but remains an IBV study below the Tier 2 review threshold for the HPMI group's IAV focus. The dairy H5N1 cluster now includes: bovine nasal epithelium replication, neuroinvasion in cats, mRNA vaccine, natural immunity, polymerase/ANP32 adaptation, mammary cytokine networks, and dry cow pathogenesis.
- **Action needed (persistent)**: Configure NDEx credentials in ~/.ndex/config.json with profile "rdaneel" to enable network publishing. There are now 20 unpublished network artifacts across six scans.

## Scan Log: 2026-03-10 (previous)

- **Scan method**: Web search fallback (bioRxiv API blocked by proxy)
- **Papers found at Tier 1**: 8 papers matched HPMI keywords
- **Papers reviewed at Tier 2**: 3 (top scorers with relevance >= 0.6, limited by full-text access)
- **Papers analyzed at Tier 3**: 3 (all rated must_read)
- **Networks published to NDEx**: 0 (credentials missing at ~/.ndex/config.json)
- **Errors**: bioRxiv API and website blocked by egress proxy; NDEx config.json not found

### Tier 1 Papers from 2026-03-10 (scored)

| DOI | Title | Score |
|-----|-------|-------|
| 10.64898/2026.03.05.709812 | c-Fos enhances IAV replication via M2 stabilization | 0.95 |
| 10.64898/2026.01.15.699784 | Novel ISG15 transcript restricts IAV | 0.92 |
| 10.64898/2026.01.30.702929 | PA-X dual roles: IFN suppression + MHC I disruption | 0.90 |
| 10.1101/2025.01.06.631435 | H5N1 polymerase mutations / ANP32 adaptation | 0.80 |
| 10.64898/2026.01.16.699876 | Bovine H5N1 replication in human nasal epithelium | 0.75 |
| 10.64898/2026.01.20.700505 | Antiviral compound targeting host metabolic pathway | 0.65 |
| 10.64898/2026.02.18.706711 | Antibody landscape to influenza (vaccine selection) | 0.50 |
| 10.64898/2026.03.03.709347 | Parainfluenza HN antibodies (not influenza) | 0.35 |

### Tier 2 Reviews from 2026-03-10 Summary

1. **c-Fos/M2 (must_read)**: Novel proviral feedback loop — M2 calcium → c-Fos → M2 stabilization → autophagosome accumulation. Therapeutic target potential.
2. **ncISG15 (must_read)**: New ISG15 isoform that restricts IAV polymerase, escapes NS1 antagonism. ISGylation-independent mechanism.
3. **PA-X dual roles (must_read)**: PA-X suppresses IFN-lambda, bystander ISG expression, AND MHC I presentation. 3D airway model.

### Tier 3 Analyses from 2026-03-10 Summary

All 3 papers rated **high field impact**:
- c-Fos/M2: 12 molecular interactions mapped, 21 network nodes. Druggable host dependency.
- ncISG15: 10 interactions mapped, 9 nodes. Novel restriction factor paradigm.
- PA-X: 11 interactions mapped, 12 nodes. Multi-axis immune evasion.
