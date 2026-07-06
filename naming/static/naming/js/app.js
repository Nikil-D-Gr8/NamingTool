/**
 * NamingTool — Client-side interactivity
 *
 * - Live name preview as form fields change
 * - Custom field toggle (show text input when "Custom" is selected)
 * - Tag editor with multiple export formats
 * - Copy to clipboard (name + tags)
 * - Name history via localStorage
 */

const HISTORY_KEY = 'namingtool_history';
const MAX_HISTORY = 20;

document.addEventListener('DOMContentLoaded', () => {
    initNamePreview();
    initCustomFields();
    initTagEditor();
    initCopyName();
    initCopyTags();
    initHistory();
});

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

function initTagEditor() {
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
            const key = btn.getAttribute('data-key');
            delete currentTags[key];
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
        case 'json':
            return JSON.stringify(currentTags, null, 2);
        case 'yaml':
            return entries.map(([k, v]) => `${k}: ${v}`).join('\n');
        case 'csv':
            return 'key,value\n' + entries.map(([k, v]) => `${k},${v}`).join('\n');
        case 'kv':
        default:
            return entries.map(([k, v]) => `${k}: ${v}`).join('\n');
    }
}

function updateTagsPreview() {
    const previewCard = document.getElementById('tagsPreviewCard');
    const previewText = document.getElementById('tagsPreviewText');
    if (!previewCard || !previewText) return;

    const entries = Object.entries(currentTags);
    if (entries.length === 0) {
        previewCard.style.display = 'none';
        return;
    }

    previewCard.style.display = 'block';
    previewText.textContent = formatTags(getSelectedFormat());
}

// Update preview when format changes
document.addEventListener('change', e => {
    if (e.target.name === 'tagFormat') {
        updateTagsPreview();
    }
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
        history.forEach((entry, i) => {
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

    // Expose render so addToHistory can call it
    window._renderHistory = render;
    render();
}

function addToHistory(name) {
    let history = loadHistory();
    // Avoid duplicates at the top
    history = history.filter(h => h.name !== name);
    history.unshift({ name, timestamp: Date.now() });
    if (history.length > MAX_HISTORY) history = history.slice(0, MAX_HISTORY);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    if (window._renderHistory) window._renderHistory();
}

function loadHistory() {
    try {
        return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
    } catch (e) { return []; }
}

function timeAgo(ts) {
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
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
        // Fallback
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
