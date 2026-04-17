/**
 * Agent Hub Dev — local NDEx agent browser + network viewer.
 *
 * Views: Browse (agent list + network cards), Network Viewer.
 * All data from local NDEx at 127.0.0.1:8080.
 */

// ============================================================
// Network Type Detection
// ============================================================

const NETWORK_TYPE_CONFIG = {
    'plans':            { label: 'Plans',           badgeClass: 'badge-self-knowledge' },
    'session-history':  { label: 'Session History', badgeClass: 'badge-self-knowledge' },
    'collaborator-map': { label: 'Collaborators',   badgeClass: 'badge-self-knowledge' },
    'papers-read':      { label: 'Papers Read',     badgeClass: 'badge-self-knowledge' },
    'expertise':        { label: 'Expertise',       badgeClass: 'badge-expertise' },
    'knowledge-base':   { label: 'Knowledge Base',  badgeClass: 'badge-knowledge-base' },
    'triage':           { label: 'Triage',          badgeClass: 'badge-triage' },
    'analysis':         { label: 'Analysis',        badgeClass: 'badge-analysis' },
    'review':           { label: 'Review',          badgeClass: 'badge-review' },
    'critique':         { label: 'Critique',        badgeClass: 'badge-critique' },
    'synthesis':        { label: 'Synthesis',       badgeClass: 'badge-synthesis' },
    'request':          { label: 'Request',         badgeClass: 'badge-request' },
    'report':           { label: 'Report',          badgeClass: 'badge-report' },
};

/**
 * Detect network type from name and properties.
 */
function detectNetworkType(net) {
    const props = extractProps(net);
    const workflow = (props['ndex-workflow'] || '').toLowerCase();
    const dataType = (props['ndex-data-type'] || '').toLowerCase();
    const messageType = (props['ndex-message-type'] || '').toLowerCase();
    const name = (net.name || '').toLowerCase();

    // Check properties first
    for (const key of Object.keys(NETWORK_TYPE_CONFIG)) {
        if (workflow.includes(key) || dataType.includes(key) || messageType === key) {
            return key;
        }
    }

    // Name pattern matching — self-knowledge networks
    if (name.includes('-plans')) return 'plans';
    if (name.includes('session-history')) return 'session-history';
    if (name.includes('collaborator-map') || name.includes('collaborator')) return 'collaborator-map';
    if (name.includes('papers-read')) return 'papers-read';
    if (name.includes('expertise') || name.includes('expertise guide')) return 'expertise';
    if (name.includes('knowledge base') || name.includes('knowledge-base')) return 'knowledge-base';
    if (name.includes('triage')) return 'triage';

    // Content network patterns
    if (name.includes('review')) return 'review';
    if (name.includes('critique')) return 'critique';
    if (name.includes('synthesis')) return 'synthesis';
    if (name.includes('analysis')) return 'analysis';
    if (name.includes('request')) return 'request';
    if (name.includes('report')) return 'report';

    return null;
}

/**
 * Classify a network type into a broader category for grouping.
 */
function typeCategory(type) {
    if (['plans', 'session-history', 'collaborator-map', 'papers-read'].includes(type)) return 'self-knowledge';
    if (['expertise', 'knowledge-base'].includes(type)) return 'expertise';
    return 'content';
}

// ============================================================
// Navigation
// ============================================================

document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`view-${btn.dataset.view}`).classList.add('active');
        document.getElementById('uuid-popover').style.display = 'none';
    });
});

// ============================================================
// Server status check
// ============================================================

(async function checkServer() {
    const dot = document.getElementById('server-status');
    const ok = await NdexApi.checkStatus();
    dot.classList.toggle('ok', ok);
    dot.classList.toggle('err', !ok);
})();

// ============================================================
// Utility
// ============================================================

function escHtml(str) {
    const el = document.createElement('span');
    el.textContent = str;
    return el.innerHTML;
}

function relativeTime(timestamp) {
    if (!timestamp) return '';
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    const d = new Date(timestamp);
    const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return `${monthNames[d.getMonth()]} ${d.getDate()}`;
}

