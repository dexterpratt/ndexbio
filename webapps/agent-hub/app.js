/**
 * NDEx Agent Hub — main application logic.
 *
 * Three views: Feed, Request, Network Viewer.
 * All data comes from the NDEx public REST API (no auth, no backend).
 */

// ============================================================
// Navigation
// ============================================================

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`view-${btn.dataset.view}`).classList.add('active');
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
// Feed View
// ============================================================

const feedSearch = document.getElementById('feed-search');
const feedSearchBtn = document.getElementById('feed-search-btn');
const feedList = document.getElementById('feed-list');

feedSearchBtn.addEventListener('click', doFeedSearch);
feedSearch.addEventListener('keydown', e => { if (e.key === 'Enter') doFeedSearch(); });

async function doFeedSearch() {
    const query = feedSearch.value.trim();
    if (!query) return;

    feedList.innerHTML = '<p class="loading">Searching...</p>';

    try {
        const data = await NdexApi.searchNetworks(query, 0, 50);
        const networks = data.networks || [];

        if (networks.length === 0) {
            feedList.innerHTML = '<p class="placeholder">No networks found.</p>';
            return;
        }

        feedList.innerHTML = '';
        for (const net of networks) {
            feedList.appendChild(buildFeedCard(net));
        }
    } catch (err) {
        feedList.innerHTML = `<p class="placeholder">Error: ${err.message}</p>`;
    }
}

function buildFeedCard(net) {
    const card = document.createElement('div');
    card.className = 'feed-card';
    card.addEventListener('click', () => openNetworkViewer(net.externalId));

    const props = {};
    if (net.properties) {
        for (const p of net.properties) {
            props[p.predicateString || p.name || ''] = p.value || '';
        }
    }

    const messageType = props['ndex-message-type'] || '';
    const requestStatus = props['ndex-request-status'] || '';
    const workflow = props['ndex-workflow'] || '';
    const doi = props['ndex-doi'] || props['ndex-source'] || '';

    // Badge
    let badgeClass = 'badge-default';
    let badgeLabel = messageType || 'network';
    if (messageType === 'analysis') { badgeClass = 'badge-analysis'; badgeLabel = 'Analysis'; }
    else if (messageType === 'request') {
        badgeClass = requestStatus === 'completed' ? 'badge-completed'
                   : requestStatus === 'error' ? 'badge-error'
                   : 'badge-pending';
        badgeLabel = `Request (${requestStatus || 'pending'})`;
    }
    else if (messageType === 'post') { badgeClass = 'badge-post'; badgeLabel = 'Post'; }

    // Meta line
    const metaParts = [];
    if (net.owner) metaParts.push(`by ${net.owner}`);
    if (net.modificationTime) {
        metaParts.push(new Date(net.modificationTime).toLocaleDateString());
    }
    if (net.nodeCount) metaParts.push(`${net.nodeCount} nodes`);
    if (net.edgeCount) metaParts.push(`${net.edgeCount} edges`);
    if (workflow) metaParts.push(workflow);
    if (doi) metaParts.push(doi);

    const descText = (net.description || '').replace(/<[^>]*>/g, '').substring(0, 250);

    card.innerHTML = `
        <div class="feed-card-header">
            <span class="feed-card-title">${escHtml(net.name || 'Untitled')}</span>
            <span class="feed-card-badge ${badgeClass}">${badgeLabel}</span>
        </div>
        <div class="feed-card-meta">${metaParts.map(m => `<span>${escHtml(m)}</span>`).join('')}</div>
        ${descText ? `<div class="feed-card-desc">${escHtml(descText)}</div>` : ''}
    `;
    return card;
}

// ============================================================
// Network Viewer
// ============================================================

const viewerUuid = document.getElementById('viewer-uuid');
const viewerLoadBtn = document.getElementById('viewer-load-btn');
const viewerContent = document.getElementById('viewer-content');

viewerLoadBtn.addEventListener('click', () => loadNetwork(viewerUuid.value.trim()));
viewerUuid.addEventListener('keydown', e => { if (e.key === 'Enter') loadNetwork(viewerUuid.value.trim()); });

let cy = null; // cytoscape instance

