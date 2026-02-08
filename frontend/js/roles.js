// Role Management - Form Submission
// GET /roles, POST /roles, DELETE /roles/{id}

const AVAILABLE_PERMISSIONS = [
    'users:create', 'users:read', 'users:update', 'users:delete',
    'roles:create', 'roles:read', 'roles:update', 'roles:delete',
    'forms:create', 'forms:read', 'forms:update', 'forms:delete',
    'templates:create', 'templates:read', 'templates:update', 'templates:delete',
    'submissions:create', 'submissions:read', 'submissions:viewDetails', 'submissions:update', 'submissions:delete', 'submissions:review',
    'banks:create', 'banks:read', 'banks:update', 'banks:delete',
    'policies:create', 'policies:read', 'policies:update', 'policies:delete',
    'system:configure'
];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadRoles();
    renderPermissionsGrid();
    const form = document.getElementById('addRoleForm');
    if (form) form.addEventListener('submit', handleCreateRole);

    // Enforce UI permissions
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

function showRolesAuditTrail() {
    if (typeof showAuditTrail === 'function') {
        // Reuse shared audit trail modal, filtered to role-related entries
        return showAuditTrail({
            resourceType: 'role',
            title: 'Roles & Permissions Audit Trail',
            subtitle: 'Roles & Permissions Audit Trail - All Activities',
            subjectLabel: 'Role'
        });
    }
}

async function loadUserInfo() {
    try {
        const u = await apiGetCurrentUser();
        if (u) {
            const n = document.getElementById('userName'); if (n) n.textContent = [u.first_name, u.last_name].filter(Boolean).join(' ').trim() || u.username;
            const r = document.getElementById('userRole'); if (r) r.textContent = u.user_role || 'User';
        }

        // Update permissions in session storage
        let permissions = [];
        try {
            const permData = await apiGetUserPermissions();
            permissions = permData.permissions || [];
        } catch (err) {
            console.warn('Could not fetch permissions during loadUserInfo:', err);
        }

        // Update the session data with fresh permissions
        const session = getCurrentUser();
        if (session) {
            session.permissions = permissions;
            session.is_admin = u.is_superuser || u.user_role === 'admin';
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        }

        // Re-enforce UI permissions after updating
        if (typeof enforceUIPermissions === 'function') {
            setTimeout(enforceUIPermissions, 100);
        }
    } catch (e) { console.error(e); }
}

function renderPermissionsGrid(containerId = 'permissionsGrid', selectedPermissions = []) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = AVAILABLE_PERMISSIONS.map(p => `
        <label class="perm-check">
            <input type="checkbox" name="perm" value="${escapeHtml(p)}" ${selectedPermissions.includes(p) ? 'checked' : ''}> 
            ${escapeHtml(p)}
        </label>
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
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Loading…</td></tr>';
    try {
        const data = await apiGetRoles();
        const list = Array.isArray(data) ? data : (data && data.data ? data.data : []);
        tbody.innerHTML = '';
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No roles found</td></tr>';
            return;
        }
        for (const role of list) {
            const userCount = await getRoleUserCount(role.id);
            tbody.appendChild(createRoleRow(role, userCount));
        }
    } catch (e) {
        console.error('loadRoles', e);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--danger);">Error loading roles</td></tr>';
        if (typeof showToast === 'function') showToast('Failed to load roles', 'error');
    }
}

async function getRoleUserCount(roleId) {
    try {
        const result = await apiRequest(`/roles/${roleId}/user-count`);
        return result?.user_count || 0;
    } catch (e) {
        return 0;
    }
}

function createRoleRow(role, userCount = 0) {
    const tr = document.createElement('tr');
    tr.id = `role-row-${role.id}`;
    tr.dataset.roleId = role.id;
    const perms = role.permissions || [];
    const permText = Array.isArray(perms) ? perms.join(', ') : (typeof perms === 'string' ? perms : '—');
    const permShort = permText.length > 60 ? permText.slice(0, 57) + '…' : permText;
    
    // Format audit fields from database (note: updated_by is now user ID, not username)
    const createdAt = role.created_at ? formatDateTime(role.created_at) : '-';
    const updatedAt = role.updated_at ? formatDateTime(role.updated_at) : '-';
    const updatedBy = role.updated_by ? `User #${role.updated_by}` : '-';
    
    tr.innerHTML = `
        <td class="sticky-col"><strong>${escapeHtml(role.name || '')}</strong></td>
        <td>${escapeHtml(role.description || '—')}</td>
        <td title="${escapeHtml(permText)}">${escapeHtml(permShort) || '—'}</td>
        <td>${userCount}</td>
        <td>${createdAt}</td>
        <td>${updatedAt}</td>
        <td>${updatedBy}</td>
        <td class="table-actions">
            <button class="btn btn-sm btn-primary" onclick="editRole(${role.id})" data-permission="roles" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteRole(${role.id}, '${escapeHtml(role.name || '').replace(/'/g, "\\'")}')" data-permission="roles" data-action="delete">Delete</button>
        </td>
    `;
    return tr;
}

// Ensure loadRoles calls enforceUIPermissions after rendering
const originalLoadRoles = loadRoles;
loadRoles = async function () {
    await originalLoadRoles();
    if (typeof enforceUIPermissions === 'function') {
        enforceUIPermissions();
    }
};

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

async function editRole(roleId) {
    try {
        const roles = await apiGetRoles();
        const roleList = Array.isArray(roles) ? roles : (roles && roles.data ? roles.data : []);
        const role = roleList.find(r => r.id === roleId);
        if (!role) return;

        const currentPerms = role.permissions || [];
        const content = `
            <form id="editRoleForm" onsubmit="handleEditRole(event)">
                <input type="hidden" name="roleId" value="${roleId}">
                <div class="form-group"><label>Role Name *</label><input type="text" name="name" value="${escapeHtml(role.name || '')}" required></div>
                <div class="form-group"><label>Description</label><textarea name="description" rows="3">${escapeHtml(role.description || '')}</textarea></div>
                <div class="form-group">
                    <label>Permissions</label>
                    <div class="permissions-grid" id="editPermissionsGrid"></div>
                </div>
            </form>
        `;
        createModal('Edit Role', content, [
            { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
            { label: 'Save', type: 'primary', onclick: "document.getElementById('editRoleForm').requestSubmit()" }
        ]);
        renderPermissionsGrid('editPermissionsGrid', currentPerms);
    } catch (e) {
        showToast('Error loading role', 'error');
    }
}

async function handleEditRole(ev) {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const roleId = parseInt(fd.get('roleId'));
    if (!roleId) {
        showToast('Invalid role id', 'error');
        return;
    }
    const perms = Array.from(document.querySelectorAll('#editPermissionsGrid input[name=perm]:checked')).map(c => c.value);
    const payload = {
        name: (fd.get('name') || '').trim(),
        description: fd.get('description'),
        permissions: perms
    };
    if (!payload.name) {
        showToast('Role name is required', 'error');
        return;
    }
    try {
        await apiUpdateRole(roleId, payload);
        showToast('Role updated successfully', 'success');
        closeModal();
        await loadRoles(); // Reload roles to show changes
    } catch (e) {
        showToast(e.message || 'Error updating role', 'error');
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