function extractProps(net) {
    const props = {};
    if (net.properties) {
        for (const p of net.properties) {
            props[p.predicateString || p.name || ''] = p.value || '';
        }
    }
    return props;
}

/**
 * Strip known agent prefixes from network name.
 */
function cleanNetworkName(name) {
    if (!name) return 'Untitled';
    // Strip "ndexagent <username> " prefix
    const prefix = /^ndexagent\s+\w+\s+/i;
    const match = name.match(prefix);
    if (match) return name.slice(match[0].length);
    // Strip bare "ndexagent " prefix
    if (name.toLowerCase().startsWith('ndexagent ')) return name.slice(10);
    return name;
}

/**
 * Generate a stable color from a string (username).
 */
function stringColor(str) {
    const colors = ['#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#e53e3e', '#38b2ac', '#d69e2e', '#667eea'];
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

// ============================================================
// Browse View — Agent Discovery + Network Cards
// ============================================================

let allNetworks = [];
let agentMap = {};  // username -> { networks: [], color }
let selectedAgent = null;

async function loadAgents() {
    const agentListEl = document.getElementById('agent-list');
    agentListEl.innerHTML = '<p class="placeholder">Loading...</p>';

    try {
        // Search for all networks on local server
        const data = await NdexApi.searchNetworks('*', 0, 200);
        allNetworks = data.networks || [];

        // Group by owner to discover agents
        agentMap = {};
        for (const net of allNetworks) {
            const owner = net.owner || 'unknown';
            if (!agentMap[owner]) {
                agentMap[owner] = {
                    username: owner,
                    networks: [],
                    color: stringColor(owner),
                };
            }
            agentMap[owner].networks.push(net);
        }

        // Sort agents by network count descending
        const agents = Object.values(agentMap).sort((a, b) => b.networks.length - a.networks.length);

        renderAgentList(agents);

        // Auto-select first agent if any
        if (agents.length > 0) {
            selectAgent(agents[0].username);
        }
    } catch (err) {
        agentListEl.innerHTML = `<p class="placeholder">Error: ${escHtml(err.message)}<br><br>Is NDEx running at 127.0.0.1:8080?</p>`;
    }
}

function renderAgentList(agents) {
    const agentListEl = document.getElementById('agent-list');
    agentListEl.innerHTML = '';

    if (agents.length === 0) {
        agentListEl.innerHTML = '<p class="placeholder">No agents found.</p>';
        return;
    }

    for (const agent of agents) {
        const item = document.createElement('div');
        item.className = 'agent-list-item' + (agent.username === selectedAgent ? ' active' : '');
        item.dataset.username = agent.username;

        const initial = agent.username.charAt(0).toUpperCase();

        item.innerHTML = `
            <div class="agent-list-avatar" style="background:${agent.color}20;color:${agent.color}">${initial}</div>
            <div class="agent-list-info">
                <div class="agent-list-name">${escHtml(agent.username)}</div>
                <div class="agent-list-count">${agent.networks.length} network${agent.networks.length !== 1 ? 's' : ''}</div>
            </div>
        `;

        item.addEventListener('click', () => selectAgent(agent.username));
        agentListEl.appendChild(item);
    }
}

function selectAgent(username) {
    selectedAgent = username;
    const agent = agentMap[username];
    if (!agent) return;

    // Update sidebar active state
    document.querySelectorAll('.agent-list-item').forEach(el => {
        el.classList.toggle('active', el.dataset.username === username);
    });

    // Update header
    document.getElementById('selected-agent-name').textContent = username;
    document.getElementById('selected-agent-count').textContent =
        `${agent.networks.length} network${agent.networks.length !== 1 ? 's' : ''}`;

    // Sort networks: self-knowledge first, then expertise, then content. Within each, by mod time.
    const categoryOrder = { 'self-knowledge': 0, 'expertise': 1, 'content': 2 };
    const sorted = [...agent.networks].sort((a, b) => {
        const typeA = detectNetworkType(a);
        const typeB = detectNetworkType(b);
        const catA = categoryOrder[typeCategory(typeA)] ?? 2;
        const catB = categoryOrder[typeCategory(typeB)] ?? 2;
        if (catA !== catB) return catA - catB;
        return (b.modificationTime || 0) - (a.modificationTime || 0);
    });

    renderNetworkCards(sorted);
}

function renderNetworkCards(networks) {
    const container = document.getElementById('network-cards');
    container.innerHTML = '';

    if (networks.length === 0) {
        container.innerHTML = '<p class="placeholder">No networks for this agent.</p>';
        return;
    }

    for (const net of networks) {
        const card = document.createElement('div');
        card.className = 'network-card';
        card.addEventListener('click', () => openNetworkViewer(net.externalId));

        const displayName = cleanNetworkName(net.name);
        const netType = detectNetworkType(net);
        const typeConfig = netType ? NETWORK_TYPE_CONFIG[netType] : null;

        // Badges
        const badges = [];
        if (typeConfig) {
            badges.push(`<span class="stat-badge ${typeConfig.badgeClass}">${typeConfig.label}</span>`);
        }
        if (net.nodeCount) badges.push(`<span class="stat-badge stat-nodes">${net.nodeCount} nodes</span>`);
        if (net.edgeCount) badges.push(`<span class="stat-badge stat-edges">${net.edgeCount} edges</span>`);

        // Description truncated
        const desc = net.description || '';
        const truncated = desc.length > 120 ? desc.substring(0, 120).replace(/\s+\S*$/, '') + '...' : desc;

        card.innerHTML = `
            <div class="network-card-name">${escHtml(displayName)}</div>
            <div class="network-card-badges">${badges.join('')}</div>
            ${truncated ? `<div class="network-card-desc">${escHtml(truncated)}</div>` : ''}
            <div class="network-card-time">${relativeTime(net.modificationTime)}</div>
        `;

        container.appendChild(card);
    }
}

// ============================================================
// Network Viewer
// ============================================================

const viewerUuid = document.getElementById('viewer-uuid');
const viewerLoadBtn = document.getElementById('viewer-load-btn');
const viewerContent = document.getElementById('viewer-content');
const uuidPopover = document.getElementById('uuid-popover');
const getByUuidBtn = document.getElementById('get-by-uuid-btn');

// UUID popover toggle
getByUuidBtn.addEventListener('click', () => {
    const isOpen = uuidPopover.style.display !== 'none';
    uuidPopover.style.display = isOpen ? 'none' : 'flex';
    if (!isOpen) {
        viewerUuid.focus();
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.querySelector('[data-view="network"]').classList.add('active');
        document.getElementById('view-network').classList.add('active');
    }
});
document.addEventListener('click', (e) => {
    if (!uuidPopover.contains(e.target) && e.target !== getByUuidBtn) {
        uuidPopover.style.display = 'none';
    }
});

viewerLoadBtn.addEventListener('click', () => {
    loadNetwork(viewerUuid.value.trim());
    uuidPopover.style.display = 'none';
});
viewerUuid.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
        loadNetwork(viewerUuid.value.trim());
        uuidPopover.style.display = 'none';
    }
    if (e.key === 'Escape') uuidPopover.style.display = 'none';
});