function openNetworkViewer(networkId) {
    // Switch to viewer tab
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelector('[data-view="network"]').classList.add('active');
    document.getElementById('view-network').classList.add('active');

    viewerUuid.value = networkId;
    loadNetwork(networkId);
}

async function loadNetwork(networkId) {
    if (!networkId) return;

    viewerContent.style.display = 'none';
    document.getElementById('viewer-details').style.display = 'none';

    try {
        // Fetch summary and full network in parallel
        const [summary, cx2Data] = await Promise.all([
            NdexApi.getNetworkSummary(networkId),
            NdexApi.downloadNetwork(networkId),
        ]);

        renderNetworkSidebar(summary);
        renderGraph(cx2Data);
        viewerContent.style.display = 'block';
    } catch (err) {
        viewerContent.style.display = 'block';
        document.getElementById('viewer-name').textContent = 'Error loading network';
        document.getElementById('viewer-meta').textContent = err.message;
        document.getElementById('viewer-description').innerHTML = '';
        document.getElementById('viewer-properties').innerHTML = '';
    }
}

function renderNetworkSidebar(summary) {
    document.getElementById('viewer-name').textContent = summary.name || 'Untitled';

    // Meta
    const meta = document.getElementById('viewer-meta');
    const parts = [];
    if (summary.owner) parts.push(`Owner: ${summary.owner}`);
    if (summary.nodeCount != null) parts.push(`${summary.nodeCount} nodes`);
    if (summary.edgeCount != null) parts.push(`${summary.edgeCount} edges`);
    if (summary.modificationTime) parts.push(`Modified: ${new Date(summary.modificationTime).toLocaleDateString()}`);
    meta.textContent = parts.join(' | ');

    // Description — render as markdown
    const desc = summary.description || '';
    const descEl = document.getElementById('viewer-description');
    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
        descEl.innerHTML = DOMPurify.sanitize(marked.parse(desc));
    } else {
        descEl.textContent = desc;
    }

    // Properties table
    const propsEl = document.getElementById('viewer-properties');
    const props = NdexApi.extractProperties(summary);
    const keys = Object.keys(props).sort();
    if (keys.length > 0) {
        let html = '<h3>Properties</h3><table class="prop-table">';
        for (const k of keys) {
            html += `<tr><td>${escHtml(k)}</td><td>${escHtml(String(props[k]))}</td></tr>`;
        }
        html += '</table>';
        propsEl.innerHTML = html;
    } else {
        propsEl.innerHTML = '';
    }
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
    default: '#a0aec0',
};

function renderGraph(cx2Data) {
    const parsed = NdexApi.parseCX(cx2Data);
    const cyContainer = document.getElementById('cy');

    if (parsed.nodes.length === 0) {
        cyContainer.innerHTML = '<p class="loading">No graph data in this network.</p>';
        document.getElementById('graph-legend').style.display = 'none';
        if (cy) { cy.destroy(); cy = null; }
        return;
    }
    cyContainer.innerHTML = '';

    // Map nodes
    const elements = [];
    const typesUsed = new Set();

    for (const node of parsed.nodes) {
        const attrs = node.v || {};
        const nodeType = attrs.type || 'default';
        typesUsed.add(nodeType);

        elements.push({
            group: 'nodes',
            data: {
                id: String(node.id),
                label: attrs.name || `node_${node.id}`,
                nodeType: nodeType,
                color: NODE_TYPE_COLORS[nodeType] || NODE_TYPE_COLORS.default,
                ...attrs,
            },
        });
    }

    for (const edge of parsed.edges) {
        const attrs = edge.v || {};
        elements.push({
            group: 'edges',
            data: {
                id: `e_${edge.id ?? `${edge.s}_${edge.t}`}`,
                source: String(edge.s),
                target: String(edge.t),
                label: attrs.interaction || '',
                ...attrs,
            },
        });
    }

    if (cy) cy.destroy();

    cy = cytoscape({
        container: cyContainer,
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': 'data(color)',
                    'color': '#1a202c',
                    'font-size': '10px',
                    'text-valign': 'bottom',
                    'text-margin-y': 4,
                    'width': 24,
                    'height': 24,
                    'border-width': 1,
                    'border-color': '#cbd5e0',
                    'text-max-width': '80px',
                    'text-wrap': 'ellipsis',
                },
            },
            {
                selector: 'edge',
                style: {
                    'label': 'data(label)',
                    'font-size': '8px',
                    'color': '#718096',
                    'width': 1.5,
                    'line-color': '#cbd5e0',
                    'target-arrow-color': '#a0aec0',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -8,
                },
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#2c5282',
                },
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#2c5282',
                    'target-arrow-color': '#2c5282',
                    'width': 3,
                },
            },
        ],
        layout: {
            name: parsed.nodes.length > 100 ? 'cose' : 'cose',
            animate: false,
            nodeRepulsion: 8000,
            idealEdgeLength: 80,
            gravity: 0.3,
        },
    });

    // Click handler for details panel
    cy.on('tap', 'node', evt => showElementDetails('Node', evt.target.data()));
    cy.on('tap', 'edge', evt => showElementDetails('Edge', evt.target.data()));

    // Legend
    renderLegend(typesUsed);
}

