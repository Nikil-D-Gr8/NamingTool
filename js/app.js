/**
 * NamingTool — Pure static client-side app
 *
 * All vocabulary data is embedded. No server needed.
 * - Live name preview as form fields change
 * - Custom field toggle
 * - Tag editor with multiple export formats
 * - Copy to clipboard
 * - Name history via localStorage
 * - Vocabulary browser with localStorage persistence
 * - Client-side SPA navigation
 */

/* -------------------------------------------------------
   Vocabulary Data (from vocabulary.yaml)
   ------------------------------------------------------- */
const DEFAULT_VOCAB = {
    owner: {
        nik: "Nikil",
        fam: "Family",
        lab: "Lab",
        shr: "Shared"
    },
    provider: {
        hom: "Home Lab",
        oci: "Oracle Cloud",
        aws: "AWS",
        azr: "Azure",
        gcp: "Google Cloud",
        het: "Hetzner",
        do: "DigitalOcean",
        lin: "Linode"
    },
    environment: {
        prd: "Production",
        dev: "Development",
        tst: "Testing",
        stg: "Staging",
        lab: "Lab",
        poc: "Proof of Concept"
    },
    resource_type: {
        vm: "Virtual Machine",
        ct: "Container",
        pod: "Pod",
        k8s: "Kubernetes Cluster",
        node: "Node",
        host: "Host",
        net: "Network",
        subnet: "Subnet",
        vcn: "Virtual Cloud Network",
        vpc: "Virtual Private Cloud",
        lb: "Load Balancer",
        proxy: "Proxy",
        fw: "Firewall",
        vpn: "VPN",
        gw: "Gateway",
        dns: "DNS",
        router: "Router",
        switch: "Switch",
        disk: "Disk",
        vol: "Volume",
        bucket: "Bucket",
        db: "Database",
        cache: "Cache",
        mq: "Message Queue",
        cert: "Certificate",
        secret: "Secret",
        user: "User",
        group: "Group",
        policy: "Policy",
        repo: "Repository",
        app: "Application",
        svc: "Service",
        job: "Job",
        cron: "Cron Job",
        game: "Game"
    },
    purpose: {
        infrastructure: {
            core: "Core", edge: "Edge", storage: "Storage", backup: "Backup",
            monitor: "Monitoring", logging: "Logging", identity: "Identity",
            proxy: "Proxy", dns: "DNS", auth: "Authentication", mail: "Mail"
        },
        applications: {
            blog: "Blog", wiki: "Wiki", paste: "Paste", docs: "Documentation",
            git: "Git", forgejo: "Forgejo", gitea: "Gitea", nextcloud: "Nextcloud",
            immich: "Immich", jellyfin: "Jellyfin", vaultwarden: "Vaultwarden"
        },
        games: {
            minecraft: "Minecraft", terraria: "Terraria", factorio: "Factorio",
            valheim: "Valheim", palworld: "Palworld"
        },
        developer: {
            registry: "Registry", ci: "CI/CD", runner: "Runner",
            builder: "Builder", artifacts: "Artifacts"
        },
        ai: {
            ollama: "Ollama", openwebui: "Open WebUI", comfy: "ComfyUI"
        },
        databases: {
            postgres: "PostgreSQL", mysql: "MySQL", redis: "Redis", mongo: "MongoDB"
        }
    },
    tags: {
        ownership: ["owner", "team", "department", "contact", "email"],
        business: ["purpose", "description", "project", "repository", "documentation"],
        infrastructure: ["provider", "region", "availability-zone", "datacenter", "rack", "host", "cluster"],
        lifecycle: ["environment", "created", "created-by", "managed-by", "last-modified"],
        cost: ["budget", "cost-center", "monthly-cost", "billing-account"],
        security: ["public", "private", "internet-facing", "classification", "backup", "encrypted"],
        os: ["os", "distribution", "version", "architecture", "kernel"],
        network: ["hostname", "domain", "ipv4", "ipv6", "mac", "vlan", "subnet", "gateway", "dns"],
        applications: ["application", "service", "version", "language", "runtime", "port", "database"],
        containers: ["image", "tag", "registry", "compose-project", "namespace"],
        kubernetes: ["namespace", "cluster", "nodepool", "ingress", "storage-class"],
        monitoring: ["prometheus", "grafana", "logging", "alerts", "healthcheck"],
        backup: ["backup-frequency", "backup-location", "retention", "restore-tested"],
        misc: ["criticality", "priority", "maintenance-window", "notes"]
    }
};

const VOCAB_STORAGE_KEY = 'namingtool_vocab';
const HISTORY_KEY = 'namingtool_history';
const MAX_HISTORY = 20;

/* -------------------------------------------------------
   Vocabulary persistence (localStorage)
   ------------------------------------------------------- */