let cy = null;

function openNetworkViewer(networkId) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelector('[data-view="network"]').classList.add('active');
    document.getElementById('view-network').classList.add('active');

    loadNetwork(networkId);
}

async function loadNetwork(networkId) {
    if (!networkId) return;

    viewerContent.style.display = 'none';
    document.getElementById('viewer-details').style.display = 'none';

    try {
        const [summary, cx2Data] = await Promise.all([
            NdexApi.getNetworkSummary(networkId),
            NdexApi.downloadNetwork(networkId),
        ]);

        renderNetworkSidebar(summary);
        viewerContent.style.display = 'block';
        renderGraph(cx2Data, summary);
    } catch (err) {
        viewerContent.style.display = 'block';
        document.getElementById('viewer-name').textContent = 'Error loading network';
        document.getElementById('viewer-meta').textContent = err.message;
        document.getElementById('viewer-description').innerHTML = '';
        document.getElementById('viewer-properties').innerHTML = '';
    }
}

const HIDDEN_PROPERTIES = new Set(['ndex-agent', 'ndex-interest-group', 'ndex-property-order']);

function formatPropValue(key, value) {
    const str = String(value);
    if (key === 'ndex-paper-doi' && str.startsWith('10.')) {
        return `<a href="https://doi.org/${escHtml(str)}" target="_blank" rel="noopener">${escHtml(str)}</a>`;
    }
    if (/^[0-9a-f-]{36}$/i.test(str)) {
        return `<a href="#${escHtml(str)}" class="uuid-link">${escHtml(str)}</a>`;
    }
    return escHtml(str);
}