function renderLegend(typesUsed) {
    const legend = document.getElementById('graph-legend');
    if (typesUsed.size <= 1 && typesUsed.has('default')) {
        legend.style.display = 'none';
        return;
    }
    let html = '';
    for (const t of typesUsed) {
        const color = NODE_TYPE_COLORS[t] || NODE_TYPE_COLORS.default;
        html += `<div class="legend-item">
            <span class="legend-dot" style="background:${color}"></span>
            <span>${escHtml(t)}</span>
        </div>`;
    }
    legend.innerHTML = html;
    legend.style.display = 'block';
}

function showElementDetails(type, data) {
    const panel = document.getElementById('viewer-details');
    const content = document.getElementById('detail-content');
    panel.style.display = 'block';

    // Filter out internal cytoscape fields
    const skip = new Set(['id', 'source', 'target', 'color', 'label']);
    let html = `<table>`;
    html += `<tr><td>Type</td><td>${escHtml(type)}</td></tr>`;
    for (const [k, v] of Object.entries(data)) {
        if (skip.has(k) || v === '' || v == null) continue;
        html += `<tr><td>${escHtml(k)}</td><td>${escHtml(String(v))}</td></tr>`;
    }
    html += '</table>';
    content.innerHTML = html;
}

// ============================================================
// Request Form
// ============================================================

document.getElementById('req-generate').addEventListener('click', () => {
    const agent = document.getElementById('req-agent').value.trim();
    const topic = document.getElementById('req-topic').value.trim();
    const category = document.getElementById('req-category').value;
    const days = document.getElementById('req-days').value;
    const instructions = document.getElementById('req-instructions').value.trim();

    if (!topic) {
        alert('Topic is required.');
        return;
    }

    // Build description
    let desc = `Please review recent preprints on: ${topic}`;
    if (category) desc += `\n\nCategory: ${category}`;
    if (days && days !== '7') desc += `\nSearch the last ${days} days.`;
    if (instructions) desc += `\n\n${instructions}`;

    const spec = {
        name: `ndexagent request: ${topic.substring(0, 80)}`,
        description: desc,
        properties: {
            'ndex-agent': agent || 'rdaneel',
            'ndex-message-type': 'request',
            'ndex-workflow': 'literature-review',
            'ndex-request-status': 'pending',
        },
    };

    document.getElementById('req-spec').textContent = JSON.stringify(spec, null, 2);
    document.getElementById('req-output').style.display = 'block';
});

document.getElementById('req-copy').addEventListener('click', () => {
    const text = document.getElementById('req-spec').textContent;
    navigator.clipboard.writeText(text).then(() => {
        document.getElementById('req-copy').textContent = 'Copied!';
        setTimeout(() => { document.getElementById('req-copy').textContent = 'Copy to Clipboard'; }, 2000);
    });
});

// ============================================================
// Utility
// ============================================================

function escHtml(str) {
    const el = document.createElement('span');
    el.textContent = str;
    return el.innerHTML;
}

// Check for network ID in URL hash (allows direct linking)
(function checkHash() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        const id = hash.substring(1);
        // UUID pattern check
        if (/^[0-9a-f-]{36}$/i.test(id)) {
            openNetworkViewer(id);
        }
    }
})();
