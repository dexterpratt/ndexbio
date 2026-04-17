/**
 * NDEx REST API client for local development server.
 * Points at localhost:8080 (Docker NDEx container).
 * All networks are expected to be PUBLIC on local instance.
 */

const NDEX_SERVER = 'http://127.0.0.1:8080';
const V2_BASE = `${NDEX_SERVER}/v2`;

const NdexApi = {

    /**
     * Search for networks by keyword.
     * Returns {networks: [...], numFound: N}.
     */
    async searchNetworks(query, start = 0, size = 100) {
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
     * Get networks owned by a user via search with accountName filter.
     */
    async getUserNetworks(username, offset = 0, limit = 100) {
        const resp = await fetch(`${V2_BASE}/search/network?start=${offset}&size=${limit}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ searchString: '*', accountName: username }),
        });
        if (!resp.ok) throw new Error(`User networks failed: ${resp.status}`);
        const data = await resp.json();
        return data.networks || [];
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
     * Returns: { nodes, edges, networkAttributes, visualProperties }
     */
    parseCX(cxData) {
        const result = {
            nodes: [],
            edges: [],
            networkAttributes: {},
            visualProperties: [],
        };

        if (!Array.isArray(cxData)) return result;

        const isCX1 = cxData.some(aspect =>
            aspect.nodes && aspect.nodes.length > 0 && '@id' in aspect.nodes[0]
        );

        if (isCX1) return this._parseCX1(cxData, result);
        return this._parseCX2(cxData, result);
    },

    _parseCX1(cxData, result) {
        const rawNodes = [];
        const nodeAttrs = {};
        const edgeAttrs = {};
        const nodePositions = {};

        for (const aspect of cxData) {
            if (aspect.nodes) {
                for (const n of aspect.nodes) rawNodes.push(n);
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

        for (const n of rawNodes) {
            const id = n['@id'];
            const attrs = nodeAttrs[id] || {};
            attrs.name = attrs.name || n.n || n.r || `node_${id}`;
            if (n.r && n.r !== attrs.name) attrs.represents = n.r;
            const node = { id, v: attrs };
            if (nodePositions[id]) {
                node.x = nodePositions[id].x;
                node.y = nodePositions[id].y;
            }
            result.nodes.push(node);
        }

        for (const [edgeId, attrs] of Object.entries(edgeAttrs)) {
            const s = attrs._s;
            const t = attrs._t;
            delete attrs._s;
            delete attrs._t;
            result.edges.push({ id: Number(edgeId), s, t, v: attrs });
        }

        return result;
    },

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
     * Extract properties from a network summary into a flat object.
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