function renderNetworkSidebar(summary) {
    const displayName = cleanNetworkName(summary.name);
    document.getElementById('viewer-name').textContent = displayName;

    const meta = document.getElementById('viewer-meta');
    const props = NdexApi.extractProperties(summary);

    let metaHtml = '';
    const line1 = [];
    if (summary.owner) line1.push(`<span class="viewer-meta-owner">${escHtml(summary.owner)}</span>`);
    if (summary.modificationTime) line1.push(escHtml(relativeTime(summary.modificationTime)));
    if (line1.length) metaHtml += `<div class="viewer-meta-line">${line1.join(' \u2013 ')}</div>`;
    meta.innerHTML = metaHtml;

    // Description with markdown
    const desc = summary.description || '';
    const descEl = document.getElementById('viewer-description');
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
        descEl.innerHTML = DOMPurify.sanitize(marked.parse(desc));
    } else {
        descEl.textContent = desc;
    }

    // Intercept UUID links in description
    descEl.querySelectorAll('a').forEach(a => {
        const href = a.getAttribute('href') || '';
        const hashMatch = href.match(/^#([0-9a-f-]{36})$/i);
        if (hashMatch) {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                openNetworkViewer(hashMatch[1]);
            });
        }
    });

    // Properties table
    const propsEl = document.getElementById('viewer-properties');
    const visibleKeys = Object.keys(props).filter(k => !HIDDEN_PROPERTIES.has(k));

    const propertyOrder = props['ndex-property-order'];
    let keys;
    if (propertyOrder) {
        const ordered = propertyOrder.split(',').map(s => s.trim());
        const orderedSet = new Set(ordered);
        keys = ordered.filter(k => visibleKeys.includes(k));
        keys.push(...visibleKeys.filter(k => !orderedSet.has(k)).sort());
    } else {
        keys = visibleKeys.sort();
    }

    // Add full name if it was cleaned
    const extraRows = [];
    if (displayName !== summary.name) {
        extraRows.push(['full name', escHtml(summary.name)]);
    }

    if (keys.length > 0 || extraRows.length > 0) {
        let html = '<h3>Properties</h3><table class="prop-table">';
        for (const [k, v] of extraRows) {
            html += `<tr><td>${escHtml(k)}</td><td>${v}</td></tr>`;
        }
        for (const k of keys) {
            html += `<tr><td>${escHtml(k)}</td><td>${formatPropValue(k, props[k])}</td></tr>`;
        }
        html += '</table>';
        propsEl.innerHTML = html;
    } else {
        propsEl.innerHTML = '';
    }

    // Make UUID links navigable
    propsEl.querySelectorAll('a.uuid-link').forEach(a => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            openNetworkViewer(a.getAttribute('href').substring(1));
        });
    });

    renderNetworkSidebar._lastSummary = summary;
}

// ============================================================
// Cytoscape graph rendering
// ============================================================

const NODE_TYPE_COLORS = {
    protein: '#4299e1',
    gene: '#48bb78',
    rna: '#ed8936',
    biological_process: '#9f7aea',
    pathology: '#e53e3e',
    abundance: '#38b2ac',
    complex: '#d69e2e',
    activity: '#667eea',
    drug: '#e53e3e',
    phenotype: '#38b2ac',
    pathway: '#9f7aea',
    task: '#4299e1',
    goal: '#48bb78',
    session: '#ed8936',
    paper: '#667eea',
    agent: '#d69e2e',
    default: '#a0aec0',
};