function getVocab() {
    try {
        const stored = localStorage.getItem(VOCAB_STORAGE_KEY);
        if (stored) return JSON.parse(stored);
    } catch (e) { /* ignore */ }
    return JSON.parse(JSON.stringify(DEFAULT_VOCAB));
}

function saveVocab(vocab) {
    localStorage.setItem(VOCAB_STORAGE_KEY, JSON.stringify(vocab));
}

/* -------------------------------------------------------
   SPA Navigation
   ------------------------------------------------------- */
function navigateTo(page) {
    document.querySelectorAll('.page-view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));

    document.getElementById('page-' + page).classList.add('active');
    document.getElementById('nav-' + page).classList.add('active');

    if (page === 'home') initGeneratorPage();
    if (page === 'vocab') initVocabPage();
}

/* -------------------------------------------------------
   Boot
   ------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('nav-home').addEventListener('click', e => { e.preventDefault(); navigateTo('home'); });
    document.getElementById('nav-vocab').addEventListener('click', e => { e.preventDefault(); navigateTo('vocab'); });
    navigateTo('home');
});

/* -------------------------------------------------------
   Generator Page Init
   ------------------------------------------------------- */
function initGeneratorPage() {
    const vocab = getVocab();
    populateDropdowns(vocab);
    initNamePreview();
    initCustomFields();
    initTagEditor(vocab);
    initCopyName();
    initCopyTags();
    initHistory();
}

function populateDropdowns(vocab) {
    populateSelect('id_owner', vocab.owner);
    populateSelect('id_provider', vocab.provider);
    populateSelect('id_environment', vocab.environment);
    populateSelect('id_resource_type', vocab.resource_type);
    populatePurpose('id_purpose', vocab.purpose);
    populateTagSuggestions(vocab.tags);
}

function populateSelect(id, data) {
    const select = document.getElementById(id);
    if (!select) return;
    const label = select.dataset.label || 'option';
    select.innerHTML = `<option value="">Select ${label}…</option>`;
    for (const [code, name] of Object.entries(data)) {
        const opt = document.createElement('option');
        opt.value = code;
        opt.textContent = `${name} (${code})`;
        select.appendChild(opt);
    }
    const custom = document.createElement('option');
    custom.value = '__custom__';
    custom.textContent = '✏️ Custom…';
    select.appendChild(custom);
}

function populatePurpose(id, purposeData) {
    const select = document.getElementById(id);
    if (!select) return;
    select.innerHTML = '<option value="">Select purpose…</option>';
    for (const [_cat, items] of Object.entries(purposeData)) {
        for (const [code, label] of Object.entries(items)) {
            const opt = document.createElement('option');
            opt.value = code;
            opt.textContent = `${label} (${code})`;
            select.appendChild(opt);
        }
    }
    const custom = document.createElement('option');
    custom.value = '__custom__';
    custom.textContent = '✏️ Custom…';
    select.appendChild(custom);
}

function populateTagSuggestions(tags) {
    const datalist = document.getElementById('tagKeySuggestions');
    if (!datalist) return;
    datalist.innerHTML = '';
    for (const keys of Object.values(tags)) {
        for (const key of keys) {
            const opt = document.createElement('option');
            opt.value = key;
            datalist.appendChild(opt);
        }
    }
}

/* -------------------------------------------------------
   Live Name Preview
   ------------------------------------------------------- */
function initNamePreview() {
    const previewEl = document.getElementById('previewName');
    if (!previewEl) return;

    const fields = ['owner', 'provider', 'environment', 'resource_type', 'purpose'];
    const instanceInput = document.getElementById('id_instance');

    function update() {
        const parts = fields.map(f => {
            const select = document.getElementById('id_' + f);
            const custom = document.getElementById('id_' + f + '_custom');
            if (!select) return '‹' + f.replace('_', ' ') + '›';
            if (select.value === '__custom__' && custom && custom.value.trim()) {
                return custom.value.trim().toLowerCase();
            }
            return select.value || '‹' + f.replace('_', ' ') + '›';
        });
        const inst = instanceInput ? String(parseInt(instanceInput.value) || 1).padStart(3, '0') : '001';
        parts.push(inst);
        previewEl.textContent = parts.join('-');
    }

    fields.forEach(f => {
        const select = document.getElementById('id_' + f);
        const custom = document.getElementById('id_' + f + '_custom');
        if (select) select.addEventListener('change', update);
        if (custom) custom.addEventListener('input', update);
    });
    if (instanceInput) instanceInput.addEventListener('input', update);
    update();
}

/* -------------------------------------------------------
   Custom Field Toggle
   ------------------------------------------------------- */
function initCustomFields() {
    const fields = ['owner', 'provider', 'environment', 'resource_type', 'purpose'];
    fields.forEach(f => {
        const select = document.getElementById('id_' + f);
        const custom = document.getElementById('id_' + f + '_custom');
        if (!select || !custom) return;

        function toggle() {
            if (select.value === '__custom__') {
                custom.classList.add('visible');
                custom.focus();
            } else {
                custom.classList.remove('visible');
                custom.value = '';
            }
        }
        select.addEventListener('change', toggle);
        toggle();
    });
}

/* -------------------------------------------------------
   Tag Editor
   ------------------------------------------------------- */
let currentTags = {};

function initTagEditor(vocab) {
    const tagsList = document.getElementById('tagsList');
    const keyInput = document.getElementById('tagKeyInput');
    const valueInput = document.getElementById('tagValueInput');
    const addBtn = document.getElementById('addTagBtn');
    if (!tagsList) return;

    function render() {
        tagsList.innerHTML = '';
        const entries = Object.entries(currentTags);
        if (entries.length === 0) {
            tagsList.innerHTML = '<span class="text-muted" style="font-size:0.8rem;">No tags added yet</span>';
        }
        entries.forEach(([k, v]) => {
            const chip = document.createElement('div');
            chip.className = 'tag-chip';
            chip.innerHTML = `
                <span class="tag-chip-key">${escapeHtml(k)}</span>
                <span class="tag-chip-value">${escapeHtml(v)}</span>
                <button type="button" class="tag-chip-remove" data-key="${escapeHtml(k)}">×</button>
            `;
            tagsList.appendChild(chip);
        });
        updateTagsPreview();
    }

    function addTag() {
        const k = keyInput.value.trim();
        const v = valueInput.value.trim();
        if (!k) return;
        currentTags[k] = v;
        keyInput.value = '';
        valueInput.value = '';
        render();
        keyInput.focus();
    }

    if (addBtn) addBtn.addEventListener('click', addTag);
    if (valueInput) {
        valueInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') { e.preventDefault(); addTag(); }
        });
    }
    if (keyInput) {
        keyInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') { e.preventDefault(); valueInput.focus(); }
        });
    }
    tagsList.addEventListener('click', e => {
        const btn = e.target.closest('.tag-chip-remove');
        if (btn) {
            delete currentTags[btn.getAttribute('data-key')];
            render();
        }
    });
    render();
}

