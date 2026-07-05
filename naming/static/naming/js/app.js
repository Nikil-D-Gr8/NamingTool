/**
 * NamingTool — Client-side interactivity
 *
 * - Live name preview as form fields change
 * - Custom field toggle (show text input when "Custom" is selected)
 * - Tag editor
 * - Auto-instance detection
 * - Form persistence via localStorage
 */

const STORAGE_KEY = 'namingtool_create_draft';

document.addEventListener('DOMContentLoaded', () => {
    initFormPersistence();   // must run before preview so restored values are visible
    initNamePreview();
    initCustomFields();
    initTagEditor();
    initAutoInstance();
});

/* -------------------------------------------------------
   Form Persistence (localStorage)
   Saves all create-form state so navigating away doesn't
   lose your selections. Cleared on successful submit.
   Only active on the create page (not edit).
   ------------------------------------------------------- */
function initFormPersistence() {
    const form = document.getElementById('resourceForm');
    if (!form) return;

    // Only persist on the create page, not edit (edit has a resource object)
    const isCreatePage = window.location.pathname.includes('/new');
    if (!isCreatePage) return;

    const fields = ['owner', 'provider', 'environment', 'resource_type', 'purpose'];
    const instanceInput = document.getElementById('id_instance');
    const notesInput = document.getElementById('id_notes');

    // --- Restore saved draft ---
    const saved = _loadDraft();
    if (saved) {
        // Restore select dropdowns
        fields.forEach(f => {
            const select = document.getElementById('id_' + f);
            const custom = document.getElementById('id_' + f + '_custom');
            if (select && saved[f] !== undefined) {
                select.value = saved[f];
                // If the saved value doesn't match any option, it was custom
                if (select.value !== saved[f]) {
                    select.value = '__custom__';
                }
            }
            if (custom && saved[f + '_custom']) {
                custom.value = saved[f + '_custom'];
            }
        });
        // Restore group
        const groupSelect = document.getElementById('id_group');
        if (groupSelect && saved.group) {
            groupSelect.value = saved.group;
        }
        // Restore instance
        if (instanceInput && saved.instance) {
            instanceInput.value = saved.instance;
        }
        // Restore notes
        if (notesInput && saved.notes) {
            notesInput.value = saved.notes;
        }
        // Restore tags
        if (saved.tags) {
            const tagsJson = document.getElementById('tagsJson');
            if (tagsJson) {
                tagsJson.value = JSON.stringify(saved.tags);
            }
        }
    }

    // --- Save on every change ---
    function saveDraft() {
        const draft = {};
        const groupSelect = document.getElementById('id_group');
        if (groupSelect) draft.group = groupSelect.value;
        
        fields.forEach(f => {
            const select = document.getElementById('id_' + f);
            const custom = document.getElementById('id_' + f + '_custom');
            if (select) draft[f] = select.value;
            if (custom) draft[f + '_custom'] = custom.value;
        });
        if (instanceInput) draft.instance = instanceInput.value;
        if (notesInput) draft.notes = notesInput.value;

        // Tags
        const tagsJson = document.getElementById('tagsJson');
        if (tagsJson) {
            try { draft.tags = JSON.parse(tagsJson.value); } catch(e) { draft.tags = {}; }
        }

        localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
    }

    // Listen on all inputs
    const groupSelect = document.getElementById('id_group');
    if (groupSelect) groupSelect.addEventListener('change', saveDraft);
    fields.forEach(f => {
        const select = document.getElementById('id_' + f);
        const custom = document.getElementById('id_' + f + '_custom');
        if (select) select.addEventListener('change', saveDraft);
        if (custom) custom.addEventListener('input', saveDraft);
    });
    if (instanceInput) instanceInput.addEventListener('input', saveDraft);
    if (notesInput) notesInput.addEventListener('input', saveDraft);

    // Listen for tag changes (dispatched by tag editor)
    document.addEventListener('tags-changed', saveDraft);

    // --- Clear draft on successful submit ---
    form.addEventListener('submit', () => {
        localStorage.removeItem(STORAGE_KEY);
    });
}

function _loadDraft() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch(e) { return null; }
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

    // Listen to all relevant inputs
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
        // Initialize on page load (for edit forms where __custom__ might be pre-selected)
        toggle();
    });
}

/* -------------------------------------------------------
   Tag Editor
   ------------------------------------------------------- */
function initTagEditor() {
    const tagsList = document.getElementById('tagsList');
    const tagsJson = document.getElementById('tagsJson');
    const keyInput = document.getElementById('tagKeyInput');
    const valueInput = document.getElementById('tagValueInput');
    const addBtn = document.getElementById('addTagBtn');
    if (!tagsList || !tagsJson) return;

    // Load existing tags
    let tags = {};
    try {
        tags = JSON.parse(tagsJson.value) || {};
    } catch(e) { tags = {}; }

    function render() {
        tagsList.innerHTML = '';
        Object.entries(tags).forEach(([k, v]) => {
            const chip = document.createElement('div');
            chip.className = 'tag-chip';
            chip.innerHTML = `
                <span class="tag-chip-key">${escapeHtml(k)}</span>
                <span class="tag-chip-value">${escapeHtml(v)}</span>
                <button type="button" class="tag-chip-remove" data-key="${escapeHtml(k)}">×</button>
            `;
            tagsList.appendChild(chip);
        });
        tagsJson.value = JSON.stringify(tags);
        document.dispatchEvent(new CustomEvent('tags-changed'));
    }

    function addTag() {
        const k = keyInput.value.trim();
        const v = valueInput.value.trim();
        if (!k) return;
        tags[k] = v;
        keyInput.value = '';
        valueInput.value = '';
        render();
        keyInput.focus();
    }

    if (addBtn) addBtn.addEventListener('click', addTag);

    // Enter key in value input adds tag
    if (valueInput) {
        valueInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') { e.preventDefault(); addTag(); }
        });
    }

    // Remove tag
    tagsList.addEventListener('click', e => {
        const btn = e.target.closest('.tag-chip-remove');
        if (btn) {
            const key = btn.getAttribute('data-key');
            delete tags[key];
            render();
        }
    });

    render();
}

/* -------------------------------------------------------
   Auto Instance Detection
   ------------------------------------------------------- */
function initAutoInstance() {
    const btn = document.getElementById('autoInstanceBtn');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const params = new URLSearchParams();
        ['owner', 'provider', 'environment', 'resource_type', 'purpose'].forEach(f => {
            const select = document.getElementById('id_' + f);
            const custom = document.getElementById('id_' + f + '_custom');
            let val = select ? select.value : '';
            if (val === '__custom__' && custom) val = custom.value.trim().toLowerCase();
            params.set(f, val);
        });

        fetch('/api/next-instance/?' + params.toString())
            .then(r => r.json())
            .then(data => {
                const inst = document.getElementById('id_instance');
                if (inst && data.next_instance) {
                    inst.value = data.next_instance;
                    inst.dispatchEvent(new Event('input'));
                }
            })
            .catch(() => {});
    });
}

/* -------------------------------------------------------
   Utils
   ------------------------------------------------------- */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