function shouldUseDagre(parsed, summary) {
    const props = NdexApi.extractProperties(summary || {});
    const dataType = (props['ndex-data-type'] || '').toLowerCase();
    const workflow = (props['ndex-workflow'] || '').toLowerCase();
    const name = (summary?.name || '').toLowerCase();

    const treeKeywords = ['plan', 'episodic-memory', 'outline', 'hierarchy', 'tree'];
    for (const kw of treeKeywords) {
        if (dataType.includes(kw) || workflow.includes(kw) || name.includes(kw)) {
            return true;
        }
    }

    if (parsed.nodes.length < 3 || parsed.nodes.length > 200) return false;

    const inDegree = {};
    for (const node of parsed.nodes) inDegree[String(node.id)] = 0;
    for (const edge of parsed.edges) {
        const target = String(edge.t);
        if (inDegree[target] !== undefined) inDegree[target]++;
    }

    const roots = Object.entries(inDegree).filter(([, deg]) => deg === 0);
    if (roots.length !== 1) return false;

    const adj = {};
    for (const node of parsed.nodes) adj[String(node.id)] = [];
    for (const edge of parsed.edges) {
        adj[String(edge.s)] = adj[String(edge.s)] || [];
        adj[String(edge.s)].push(String(edge.t));
    }

    const WHITE = 0, GRAY = 1, BLACK = 2;
    const color = {};
    for (const node of parsed.nodes) color[String(node.id)] = WHITE;

    function hasCycle(u) {
        color[u] = GRAY;
        for (const v of (adj[u] || [])) {
            if (color[v] === GRAY) return true;
            if (color[v] === WHITE && hasCycle(v)) return true;
        }
        color[u] = BLACK;
        return false;
    }

    for (const node of parsed.nodes) {
        if (color[String(node.id)] === WHITE) {
            if (hasCycle(String(node.id))) return false;
        }
    }

    return true;
}

function renderGraph(cx2Data, summary) {
    const parsed = NdexApi.parseCX(cx2Data);
    const cyContainer = document.getElementById('cy');

    if (parsed.nodes.length === 0) {
        cyContainer.innerHTML = '<p class="loading">No graph data in this network.</p>';
        document.getElementById('graph-legend').style.display = 'none';
        if (cy) { cy.destroy(); cy = null; }
        return;
    }
    cyContainer.innerHTML = '';

    const elements = [];
    const typesUsed = new Set();

    let hasPositions = false;
    let hasHighlights = false;

    for (const node of parsed.nodes) {
        const attrs = node.v || {};
        const nodeType = attrs.type || attrs.node_type || 'default';
        typesUsed.add(nodeType);

        const isHighlighted = String(attrs.highlight || '').toLowerCase() === 'true';
        if (isHighlighted) hasHighlights = true;

        const elem = {
            group: 'nodes',
            data: {
                id: String(node.id),
                label: attrs.name || `node_${node.id}`,
                nodeType,
                color: NODE_TYPE_COLORS[nodeType] || NODE_TYPE_COLORS.default,
                highlighted: isHighlighted,
                ...attrs,
            },
        };
        if (typeof node.x === 'number' && typeof node.y === 'number') {
            elem.position = { x: node.x, y: node.y };
            hasPositions = true;
        }
        elements.push(elem);
    }

    for (const edge of parsed.edges) {
        const attrs = edge.v || {};
        const isHighlighted = String(attrs.highlight || '').toLowerCase() === 'true';
        if (isHighlighted) hasHighlights = true;

        elements.push({
            group: 'edges',
            data: {
                id: `e_${edge.id ?? `${edge.s}_${edge.t}`}`,
                source: String(edge.s),
                target: String(edge.t),
                label: attrs.interaction || '',
                highlighted: isHighlighted,
                ...attrs,
            },
        });
    }

    if (cy) cy.destroy();

    let layoutConfig;
    if (hasPositions) {
        layoutConfig = { name: 'preset', animate: false };
    } else if (shouldUseDagre(parsed, summary)) {
        layoutConfig = { name: 'dagre', rankDir: 'TB', nodeSep: 50, rankSep: 70, animate: false };
    } else {
        layoutConfig = { name: 'cose', animate: false, nodeRepulsion: 8000, idealEdgeLength: 80, gravity: 0.3 };
    }

    cy = cytoscape({
        container: cyContainer,
        elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': 'data(color)',
                    'color': '#1a202c',
                    'font-size': '14px',
                    'text-valign': 'bottom',
                    'text-margin-y': 6,
                    'width': 28,
                    'height': 28,
                    'border-width': 1,
                    'border-color': '#cbd5e0',
                    'text-max-width': '120px',
                    'text-wrap': 'ellipsis',
                    'text-background-color': '#ffffff',
                    'text-background-opacity': 0.85,
                    'text-background-padding': '2px',
                    'text-background-shape': 'roundrectangle',
                },
            },
            {
                selector: 'edge',
                style: {
                    'label': 'data(label)',
                    'font-size': '10px',
                    'color': '#4a5568',
                    'width': 1.5,
                    'line-color': '#cbd5e0',
                    'target-arrow-color': '#a0aec0',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10,
                    'text-background-color': '#ffffff',
                    'text-background-opacity': 0.85,
                    'text-background-padding': '1px',
                    'text-background-shape': 'roundrectangle',
                },
            },
            {
                selector: 'node:selected',
                style: { 'border-width': 3, 'border-color': '#2c5282' },
            },
            {
                selector: 'edge:selected',
                style: { 'line-color': '#2c5282', 'target-arrow-color': '#2c5282', 'width': 3 },
            },
            {
                selector: 'node[?highlighted]',
                style: { 'border-width': 3, 'border-color': '#e53e3e' },
            },
            {
                selector: 'edge[?highlighted]',
                style: { 'line-color': '#e53e3e', 'target-arrow-color': '#e53e3e', 'width': 2.5 },
            },
        ],
        layout: { name: 'preset' },
    });

    const fitGraph = () => {
        requestAnimationFrame(() => {
            cy.fit(30);
            cy.center();
        });
    };

    if (hasPositions) {
        fitGraph();
    } else {
        const layout = cy.layout(layoutConfig);
        layout.one('layoutstop', fitGraph);
        layout.run();
    }

    cy.on('tap', 'node', evt => showElementDetails('Node', evt.target.data()));
    cy.on('tap', 'edge', evt => showElementDetails('Edge', evt.target.data()));

    renderLegend(typesUsed, hasHighlights);
}

