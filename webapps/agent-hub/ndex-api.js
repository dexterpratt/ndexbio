/**
 * NDEx public REST API client (browser-side, no auth).
 *
 * All reads go through the NDEx v3 REST API via fetch().
 * CORS: NDEx public endpoints support cross-origin requests.
 */

const NDEX_SERVER = 'https://www.ndexbio.org';
const V2_BASE = `${NDEX_SERVER}/v2`;

const NdexApi = {

    /**
     * Search for networks by keyword.
     * Returns {networks: [...], numFound: N}.
     */
    async searchNetworks(query, start = 0, size = 20) {
        const resp = await fetch(`${V2_BASE}/search/network?start=${start}&size=${size}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ searchString: query }),
        });
        if (!resp.ok) throw new Error(`Search failed: ${resp.status}`);
        return resp.json();
    },

    /**
     * Get network summary (metadata, properties, node/edge counts).
     */
    async getNetworkSummary(networkId) {
        const resp = await fetch(`${V2_BASE}/network/${networkId}/summary`);
        if (!resp.ok) throw new Error(`Summary failed: ${resp.status}`);
        return resp.json();
    },

    /**
     * Download full network in CX2 format.
     */
    async downloadNetwork(networkId) {
        const resp = await fetch(`${V2_BASE}/network/${networkId}`);
        if (!resp.ok) throw new Error(`Download failed: ${resp.status}`);
        return resp.json();
    },

    /**
     * Get public networks owned by a user (no auth required).
     * Uses search API with account_name filter instead of the
     * authenticated user endpoint.
     */
    async getUserNetworks(username, offset = 0, limit = 20) {
        const resp = await fetch(`${V2_BASE}/search/network?start=${offset}&size=${limit}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ searchString: '*', accountName: username }),
        });
        if (!resp.ok) throw new Error(`User networks failed: ${resp.status}`);
        const data = await resp.json();
        // Return the networks array to match the expected format
        return data.networks || [];
    },

    /**
     * Get user profile info (externalId, displayName, etc).
     * The user lookup endpoint is public.
     */
    async getUserProfile(username) {
        const resp = await fetch(`${V2_BASE}/user?username=${encodeURIComponent(username)}`);
        if (!resp.ok) throw new Error(`User lookup failed: ${resp.status}`);
        return resp.json();
    },

    /**
     * Check server connectivity.
     */
    async checkStatus() {
        try {
            const resp = await fetch(`${V2_BASE}/admin/status`, { method: 'GET' });
            return resp.ok;
        } catch {
            return false;
        }
    },

    /**
     * Parse a CX stream (v1 or v2) into a unified structure.
     *
     * CX1 format: array of aspect objects like {nodes: [{@id, n, r}, ...]},
     *   {edges: [{@id, s, t, i}, ...]}, {nodeAttributes: [{po, n, v}, ...]}
     * CX2 format: array of aspect objects like {nodes: [{id, v: {name, ...}}, ...]},
     *   {edges: [{id, s, t, v: {interaction, ...}}, ...]}
     *
     * Returns a unified format:
     *   nodes: [{id, v: {name, ...}}, ...]
     *   edges: [{id, s, t, v: {interaction, ...}}, ...]
     */
    parseCX(cxData) {
        const result = {
            nodes: [],
            edges: [],
            networkAttributes: {},
            visualProperties: [],
        };

        if (!Array.isArray(cxData)) return result;

        // Detect format: CX1 nodes have @id, CX2 nodes have id
        const isCX1 = cxData.some(aspect =>
            aspect.nodes && aspect.nodes.length > 0 && '@id' in aspect.nodes[0]
        );

        if (isCX1) {
            return this._parseCX1(cxData, result);
        }
        return this._parseCX2(cxData, result);
    },

    /** Parse CX1 format into unified structure. */
    _parseCX1(cxData, result) {
        const rawNodes = [];   // {po (node id), n (attr name), v (attr value), d (datatype)}
        const nodeAttrs = {};  // nodeId -> {attrName: value}
        const edgeAttrs = {};  // edgeId -> {attrName: value}
        const nodePositions = {};  // nodeId -> {x, y}

        for (const aspect of cxData) {
            if (aspect.nodes) {
                for (const n of aspect.nodes) {
                    rawNodes.push(n);
                }
            } else if (aspect.edges) {
                for (const e of aspect.edges) {
                    const edgeId = e['@id'];
                    if (!edgeAttrs[edgeId]) edgeAttrs[edgeId] = {};
                    edgeAttrs[edgeId]._s = e.s;
                    edgeAttrs[edgeId]._t = e.t;
                    if (e.i) edgeAttrs[edgeId].interaction = e.i;
                }
            } else if (aspect.nodeAttributes) {
                for (const a of aspect.nodeAttributes) {
                    const nodeId = a.po;
                    if (!nodeAttrs[nodeId]) nodeAttrs[nodeId] = {};
                    nodeAttrs[nodeId][a.n] = a.v;
                }
            } else if (aspect.edgeAttributes) {
                for (const a of aspect.edgeAttributes) {
                    const edgeId = a.po;
                    if (!edgeAttrs[edgeId]) edgeAttrs[edgeId] = {};
                    edgeAttrs[edgeId][a.n] = a.v;
                }
            } else if (aspect.cartesianLayout) {
                for (const pos of aspect.cartesianLayout) {
                    nodePositions[pos.node] = { x: pos.x, y: pos.y };
                }
            } else if (aspect.networkAttributes) {
                for (const a of aspect.networkAttributes) {
                    result.networkAttributes[a.n] = a.v;
                }
            } else if (aspect.cyVisualProperties || aspect.visualProperties) {
                const vp = aspect.cyVisualProperties || aspect.visualProperties;
                result.visualProperties.push(...vp);
            }
        }

        // Build unified nodes (with positions if available)
        for (const n of rawNodes) {
            const id = n['@id'];
            const attrs = nodeAttrs[id] || {};
            attrs.name = attrs.name || n.n || n.r || `node_${id}`;
            if (n.r && n.r !== attrs.name) attrs.represents = n.r;
            const node = { id: id, v: attrs };
            if (nodePositions[id]) {
                node.x = nodePositions[id].x;
                node.y = nodePositions[id].y;
            }
            result.nodes.push(node);
        }

        // Build unified edges
        for (const [edgeId, attrs] of Object.entries(edgeAttrs)) {
            const s = attrs._s;
            const t = attrs._t;
            delete attrs._s;
            delete attrs._t;
            result.edges.push({ id: Number(edgeId), s: s, t: t, v: attrs });
        }

        return result;
    },

    /** Parse CX2 format into unified structure. */
    _parseCX2(cxData, result) {
        for (const aspect of cxData) {
            if (aspect.nodes) result.nodes.push(...aspect.nodes);
            else if (aspect.edges) result.edges.push(...aspect.edges);
            else if (aspect.networkAttributes) {
                for (const attr of aspect.networkAttributes) {
                    result.networkAttributes[attr.name || attr.n] = attr.value || attr.v;
                }
            } else if (aspect.visualProperties) {
                result.visualProperties.push(...aspect.visualProperties);
            }
        }
        return result;
    },

    /**
     * Extract ndex- properties from a network summary's properties array.
     */
    extractProperties(summary) {
        const props = {};
        const propList = summary.properties || [];
        for (const p of propList) {
            const key = p.predicateString || p.name || '';
            const val = p.value || '';
            if (key) props[key] = val;
        }
        return props;
    },
};
