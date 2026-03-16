# NDEx MCP Conventions

When working with NDEx via the MCP tools, follow these conventions.
Read this file before creating, updating, or searching for networks.

## Naming Conventions

### Property keys: `ndex-` prefix

Use `ndex-<tagname>` for custom property keys set on networks. These are
structured key-value data, not free-text search targets, so hyphens are safe.

Standard property keys for agent-managed networks:

| Key | Value | Purpose |
|-----|-------|---------|
| `ndex-agent` | agent identifier, e.g. `"claude-code"` | Marks the creating agent |
| `ndex-workflow` | workflow name or ID | Links network to a workflow session |
| `ndex-session` | timestamp or session ID | Links to a specific run |
| `ndex-source` | data provenance string | Where the data came from |

### Searchable text: `ndexagent` prefix (no hyphen)

For network names and descriptions — anything that users or agents will
search for via the Lucene-based `search_networks` tool — use `ndexagent`
as a compound word prefix with no hyphen.

**Why:** NDEx search uses Lucene query syntax. Lucene treats `-` as the
NOT operator. Searching for `ndex-test` is parsed as _"ndex NOT test"_,
which returns wrong results. Quoting (`"ndex-test"`) works but is fragile
and easy to forget. The compound form `ndexagent` avoids this entirely.

Examples:
- Network name: `ndexagent TP53 pathway analysis`
- Network name: `ndexagent workflow 20250610`
- Search query: `ndexagent` (finds all agent-created networks)
- Search query: `ndexagent TP53` (finds agent networks mentioning TP53)

### NDEx username restrictions

NDEx rejects special characters in usernames. Stick to alphanumeric
characters and underscores. Do not assume hyphens, dots, or other
punctuation are allowed in usernames.

## Network Spec Format

The `create_network` and `update_network` tools accept a JSON spec string:

```json
{
  "name": "ndexagent My Network",
  "description": "Created by agent for workflow X",
  "version": "1.0",
  "properties": {
    "ndex-agent": "claude-code",
    "ndex-session": "20250610_143022"
  },
  "nodes": [
    {"id": 0, "v": {"name": "TP53", "type": "gene"}},
    {"id": 1, "v": {"name": "MDM2", "type": "gene"}}
  ],
  "edges": [
    {"s": 0, "t": 1, "v": {"interaction": "inhibits"}}
  ]
}
```

Key rules:
- `name` is the only required field
- Node `id` values must be integers (not UUIDs, not strings)
- If `id` is omitted, IDs are auto-assigned starting from 0
- Edge `s` and `t` reference node IDs
- Node/edge attributes go in `v` (a flat dict of key-value pairs)
- The spec is passed as a JSON **string**, not as a dict

## Search Conventions

`search_networks` passes the query to NDEx's Lucene-based search.

Lucene pitfalls:
- `-` is NOT: `TP53 -MDM2` means "TP53 but not MDM2"
- Unquoted hyphens in compound terms are misread (see naming section above)
- `AND`, `OR`, `NOT` are operators when uppercase
- Use quotes for exact phrase: `"cell cycle"`
- Wildcard: `TP5*` matches TP53, TP5, etc.
- Field-specific: `name:ndexagent` searches only the name field

## Indexing and Searchability

NDEx networks default to `index_level: "NONE"`, which means they will not
appear in search results — even if they are PUBLIC. The `create_network` MCP
tool automatically sets `index_level: "ALL"` on newly created networks so
they are searchable by both the owner and (if PUBLIC) other users.

If you create networks outside the MCP tools, set the index level explicitly:

```python
client.set_network_system_properties(network_id, {"index_level": "ALL"})
```

Valid `index_level` values: `NONE`, `META` (index network attributes only),
`ALL` (full index including node/edge content).

## Lifecycle for Agent-Created Networks

1. **Create** with `ndexagent` prefix in name and `ndex-` properties
2. Networks default to **PRIVATE** visibility — keep them private unless
   the workflow explicitly requires public sharing
3. **Clean up**: delete temporary/intermediate networks when the workflow
   completes, unless the user or workflow says to keep them
4. Before deleting, confirm the network is agent-created by checking for
   `ndex-agent` in its properties

## Common Pitfalls

- **Auth required for writes**: create, update, delete, visibility, sharing
  all require valid credentials in `~/.ndex/config.json`
- **Server indexing lag**: after creating a network, wait 1-2 seconds before
  searching for it or getting its summary
- **CX2 format only**: the MCP tools work with CX2, not the legacy CX format
- **UUID format**: network IDs are standard UUIDs like
  `a1f40bf7-5f02-11e9-9f06-0ac135e8bacf` — do not strip hyphens from UUIDs
  (hyphens in UUIDs are fine; the Lucene issue only applies to search queries)