function renderLegend(typesUsed, hasHighlights) {
    const legend = document.getElementById('graph-legend');
    const summary = renderNetworkSidebar._lastSummary;

    let html = '';
    if (!(typesUsed.size <= 1 && typesUsed.has('default'))) {
        for (const t of typesUsed) {
            const color = NODE_TYPE_COLORS[t] || NODE_TYPE_COLORS.default;
            html += `<div class="legend-item">
                <span class="legend-dot" style="background:${color}"></span>
                <span>${escHtml(t)}</span>
            </div>`;
        }
    }
    if (hasHighlights) {
        html += `<div class="legend-item">
            <span class="legend-dot" style="background:#fff; border: 2px solid #e53e3e;"></span>
            <span>highlighted</span>
        </div>`;
    }
    if (summary) {
        const counts = [];
        if (summary.nodeCount != null) counts.push(`${summary.nodeCount} nodes`);
        if (summary.edgeCount != null) counts.push(`${summary.edgeCount} edges`);
        if (counts.length) {
            html += `<div class="legend-count">${escHtml(counts.join(' | '))}</div>`;
        }
    }
    if (html) {
        legend.innerHTML = html;
        legend.style.display = 'block';
    } else {
        legend.style.display = 'none';
    }
}

function humanizeKey(key) {
    return key.replace(/([a-z])([A-Z])/g, '$1 $2')
              .replace(/_/g, ' ')
              .replace(/\b\w/g, c => c.toUpperCase());
}

function showElementDetails(type, data) {
    const panel = document.getElementById('viewer-details');
    const content = document.getElementById('detail-content');
    const titleEl = document.getElementById('detail-title');
    const rowHandle = document.getElementById('resize-row');
    panel.style.display = 'block';
    if (rowHandle) rowHandle.style.display = 'block';

    const elementName = data.name || data.label || data.gene_symbol;
    titleEl.textContent = elementName || (type === 'Node' ? 'Node' : 'Edge');

    const skip = new Set(['id', 'source', 'target', 'color', 'label', 'name']);
    let html = '<table>';
    const nodeType = data.nodeType || data.type;
    if (type === 'Node' && nodeType) {
        html += `<tr><td>Node Type</td><td>${escHtml(String(nodeType))}</td></tr>`;
    }
    for (const [k, v] of Object.entries(data)) {
        if (skip.has(k) || k === 'nodeType' || k === 'type' || v === '' || v == null) continue;
        html += `<tr><td>${escHtml(humanizeKey(k))}</td><td>${escHtml(String(v))}</td></tr>`;
    }
    html += '</table>';
    content.innerHTML = html;
}