/* -------------------------------------------------------
   Tags Preview & Export Formats
   ------------------------------------------------------- */
function getSelectedFormat() {
    const radio = document.querySelector('input[name="tagFormat"]:checked');
    return radio ? radio.value : 'kv';
}

function formatTags(format) {
    const entries = Object.entries(currentTags);
    if (entries.length === 0) return '';
    switch (format) {
        case 'json': return JSON.stringify(currentTags, null, 2);
        case 'yaml': return entries.map(([k, v]) => `${k}: ${v}`).join('\n');
        case 'csv': return 'key,value\n' + entries.map(([k, v]) => `${k},${v}`).join('\n');
        case 'kv': default: return entries.map(([k, v]) => `${k}: ${v}`).join('\n');
    }
}

function updateTagsPreview() {
    const previewCard = document.getElementById('tagsPreviewCard');
    const previewText = document.getElementById('tagsPreviewText');
    if (!previewCard || !previewText) return;
    const entries = Object.entries(currentTags);
    if (entries.length === 0) { previewCard.style.display = 'none'; return; }
    previewCard.style.display = 'block';
    previewText.textContent = formatTags(getSelectedFormat());
}

document.addEventListener('change', e => {
    if (e.target.name === 'tagFormat') updateTagsPreview();
});

/* -------------------------------------------------------
   Copy Name
   ------------------------------------------------------- */
function initCopyName() {
    const btn = document.getElementById('copyNameBtn');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const name = document.getElementById('previewName').textContent;
        if (!name || name.includes('‹')) return;
        copyToClipboard(name);
        flashButton(btn, 'Copied!');
        addToHistory(name);
    });
}

/* -------------------------------------------------------
   Copy Tags
   ------------------------------------------------------- */
function initCopyTags() {
    const btn = document.getElementById('copyTagsBtn');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const text = formatTags(getSelectedFormat());
        if (!text) return;
        copyToClipboard(text);
        flashButton(btn, 'Copied!');
    });
}

/* -------------------------------------------------------
   Name History (localStorage)
   ------------------------------------------------------- */
