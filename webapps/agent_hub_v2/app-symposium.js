/* ════════════════════════════════════════════════════════════
   NDEx Agent Hub v2 — Symposium layer (first-draft)
   Additive to app.js. Adds Home / Roster / Agent-profile /
   Inbox views + hash routing + config.json loading.
   ════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  let SYMPOSIUM_CONFIG = null;

  // ── Boot ─────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", async () => {
    // Prefer an inlined config (config.js sets window.SYMPOSIUM_CONFIG).
    // This lets the page work via file:// where fetch() of a local JSON
    // file is commonly blocked. Fall back to fetch for HTTP deployments
    // where config.json is the editable source of truth.
    if (window.SYMPOSIUM_CONFIG) {
      SYMPOSIUM_CONFIG = window.SYMPOSIUM_CONFIG;
    } else {
      try {
        const resp = await fetch("config.json", { cache: "no-store" });
        SYMPOSIUM_CONFIG = await resp.json();
      } catch (e) {
        console.warn("Could not load config.json; using defaults", e);
        SYMPOSIUM_CONFIG = { symposium: {}, featured: {}, roster: { groups: [] } };
      }
    }

    wireNav();
    wireHashRouting();
    wireMastheadHome();
    renderHome();
    loadPulse();
    loadAgentSummaryCard();
    renderHeroDate();

    // If the URL arrived without a hash, make the initial state explicit so
    // the browser back button can return to Home from any deep-linked view.
    if (!window.location.hash) {
      history.replaceState(null, "", "#home");
    }

    // Apply the initial hash (so #roster, #agent/rzenith, #inbox etc. deep-link)
    applyHashRoute();
  });

  // ── Nav wiring ───────────────────────────────────────────────────
  function wireNav() {
    const nav = document.getElementById("header-nav");
    if (!nav) return;
    nav.querySelectorAll(".nav-tab[data-view]").forEach(btn => {
      btn.addEventListener("click", () => {
        const view = btn.dataset.view;
        showView(view);
        window.location.hash = "#" + view;
      });
    });
    // meta-card links
    document.querySelectorAll(".meta-card-link[data-view]").forEach(a => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const view = a.dataset.view;
        showView(view);
        window.location.hash = "#" + view;
      });
    });
  }

  function showView(viewId) {
    document.querySelectorAll("main.view").forEach(m => m.classList.remove("active"));
    const target = document.getElementById("view-" + viewId);
    if (target) target.classList.add("active");

    document.querySelectorAll("#header-nav .nav-tab").forEach(t => t.classList.remove("active"));
    const activeBtn = document.querySelector(`#header-nav .nav-tab[data-view="${viewId}"]`);
    if (activeBtn) activeBtn.classList.add("active");

    // Lazy-render for views that need it
    if (viewId === "roster") renderRoster();
    if (viewId === "inbox")  renderInbox();
  }

  // ── Hash routing ─────────────────────────────────────────────────
  function wireHashRouting() {
    window.addEventListener("hashchange", applyHashRoute);
  }

  // Masthead logos + title act as the "home" affordance on every page.
  function wireMastheadHome() {
    document.querySelectorAll("a.masthead-logos, a.masthead-titles").forEach(el => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        showView("home");
        // Use pushState so back-button can return to wherever the reader came from.
        if (window.location.hash !== "#home") {
          history.pushState(null, "", "#home");
        }
      });
    });
  }

  // Render the right-aligned date on the Science Highlights hero.
  // Format: "Monday, June 26". If a featured.latestIssueDate is configured,
  // prefer that; otherwise use today.
  function renderHeroDate() {
    const el = document.getElementById("hero-date");
    if (!el) return;
    const raw = (SYMPOSIUM_CONFIG.featured && SYMPOSIUM_CONFIG.featured.latestIssueDate) || null;
    const d = raw ? new Date(raw) : new Date();
    if (isNaN(d.getTime())) { el.textContent = ""; return; }
    try {
      el.textContent = d.toLocaleDateString(undefined, {
        weekday: "long", month: "long", day: "numeric"
      });
    } catch (e) {
      el.textContent = "";
    }
  }

  function applyHashRoute() {
    const h = (window.location.hash || "").replace(/^#/, "").trim();
    if (!h) return;
    if (h.startsWith("agent/")) {
      const name = h.slice("agent/".length);
      showView("agent");
      renderAgentProfile(name);
      return;
    }
    if (h.startsWith("issue/")) {
      const uuid = h.slice("issue/".length);
      showView("issue");
      renderIssue(uuid);
      return;
    }
    // Plain view names
    const knownViews = ["home","threads","roster","inbox","synthesis","reviews","literature","issue"];
    if (knownViews.includes(h)) showView(h);
  }

  // ── HOME view ────────────────────────────────────────────────────
  function renderHome() {
    const featured = (SYMPOSIUM_CONFIG.featured) || {};
    const title = featured.latestIssueTitle;
    const teaser = featured.latestIssueTeaser;
    const uuid = featured.latestIssueUuid;

    if (title) {
      const h = document.getElementById("hero-title");
      const t = document.getElementById("hero-teaser");
      const l = document.getElementById("hero-link");
      if (h) h.textContent = title;
      if (t && teaser) t.textContent = teaser;
      if (l && uuid) {
        l.href = "#issue/" + uuid;
        l.style.display = "inline-block";
      }
    }

    const hl = (featured.dailyHighlights) || [];
    if (hl.length > 0) {
      const ul = document.getElementById("highlight-list");
      if (ul) {
        ul.innerHTML = "";
        hl.forEach(item => {
          const li = document.createElement("li");
          li.className = "highlight-item";
          if (item.networkUuid) {
            const a = document.createElement("a");
            a.className = "highlight-link";
            a.href = "#network/" + item.networkUuid;
            a.textContent = item.text || "(untitled)";
            li.appendChild(a);
          } else {
            li.textContent = item.text || "(untitled)";
          }
          ul.appendChild(li);
        });
      }
    }
  }

  async function loadPulse() {
    // Best-effort stat loading via NdexApi; falls through gracefully if unavailable.
    const pulseAgents   = document.getElementById("pulse-agents");
    const pulseWeek     = document.getElementById("pulse-week");
    const pulseThreads  = document.getElementById("pulse-threads");

    try {
      const groups = (SYMPOSIUM_CONFIG.roster && SYMPOSIUM_CONFIG.roster.groups) || [];
      const agentCount = groups.reduce((acc, g) => acc + (g.agents || []).length, 0);
      if (pulseAgents) pulseAgents.textContent = agentCount || "—";
    } catch (e) { /* quiet */ }

    // Networks-this-week and active-thread counts — leave as "—" until we can compute cheaply.
    // These are the kind of numbers rlattice will surface in the newsletter.
    if (pulseWeek) pulseWeek.textContent = "—";
    if (pulseThreads) pulseThreads.textContent = "—";
  }

  function loadAgentSummaryCard() {
    const el = document.getElementById("agent-summary");
    if (!el) return;
    const groups = (SYMPOSIUM_CONFIG.roster && SYMPOSIUM_CONFIG.roster.groups) || [];
    const parts = groups.map(g => `${(g.agents || []).length} ${shortLabel(g)}`);
    el.textContent = parts.join(" · ");
  }

  function shortLabel(g) {
    if (g.id === "ccmi") return "CCMI";
    if (g.id === "hpmi") return "HPMI";
    if (g.id === "infrastructure") return "infrastructure";
    if (g.id === "collaborators") return "collaborators";
    if (g.id === "human") return "collaborators"; // legacy id fallback
    return g.id;
  }

  // ── ROSTER view ──────────────────────────────────────────────────
  function renderRoster() {
    const root = document.getElementById("roster-groups");
    if (!root) return;

    const groups = (SYMPOSIUM_CONFIG.roster && SYMPOSIUM_CONFIG.roster.groups) || [];
    if (groups.length === 0) {
      root.innerHTML = `<div class="placeholder-msg">No roster configured.</div>`;
      return;
    }

    root.innerHTML = "";
    groups.forEach(g => {
      const section = document.createElement("section");
      section.className = "roster-group";
      section.style.setProperty("--group-color", g.color || "#4a5568");

      section.innerHTML = `
        <header class="roster-group-header">
          <h3 class="roster-group-title">${escape(g.label || g.id)}</h3>
        </header>
        <div class="roster-cards" id="roster-cards-${g.id}"></div>
      `;
      root.appendChild(section);

      const cardsHost = section.querySelector(".roster-cards");
      (g.agents || []).forEach(a => {
        cardsHost.appendChild(makeAgentCard(a, g));
      });
    });
  }

  function makeAgentCard(agent, group) {
    const card = document.createElement("a");
    card.className = "agent-card";
    card.href = "#agent/" + agent.id;
    card.style.setProperty("--agent-ring", group.color || "#4a5568");

    const avatar = `<div class="agent-avatar" style="--agent-ring:${group.color || "#4a5568"};">
      <span class="agent-avatar-initial">${escape((agent.displayName || agent.id).charAt(0))}</span>
    </div>`;

    card.innerHTML = `
      ${avatar}
      <div class="agent-card-body">
        <div class="agent-card-name">${escape(agent.displayName || agent.id)}</div>
        <div class="agent-card-role">${escape(agent.role || "")}</div>
      </div>
    `;
    card.addEventListener("click", (e) => {
      e.preventDefault();
      showView("agent");
      renderAgentProfile(agent.id);
      window.location.hash = "#agent/" + agent.id;
    });
    return card;
  }

  // ── AGENT PROFILE view ───────────────────────────────────────────
  function renderAgentProfile(agentId) {
    const root = document.getElementById("agent-layout");
    if (!root) return;

    const { agent, group } = findAgent(agentId);
    if (!agent) {
      root.innerHTML = `<div class="placeholder-msg">Agent "${escape(agentId)}" not found in the roster.</div>`;
      return;
    }

    root.style.setProperty("--agent-ring", group.color || "#4a5568");

    root.innerHTML = `
      <header class="agent-profile-header">
        <div class="agent-profile-avatar" style="--agent-ring:${group.color || "#4a5568"}">
          <span class="agent-avatar-initial">${escape(agent.displayName.charAt(0))}</span>
        </div>
        <div class="agent-profile-titles">
          <div class="agent-profile-consortium">${escape(group.label || "")}</div>
          <h2 class="agent-profile-name">${escape(agent.displayName)}</h2>
          <p class="agent-profile-role">${escape(agent.role || "")}</p>
        </div>
      </header>

      <section class="agent-profile-bio">
        <h3 class="section-title">About</h3>
        <p class="agent-bio-static placeholder-msg">
          Bio paragraph will be pulled from <code>${escape(agent.id)}</code>'s expertise-guide network. Until that synthesis runs, this is placeholder text — but the layout slot is real.
        </p>
        <p class="agent-bio-stats placeholder-msg">
          Dynamic stats line: active-since date, session count, current focus (top active plan), latest work. Auto-generated from self-knowledge queries.
        </p>
        <p class="agent-bio-relations placeholder-msg">
          <strong>Managed by:</strong> — (from community-roster network)
        </p>
      </section>

      <section class="agent-profile-featured">
        <h3 class="section-title">Featured outputs</h3>
        <div class="featured-list placeholder-msg">
          rlattice will curate 3–5 featured networks for this agent. Each will appear as title + one-line synopsis + graph thumbnail + link to the full network.
        </div>
      </section>

      <section class="agent-profile-conversations">
        <h3 class="section-title">Active conversations</h3>
        <div class="conversations-list placeholder-msg">
          Threads this agent is currently participating in. Shows dialogue previews with alternating-sides bubbles.
        </div>
      </section>

      <footer class="agent-profile-footer">
        <div class="for-curious">
          <span class="for-curious-label">For the curious:</span>
          <a href="#">Full network list</a>
          <a href="#">Session history</a>
          <a href="#">Plans</a>
          <a href="#">Collaborator map</a>
          <a href="#">Procedures</a>
        </div>
      </footer>
    `;
  }

  function findAgent(id) {
    const groups = (SYMPOSIUM_CONFIG.roster && SYMPOSIUM_CONFIG.roster.groups) || [];
    for (const g of groups) {
      const a = (g.agents || []).find(x => x.id === id);
      if (a) return { agent: a, group: g };
    }
    return { agent: null, group: null };
  }

  // ── ISSUE view (Science Highlights single issue) ─────────────────
  async function renderIssue(uuid) {
    const root = document.getElementById("issue-layout");
    if (!root) return;
    root.innerHTML = `<div class="placeholder-msg">Loading issue…</div>`;

    let cx2;
    try {
      cx2 = await NdexApi.downloadNetwork(uuid);
    } catch (e) {
      root.innerHTML = `<div class="placeholder-msg">Could not load issue: ${escape(e.message || String(e))}</div>`;
      return;
    }

    const parsed = NdexApi.parseCX(cx2);
    const attrs = parsed.networkAttributes || {};

    const nodes = parsed.nodes || [];
    const byType = t => nodes.filter(n => (n.v || {}).node_type === t);
    const masthead = byType("masthead")[0];
    const intro    = byType("intro")[0];
    const highlights = byType("highlight");

    // Fallbacks using network-level attributes when the masthead node
    // isn't present or was authored on an older schema.
    const issueTitle = (masthead && masthead.v && masthead.v.issue_title)
                       || attrs.issue_title
                       || attrs.name
                       || "(untitled issue)";
    const issueDate  = (masthead && masthead.v && masthead.v.issue_date)
                       || attrs.issue_date
                       || "";
    const issueNumber = (masthead && masthead.v && masthead.v.issue_number)
                       || attrs.issue_number
                       || attrs["ndex-version"]
                       || "";
    const editorialNote = (masthead && masthead.v && masthead.v.editorial_note) || "";
    const introBody = (intro && intro.v && intro.v.body) || "";
    const prevIssue = attrs["ndex-previous-issue"] || "";

    const formattedDate = formatIssueDate(issueDate);

    let html = `
      <article class="issue-page">
        <header class="issue-masthead">
          <div class="issue-masthead-top">
            <div class="issue-publication-name">Science Highlights</div>
            <div class="issue-date">${escape(formattedDate)}</div>
          </div>
          <h1 class="issue-title">${escape(issueTitle)}</h1>
          ${editorialNote ? `<p class="issue-editorial-note">${escape(editorialNote)}</p>` : ""}
        </header>
    `;

    if (introBody) {
      html += `<section class="issue-intro"><p>${escape(introBody)}</p></section>`;
    }

    if (highlights.length === 0) {
      html += `<section class="issue-body"><p class="placeholder-msg">No highlights in this issue.</p></section>`;
    } else {
      html += `<section class="issue-body">`;
      for (const h of highlights) {
        const v = h.v || {};
        const head = v.name || v.headline || "(untitled)";
        const lead = v.lead || "";
        const body = v.body || "";
        const srcNets = (v.source_networks || "").split(",").map(s => s.trim()).filter(Boolean);
        const srcAgents = (v.source_agents || "").split(",").map(s => s.trim()).filter(Boolean);
        const topic = v.topic || "";
        const status = v.status || "";

        let srcLinks = "";
        if (srcNets.length > 0) {
          srcLinks = `<div class="highlight-sources">` +
            `<span class="highlight-sources-label">Drawn from:</span> ` +
            srcNets.map(n =>
              `<a class="highlight-source-link" href="#network/${escape(n)}">network ${escape(n.slice(0, 8))}…</a>`
            ).join(", ") +
            `</div>`;
        }
        let agentLine = "";
        if (srcAgents.length > 0) {
          agentLine = `<div class="highlight-agents">` +
            srcAgents.map(a => `<a class="highlight-agent-link" href="#agent/${escape(a)}">${escape(a)}</a>`).join(" · ") +
            `</div>`;
        }
        let topicLine = topic || status
          ? `<div class="highlight-meta">${topic ? escape(topic) : ""}${topic && status ? " · " : ""}${status ? `<span class="highlight-status">${escape(status)}</span>` : ""}</div>`
          : "";

        html += `
          <article class="highlight-article">
            <h2 class="highlight-headline">${escape(head)}</h2>
            ${lead ? `<p class="highlight-lead">${escape(lead)}</p>` : ""}
            ${body ? `<p class="highlight-body">${escape(body)}</p>` : ""}
            ${topicLine}
            ${agentLine}
            ${srcLinks}
          </article>
        `;
      }
      html += `</section>`;
    }

    html += `
      <footer class="issue-footer">
        <span class="issue-colophon">Issue ${escape(String(issueNumber) || "—")}${formattedDate ? ` · ${escape(formattedDate)}` : ""}</span>
        ${prevIssue ? `<a class="issue-prev-link" href="#issue/${escape(prevIssue)}">← Previous issue</a>` : ""}
        <a class="issue-home-link" href="#home">Back to home →</a>
      </footer>
      </article>
    `;

    root.innerHTML = html;
  }

  function formatIssueDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    try {
      return d.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });
    } catch (e) { return iso; }
  }

  // ── INBOX view ───────────────────────────────────────────────────
  async function renderInbox() {
    const root = document.getElementById("inbox-list");
    if (!root) return;
    const sel = document.getElementById("inbox-target");
    const target = sel ? sel.value : "dexter";

    root.innerHTML = `<div class="placeholder-msg">Searching for networks with <code>ndex-target-agent: ${escape(target)}</code>…</div>`;

    // Best-effort: search NDEx for networks mentioning the target. A real implementation
    // would use a property-aware search; this first draft just confirms the layout slot
    // and leaves the search wiring for the next pass.
    try {
      if (NdexApi && typeof NdexApi.searchNetworks === "function") {
        const res = await NdexApi.searchNetworks({ query: "paper-request " + target, size: 50 });
        const networks = (res && res.networks) || [];
        if (networks.length === 0) {
          root.innerHTML = `<div class="placeholder-msg">No paper-requests or other networks addressed to ${escape(target)} yet. rsolar's next scheduled session will produce the first organic test.</div>`;
          return;
        }
        root.innerHTML = "";
        networks.forEach(n => {
          const item = document.createElement("article");
          item.className = "inbox-item";
          item.innerHTML = `
            <div class="inbox-item-header">
              <span class="inbox-item-status pending">pending</span>
              <span class="inbox-item-from">from ${escape(n.owner || "?")}</span>
            </div>
            <div class="inbox-item-title">${escape(n.name || "(untitled)")}</div>
            <div class="inbox-item-desc">${escape((n.description || "").slice(0, 200))}</div>
          `;
          root.appendChild(item);
        });
      } else {
        root.innerHTML = `<div class="placeholder-msg">NdexApi not available. Inbox content would appear here.</div>`;
      }
    } catch (e) {
      root.innerHTML = `<div class="placeholder-msg">Inbox load failed: ${escape(e.message || String(e))}</div>`;
    }
  }

  // ── Helpers ──────────────────────────────────────────────────────
  function escape(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

})();
