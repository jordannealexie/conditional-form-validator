// Role Management - Form Submission
// GET /roles, POST /roles, DELETE /roles/{id}

const AVAILABLE_PERMISSIONS = [
    'users:read', 'users:write', 'templates:read', 'templates:write',
    'submissions:read', 'submissions:write', 'submissions:review',
    'roles:read', 'roles:write', 'banks:read', 'banks:write'
];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadRoles();
    renderPermissionsGrid();
    const form = document.getElementById('addRoleForm');
    if (form) form.addEventListener('submit', handleCreateRole);
});

async function loadUserInfo() {
    try {
        const u = await apiGetCurrentUser();
        if (u) {
            const n = document.getElementById('userName'); if (n) n.textContent = [u.first_name, u.last_name].filter(Boolean).join(' ').trim() || u.username;
            const r = document.getElementById('userRole'); if (r) r.textContent = u.user_role || 'User';
        }
    } catch (e) { console.error(e); }
}

function renderPermissionsGrid() {
    const el = document.getElementById('permissionsGrid');
    if (!el) return;
    el.innerHTML = AVAILABLE_PERMISSIONS.map(p => `
        <label class="perm-check"><input type="checkbox" name="perm" value="${escapeHtml(p)}"> ${escapeHtml(p)}</label>
    `).join('');
}

function toggleAddRoleForm() {
    const form = document.getElementById('addRoleForm');
    if (!form) return;
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    if (form.style.display === 'block') {
        form.reset();
        renderPermissionsGrid();
    }
}

async function loadRoles() {
    const tbody = document.getElementById('rolesTableBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Loading…</td></tr>';
    try {
        const data = await apiGetRoles();
        const list = Array.isArray(data) ? data : (data && data.data ? data.data : []);
        tbody.innerHTML = '';
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No roles found</td></tr>';
            return;
        }
        list.forEach(role => tbody.appendChild(createRoleRow(role)));
    } catch (e) {
        console.error('loadRoles', e);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--danger);">Error loading roles</td></tr>';
        if (typeof showToast === 'function') showToast('Failed to load roles', 'error');
    }
}

function createRoleRow(role) {
    const tr = document.createElement('tr');
    const perms = role.permissions || [];
    const permText = Array.isArray(perms) ? perms.join(', ') : (typeof perms === 'string' ? perms : '—');
    const permShort = permText.length > 60 ? permText.slice(0, 57) + '…' : permText;
    const isSystem = ['admin', 'supervisor', 'fieldman'].includes((role.name || '').toLowerCase());
    tr.innerHTML = `
        <td><strong>${escapeHtml(role.name || '')}</strong></td>
        <td>${escapeHtml(role.description || '—')}</td>
        <td title="${escapeHtml(permText)}">${escapeHtml(permShort) || '—'}</td>
        <td>—</td>
        <td class="table-actions">
            ${isSystem ? '<span class="badge badge-secondary">system</span>' : `<button class="btn btn-sm btn-danger" onclick="deleteRole(${role.id}, '${escapeHtml(role.name || '').replace(/'/g, "\\'")}')">Delete</button>`}
        </td>
    `;
    return tr;
}

async function handleCreateRole(ev) {
    ev.preventDefault();
    const name = (document.getElementById('roleName') || {}).value?.trim();
    if (!name) { showToast('Role name is required', 'error'); return; }
    const description = (document.getElementById('roleDescription') || {}).value?.trim() || null;
    const perms = Array.from(document.querySelectorAll('#permissionsGrid input[name=perm]:checked')).map(c => c.value);
    try {
        await apiCreateRole({ name, description, permissions: perms });
        showToast('Role created successfully', 'success');
        toggleAddRoleForm();
        loadRoles();
    } catch (e) {
        showToast(e.message || 'Error creating role', 'error');
    }
}

function deleteRole(id, name) {
    const content = `<p>Delete role <strong>${escapeHtml(name)}</strong>? If it is assigned to users, the request will fail.</p>`;
    createModal('Delete Role', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Delete', type: 'danger', onclick: `confirmDeleteRole(${id})` }
    ]);
}

async function confirmDeleteRole(id) {
    try {
        await apiDeleteRole(id);
        showToast('Role deleted', 'success');
        closeModal();
        loadRoles();
    } catch (e) {
        showToast(e.message || 'Error deleting role', 'error');
    }
}