function initHistory() {
    const list = document.getElementById('historyList');
    const clearBtn = document.getElementById('clearHistoryBtn');
    if (!list) return;

    function render() {
        const history = loadHistory();
        if (history.length === 0) {
            list.innerHTML = '<div class="empty-state" style="padding:1.5rem;"><p class="text-muted">Names you copy will appear here.</p></div>';
            return;
        }
        list.innerHTML = '';
        history.forEach(entry => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <code class="resource-name">${escapeHtml(entry.name)}</code>
                <span class="text-muted history-time">${timeAgo(entry.timestamp)}</span>
                <button type="button" class="btn btn-ghost btn-xs history-copy-btn" data-name="${escapeHtml(entry.name)}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
            `;
            list.appendChild(item);
        });
    }

    list.addEventListener('click', e => {
        const btn = e.target.closest('.history-copy-btn');
        if (btn) {
            copyToClipboard(btn.dataset.name);
            flashButton(btn, '✓');
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            localStorage.removeItem(HISTORY_KEY);
            render();
        });
    }

    window._renderHistory = render;
    render();
}

function addToHistory(name) {
    let history = loadHistory();
    history = history.filter(h => h.name !== name);
    history.unshift({ name, timestamp: Date.now() });
    if (history.length > MAX_HISTORY) history = history.slice(0, MAX_HISTORY);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    if (window._renderHistory) window._renderHistory();
}

function loadHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
    catch (e) { return []; }
}

function timeAgo(ts) {
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

/* -------------------------------------------------------
   Vocabulary Page
   ------------------------------------------------------- */
function initVocabPage() {
    const vocab = getVocab();
    renderVocabBrowser(vocab);
    initVocabForm(vocab);
}

function renderVocabBrowser(vocab) {
    const container = document.getElementById('vocabBrowser');
    if (!container) return;
    container.innerHTML = '';

    const fieldList = [
        ['owner', 'Owners'],
        ['provider', 'Providers'],
        ['environment', 'Environments'],
        ['resource_type', 'Resource Types'],
        ['purpose', 'Purposes']
    ];

    fieldList.forEach(([fieldName, fieldLabel]) => {
        const data = vocab[fieldName];
        if (!data) return;

        const card = document.createElement('div');
        card.className = 'card';
        card.style.marginTop = '1.5rem';

        let inner = `<h2 class="card-title">${escapeHtml(fieldLabel)}</h2><div class="vocab-grid">`;
        for (const [code, value] of Object.entries(data)) {
            if (typeof value === 'object' && value !== null) {
                // Nested (purpose)
                inner += `<div class="vocab-category"><h3 class="vocab-cat-title">${escapeHtml(code)}</h3>`;
                for (const [sc, sl] of Object.entries(value)) {
                    inner += `<div class="vocab-chip"><span class="vocab-code">${escapeHtml(sc)}</span> ${escapeHtml(sl)}</div>`;
                }
                inner += '</div>';
            } else {
                inner += `<div class="vocab-chip"><span class="vocab-code">${escapeHtml(code)}</span> ${escapeHtml(value)}</div>`;
            }
        }
        inner += '</div>';
        card.innerHTML = inner;
        container.appendChild(card);
    });
}

function initVocabForm(vocab) {
    const fieldSelect = document.getElementById('vocabField');
    const catGroup = document.getElementById('vocabCategoryGroup');
    const form = document.getElementById('vocabAddForm');
    const status = document.getElementById('vocabStatus');
    if (!fieldSelect || !form) return;

    fieldSelect.addEventListener('change', () => {
        catGroup.style.display = fieldSelect.value === 'purpose' ? '' : 'none';
    });

    form.addEventListener('submit', e => {
        e.preventDefault();
        const field = fieldSelect.value;
        const code = form.querySelector('[name="code"]').value.trim().toLowerCase();
        const label = form.querySelector('[name="label"]').value.trim();
        const category = form.querySelector('[name="category"]').value.trim().toLowerCase();

        if (!field || !code || !label) {
            showVocabStatus('Please fill in all required fields.', 'error');
            return;
        }

        const v = getVocab();
        if (field === 'purpose') {
            if (!category) { showVocabStatus('Purpose entries need a category.', 'error'); return; }
            if (!v.purpose[category]) v.purpose[category] = {};
            v.purpose[category][code] = label;
        } else if (field !== 'tags') {
            if (!v[field]) v[field] = {};
            v[field][code] = label;
        }

        saveVocab(v);
        showVocabStatus(`Added "${code}" → "${label}" to ${field}.`, 'success');
        form.reset();
        catGroup.style.display = 'none';
        renderVocabBrowser(v);
    });
}

function showVocabStatus(msg, type) {
    const el = document.getElementById('vocabStatus');
    if (!el) return;
    el.textContent = msg;
    el.className = 'vocab-status ' + type;
    setTimeout(() => { el.className = 'vocab-status'; }, 3000);
}

/* -------------------------------------------------------
   Utils
   ------------------------------------------------------- */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
    } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
    }
}

function flashButton(btn, text) {
    const original = btn.innerHTML;
    btn.innerHTML = `<span style="color: var(--success);">${text}</span>`;
    btn.classList.add('copied');
    setTimeout(() => {
        btn.innerHTML = original;
        btn.classList.remove('copied');
    }, 1500);
}
