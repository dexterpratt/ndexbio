/**
 * NDEx public REST API client — v2
 * Browser-side, no auth required.
 */

// Read server URL from window.SYMPOSIUM_CONFIG at call time so runtime config
// (config.js / config.json) can redirect to a local NDEx, a demo host, etc.
// Falls back to the public NDEx if no config is loaded.
const DEFAULT_NDEX_SERVER = 'https://www.ndexbio.org';
function _ndexServer() {
  const cfg = (typeof window !== 'undefined' && window.SYMPOSIUM_CONFIG) || null;
  return (cfg && cfg.ndex && cfg.ndex.server) || DEFAULT_NDEX_SERVER;
}
function _v2Base() { return `${_ndexServer()}/v2`; }

// ── Simple cache ──────────────────────────────────────────────────────────────

const _cache = new Map();

function _cacheGet(key) {
    const entry = _cache.get(key);
    if (!entry) return null;
    if (Date.now() > entry.expires) { _cache.delete(key); return null; }
    return entry.value;
}
function _cacheSet(key, value, ttlMs) {
    _cache.set(key, { value, expires: Date.now() + ttlMs });
}

const TTL_SUMMARY = 5 * 60 * 1000;   // 5 min
const TTL_FULL    = 30 * 60 * 1000;  // 30 min

// ── API client ────────────────────────────────────────────────────────────────

const NdexApi = {

    /** Check server reachability. */
    async checkStatus() {
        try {
            const r = await fetch(`${_v2Base()}/admin/status`, { method: 'GET' });
            return r.ok;
        } catch { return false; }
    },

    /** Search networks by keyword + optional accountName filter. */
    async searchNetworks(query, start = 0, size = 20, accountName = null) {
        const body = { searchString: query };
        if (accountName) body.accountName = accountName;
        const r = await fetch(`${_v2Base()}/search/network?start=${start}&size=${size}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!r.ok) throw new Error(`Search failed: ${r.status}`);
        return r.json();
    },

    /**
     * Get ALL public networks for an account, paginating until exhausted.
     * Uses size=100 pages.  Max 1000 networks.
     */
    async getUserNetworksFull(username) {
        const cacheKey = `user_networks_full:${username}`;
        const cached = _cacheGet(cacheKey);
        if (cached) return cached;

        const all = [];
        let start = 0;
        const size = 100;
        while (true) {
            const data = await this.searchNetworks('*', start, size, username);
            const nets = data.networks || [];
            all.push(...nets);
            if (nets.length < size) break;
            start += size;
            if (start >= 1000) break;
        }
        _cacheSet(cacheKey, all, TTL_SUMMARY);
        return all;
    },

    /** Get network summary (metadata + properties). */
    async getNetworkSummary(networkId) {
        const cacheKey = `summary:${networkId}`;
        const cached = _cacheGet(cacheKey);
        if (cached) return cached;
        const r = await fetch(`${_v2Base()}/network/${networkId}/summary`);
        if (!r.ok) throw new Error(`Summary failed: ${r.status}`);
        const data = await r.json();
        _cacheSet(cacheKey, data, TTL_SUMMARY);
        return data;
    },

    /** Download full CX2 network. */
    async downloadNetwork(networkId) {
        const cacheKey = `full:${networkId}`;
        const cached = _cacheGet(cacheKey);
        if (cached) return cached;
        const r = await fetch(`${_v2Base()}/network/${networkId}`);
        if (!r.ok) throw new Error(`Download failed: ${r.status}`);
        const data = await r.json();
        _cacheSet(cacheKey, data, TTL_FULL);
        return data;
    },

    /**
     * Parse a CX stream (CX1 or CX2) into a unified structure:
     *   { nodes: [{id, v:{name,...}}, ...],
     *     edges: [{id, s, t, v:{interaction,...}}, ...],
     *     networkAttributes: {key: value, ...},
     *     visualProperties: [...] }
     */
    parseCX(cxData) {
        const result = { nodes: [], edges: [], networkAttributes: {}, visualProperties: [] };
        if (!Array.isArray(cxData)) return result;

        const isCX1 = cxData.some(asp =>
            asp.nodes && asp.nodes.length > 0 && '@id' in asp.nodes[0]
        );
        return isCX1 ? this._parseCX1(cxData, result) : this._parseCX2(cxData, result);
    },

    _parseCX1(cxData, result) {
        const rawNodes = [];
        const nodeAttrs = {};
        const edgeAttrs = {};
        const nodePositions = {};

        for (const asp of cxData) {
            if (asp.nodes) {
                rawNodes.push(...asp.nodes);
            } else if (asp.edges) {
                for (const e of asp.edges) {
                    const eid = e['@id'];
                    if (!edgeAttrs[eid]) edgeAttrs[eid] = {};
                    edgeAttrs[eid]._s = e.s;
                    edgeAttrs[eid]._t = e.t;
                    if (e.i) edgeAttrs[eid].interaction = e.i;
                }
            } else if (asp.nodeAttributes) {
                for (const a of asp.nodeAttributes) {
                    if (!nodeAttrs[a.po]) nodeAttrs[a.po] = {};
                    nodeAttrs[a.po][a.n] = a.v;
                }
            } else if (asp.edgeAttributes) {
                for (const a of asp.edgeAttributes) {
                    if (!edgeAttrs[a.po]) edgeAttrs[a.po] = {};
                    edgeAttrs[a.po][a.n] = a.v;
                }
            } else if (asp.cartesianLayout) {
                for (const pos of asp.cartesianLayout) nodePositions[pos.node] = {x: pos.x, y: pos.y};
            } else if (asp.networkAttributes) {
                for (const a of asp.networkAttributes) result.networkAttributes[a.n] = a.v;
            } else if (asp.cyVisualProperties || asp.visualProperties) {
                result.visualProperties.push(...(asp.cyVisualProperties || asp.visualProperties));
            }
        }

        for (const n of rawNodes) {
            const id = n['@id'];
            const attrs = nodeAttrs[id] || {};
            attrs.name = attrs.name || n.n || n.r || `node_${id}`;
            if (n.r && n.r !== attrs.name) attrs.represents = n.r;
            const node = {id, v: attrs};
            if (nodePositions[id]) { node.x = nodePositions[id].x; node.y = nodePositions[id].y; }
            result.nodes.push(node);
        }
        for (const [eid, attrs] of Object.entries(edgeAttrs)) {
            const s = attrs._s; const t = attrs._t;
            delete attrs._s; delete attrs._t;
            result.edges.push({id: Number(eid), s, t, v: attrs});
        }
        return result;
    },

    _parseCX2(cxData, result) {
        for (const asp of cxData) {
            if (asp.nodes)             result.nodes.push(...asp.nodes);
            else if (asp.edges)        result.edges.push(...asp.edges);
            else if (asp.networkAttributes) {
                for (const a of asp.networkAttributes)
                    result.networkAttributes[a.name || a.n] = a.value ?? a.v;
            } else if (asp.visualProperties) result.visualProperties.push(...asp.visualProperties);
        }
        return result;
    },

    /** Extract ndex- properties from a network summary into a plain object. */
    extractProperties(summaryOrPropsArray) {
        const props = {};
        const list = Array.isArray(summaryOrPropsArray)
            ? summaryOrPropsArray
            : (summaryOrPropsArray.properties || []);
        for (const p of list) {
            const key = p.predicateString || p.name || '';
            if (key) props[key] = p.value ?? '';
        }
        return props;
    },
};