// ============================================================
// Resizable panes
// ============================================================

function initResizablePanes() {
    const colHandle = document.getElementById('resize-col');
    const rowHandle = document.getElementById('resize-row');
    const sidebarRowHandle = document.getElementById('resize-sidebar-row');
    const sidebar = document.getElementById('viewer-sidebar');
    const graphContainer = document.getElementById('viewer-graph-container');
    const detailsPanel = document.getElementById('viewer-details');
    const rightColumn = document.querySelector('.viewer-right-column');
    const descPanel = document.getElementById('viewer-description');
    const propsPanel = document.getElementById('viewer-properties');

    if (!colHandle || !sidebar) return;

    let colDragging = false;
    colHandle.addEventListener('mousedown', (e) => {
        e.preventDefault();
        colDragging = true;
        colHandle.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    let rowDragging = false;
    if (rowHandle) {
        rowHandle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            rowDragging = true;
            rowHandle.classList.add('dragging');
            document.body.style.cursor = 'row-resize';
            document.body.style.userSelect = 'none';
        });
    }

    let sidebarRowDragging = false;
    if (sidebarRowHandle) {
        sidebarRowHandle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            sidebarRowDragging = true;
            sidebarRowHandle.classList.add('dragging');
            document.body.style.cursor = 'row-resize';
            document.body.style.userSelect = 'none';
        });
    }

    document.addEventListener('mousemove', (e) => {
        if (colDragging) {
            const layoutRect = sidebar.parentElement.getBoundingClientRect();
            const newWidth = e.clientX - layoutRect.left;
            sidebar.style.width = Math.max(200, Math.min(layoutRect.width * 0.6, newWidth)) + 'px';
            if (cy) cy.resize();
        }
        if (rowDragging && rightColumn) {
            const colRect = rightColumn.getBoundingClientRect();
            const offsetY = e.clientY - colRect.top;
            const graphH = Math.max(150, Math.min(colRect.height - 100, offsetY));
            graphContainer.style.flex = 'none';
            graphContainer.style.height = graphH + 'px';
            detailsPanel.style.flex = '1';
            detailsPanel.style.maxHeight = 'none';
            if (cy) cy.resize();
        }
        if (sidebarRowDragging && descPanel && propsPanel) {
            const sidebarRect = sidebar.getBoundingClientRect();
            const headerEl = sidebar.querySelector('.sidebar-header');
            const headerH = headerEl ? headerEl.offsetHeight : 0;
            const handleH = sidebarRowHandle.offsetHeight;
            const availableH = sidebarRect.height - headerH - handleH;
            const offsetY = e.clientY - sidebarRect.top - headerH;
            const descH = Math.max(60, Math.min(availableH - 60, offsetY));
            descPanel.style.flex = 'none';
            descPanel.style.height = descH + 'px';
            propsPanel.style.flex = '1';
            propsPanel.style.maxHeight = 'none';
            propsPanel.style.height = 'auto';
        }
    });

    document.addEventListener('mouseup', () => {
        if (colDragging) {
            colDragging = false;
            colHandle.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            if (cy) cy.resize();
        }
        if (rowDragging) {
            rowDragging = false;
            if (rowHandle) rowHandle.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            if (cy) cy.resize();
        }
        if (sidebarRowDragging) {
            sidebarRowDragging = false;
            sidebarRowHandle.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

initResizablePanes();

// ============================================================
// URL hash handling + init
// ============================================================

(function init() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        const id = hash.substring(1);
        if (/^[0-9a-f-]{36}$/i.test(id)) {
            openNetworkViewer(id);
            return;
        }
    }
    loadAgents();
})();
