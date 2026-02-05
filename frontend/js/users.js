// User Management - Form Submission
// Edit, Delete, Add with Role; uses /users API
// Uses shared DropdownLoader for all dropdown values - NO HARDCODING

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    initUserManagement();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Wait for DropdownLoader to be available with timeout
 * @param {number} timeout - Max wait time in ms
 * @returns {Promise<Object|null>}
 */
function waitForDropdownLoader(timeout = 2000) {
    return new Promise((resolve) => {
        const start = Date.now();
        const check = () => {
            const loader = getDropdownLoader();
            if (loader && typeof loader.loadAll === 'function') {
                resolve(loader);
            } else if (Date.now() - start > timeout) {
                resolve(null);
            } else {
                setTimeout(check, 50);
            }
        };
        check();
    });
}

/**
 * Initialize user management - load dropdowns then users
 */
async function initUserManagement() {
    try {
        // Wait for DropdownLoader with timeout
        const dropdownLoader = await waitForDropdownLoader(2000);
        if (!dropdownLoader) {
            console.warn('[users.js] DropdownLoader not available after waiting; continuing without dropdown metadata.');
            await loadUsers();
            return;
        }
        // Load dropdown data first using shared DropdownLoader
        await dropdownLoader.loadAll();
        // Then load users
        await loadUsers();
    } catch (error) {
        console.error('Error initializing user management:', error);
    }
}

/**
 * Build role options HTML using DropdownLoader
 * @param {string} [selectedRole] - Currently selected role
 * @returns {string} HTML options string
 */
function buildRoleOptions(selectedRole = '') {
    const dropdownLoader = getDropdownLoader();
    if (!dropdownLoader) return '<option value="">Select Role</option>';
    const options = dropdownLoader.buildOptions('roles', selectedRole, { emptyLabel: 'Select Role' });
    return options;
}

/**
 * Build department options HTML using DropdownLoader
 * @param {string} [selectedDept] - Currently selected department
 * @returns {string} HTML options string
 */
function buildDepartmentOptions(selectedDept = '') {
    const dropdownLoader = getDropdownLoader();
    if (!dropdownLoader) return '<option value="">Select Department</option>';
    return dropdownLoader.buildOptions('departments', selectedDept, { emptyLabel: 'Select Department' });
}

/**
 * Build location options HTML using DropdownLoader
 * @param {string} [selectedLoc] - Currently selected location
 * @returns {string} HTML options string
 */
function buildLocationOptions(selectedLoc = '') {
    const dropdownLoader = getDropdownLoader();
    if (!dropdownLoader) return '<option value="">Select Location</option>';
    return dropdownLoader.buildOptions('locations', selectedLoc, { emptyLabel: 'Select Location' });
}

/**
 * Build level options HTML using DropdownLoader
 * @param {number|string} [selectedLevel] - Currently selected level
 * @returns {string} HTML options string
 */
function buildLevelOptions(selectedLevel = '') {
    const dropdownLoader = getDropdownLoader();
    if (!dropdownLoader) return '<option value="">Select Level</option>';
    return dropdownLoader.buildOptions('levels', selectedLevel, { emptyLabel: 'Select Level' });
}

function getDropdownLoader() {
    if (typeof DropdownLoader !== 'undefined') {
        return DropdownLoader;
    }
    if (typeof window !== 'undefined' && window.DropdownLoader) {
        return window.DropdownLoader;
    }
    return null;
}

async function loadUserInfo() {
    try {
        const u = await apiGetCurrentUser();
        updateAppUserDisplay(u);
    } catch (e) { console.error('loadUserInfo', e); }
}

function setupMobileMenu() {
    const t = document.getElementById('menuToggle'), s = document.getElementById('sidebar');
    if (t && s) t.addEventListener('click', () => s.classList.toggle('active'));
}

async function loadUsers() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;">Loading…</td></tr>';
    try {
        const users = await apiGetUsers();
        const list = Array.isArray(users) ? users : (users && users.data ? users.data : []);
        tbody.innerHTML = '';
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;">No users found</td></tr>';
            return;
        }
        list.forEach(u => tbody.appendChild(createUserRow(u)));
    } catch (e) {
        console.error('loadUsers', e);
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--danger);">Error loading users</td></tr>';
        if (typeof showToast === 'function') showToast('Failed to load users', 'error');
    }
}

function createUserRow(user) {
    const tr = document.createElement('tr');
    tr.id = `user-row-${user.id}`;
    tr.dataset.userId = user.id;
    const roleCls = (user.user_role || '').toLowerCase() === 'admin' ? 'badge-primary' : (user.user_role ? 'badge-success' : 'badge-secondary');
    const roleHtml = user.user_role ? `<span class="badge ${roleCls}">${escapeHtml(user.user_role)}</span>` : '<span class="badge badge-secondary">—</span>';
    const statusHtml = user.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-secondary">Inactive</span>';
    
    // Format audit fields from database
    const createdAt = user.created_at ? formatDateTime(user.created_at) : '-';
    const updatedAt = user.updated_at ? formatDateTime(user.updated_at) : '-';
    
    tr.innerHTML = `
        <td class="sticky-col"><strong>${escapeHtml(user.username)}</strong></td>
        <td>${user.id}</td>
        <td>${escapeHtml(user.email || '—')}</td>
        <td>${escapeHtml(user.department || '—')}</td>
        <td>${escapeHtml(user.location || '—')}</td>
        <td>${roleHtml}</td>
        <td>${statusHtml}</td>
        <td>${createdAt}</td>
        <td>${updatedAt}</td>
        <td class="table-actions">
            <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})" data-permission="users" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username).replace(/'/g, "\\'")}')" data-permission="users" data-action="delete">Delete</button>
        </td>
    `;
    return tr;
}

// Ensure loadUsers calls enforceUIPermissions after rendering
const originalLoadUsers = loadUsers;
loadUsers = async function () {
    await originalLoadUsers();
    if (typeof enforceUIPermissions === 'function') {
        enforceUIPermissions();
    }
};

function showAddUserModal() {
    const roleOpts = buildRoleOptions();
    const deptOpts = buildDepartmentOptions();
    const locOpts = buildLocationOptions();
    const levelOpts = buildLevelOptions('1'); // Default to Level 1
    const content = `
        <form id="addUserForm" onsubmit="handleAddUser(event)">
            <div class="field-row" style="display:flex; gap:10px;">
                <div class="form-group" style="flex:1;"><label>First Name</label><input type="text" name="first_name"></div>
                <div class="form-group" style="flex:1;"><label>Last Name</label><input type="text" name="last_name"></div>
            </div>
            <div class="form-group"><label>Username *</label><input type="text" name="username" required></div>
            <div class="form-group"><label>Email *</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Password *</label><input type="password" name="password" required minlength="8"></div>
            <div class="form-group"><label>Role</label><select name="user_role">${roleOpts}</select></div>
            <div class="field-row" style="display:flex; gap:10px;">
                <div class="form-group" style="flex:1;"><label>Department</label><select name="department">${deptOpts}</select></div>
                <div class="form-group" style="flex:1;"><label>Location</label><select name="location">${locOpts}</select></div>
            </div>
            <div class="form-group"><label>Level</label><select name="level">${levelOpts}</select></div>
        </form>
    `;
    createModal('Add New User', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Create', type: 'primary', onclick: "document.getElementById('addUserForm').requestSubmit()" }
    ]);
}

async function handleAddUser(ev) {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const username = (fd.get('username') || '').trim();
    const email = (fd.get('email') || '').trim();
    const password = (fd.get('password') || '').trim();

    if (!username || !email || !password) {
        showToast('Username, email, and password are required', 'error');
        return;
    }
    if (typeof isValidEmail === 'function' && !isValidEmail(email)) {
        showToast('Please enter a valid email', 'error');
        return;
    }
    if (password.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    const payload = {
        username,
        email,
        password,
        first_name: fd.get('first_name') || null,
        last_name: fd.get('last_name') || null,
        user_role: fd.get('user_role') || null,
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        level: parseInt(fd.get('level')) || 1,
        bank_id: null
    };
    try {
        const newUser = await apiCreateUser(payload);
        showToast('User created successfully', 'success');
        closeModal();
        
        // Add new user to the table immediately
        if (newUser) {
            const tbody = document.getElementById('usersTableBody');
            if (tbody) {
                // Remove "no users" message if present
                const noDataRow = tbody.querySelector('td[colspan]');
                if (noDataRow) {
                    noDataRow.parentElement.remove();
                }
                // Append new user row
                tbody.appendChild(createUserRow(newUser));
                // Re-apply permissions after adding row
                if (typeof enforceUIPermissions === 'function') {
                    enforceUIPermissions();
                }
            }
        }
    } catch (e) {
        showToast(e.message || 'Error creating user', 'error');
    }
}

async function editUser(userId) {
    try {
        const user = await apiGetUser(userId);
        if (!user) return;
        const roleOpts = buildRoleOptions(user.user_role || '');
        const deptOpts = buildDepartmentOptions(user.department || '');
        const locOpts = buildLocationOptions(user.location || '');
        const levelOpts = buildLevelOptions(user.level || 1);
        const content = `
            <form id="editUserForm" onsubmit="handleEditUser(event, ${userId})">
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>First Name</label><input type="text" name="first_name" value="${escapeHtml(user.first_name || '')}"></div>
                    <div class="form-group" style="flex:1;"><label>Last Name</label><input type="text" name="last_name" value="${escapeHtml(user.last_name || '')}"></div>
                </div>
                <div class="form-group"><label>Username</label><input type="text" name="username" value="${escapeHtml(user.username)}" readonly></div>
                <div class="form-group"><label>Email *</label><input type="email" name="email" value="${escapeHtml(user.email || '')}" required></div>
                <div class="form-group"><label>Role</label><select name="user_role">${roleOpts}</select></div>
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>Department</label><select name="department">${deptOpts}</select></div>
                    <div class="form-group" style="flex:1;"><label>Location</label><select name="location">${locOpts}</select></div>
                </div>
                <div class="field-row" style="display:flex; gap:10px;">
                    <div class="form-group" style="flex:1;"><label>Level</label><select name="level">${levelOpts}</select></div>
                    <div class="form-group" style="flex:1;"><label>Status</label><select name="active">
                        <option value="true" ${user.active !== false ? 'selected' : ''}>Active</option>
                        <option value="false" ${user.active === false ? 'selected' : ''}>Inactive</option>
                    </select></div>
                </div>
            </form>
        `;
        createModal('Edit User', content, [
            { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
            { label: 'Save', type: 'primary', onclick: "document.getElementById('editUserForm').requestSubmit()" }
        ]);
    } catch (e) {
        showToast('Error loading user', 'error');
    }
}

async function handleEditUser(ev, userId) {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const email = (fd.get('email') || '').trim();
    if (!email) {
        showToast('Email is required', 'error');
        return;
    }
    if (typeof isValidEmail === 'function' && !isValidEmail(email)) {
        showToast('Please enter a valid email', 'error');
        return;
    }
    const payload = {
        email,
        first_name: fd.get('first_name') || null,
        last_name: fd.get('last_name') || null,
        user_role: fd.get('user_role') || null,
        department: fd.get('department') || null,
        location: fd.get('location') || null,
        level: parseInt(fd.get('level')) || 1,
        active: fd.get('active') === 'true'
    };
    try {
        const updatedUser = await apiUpdateUser(userId, payload);
        showToast('User updated successfully', 'success');
        closeModal();
        
        // Update the specific row immediately with response data
        if (updatedUser) {
            const existingRow = document.getElementById(`user-row-${userId}`);
            if (existingRow) {
                const newRow = createUserRow(updatedUser);
                existingRow.replaceWith(newRow);
                // Re-apply permissions after row update
                if (typeof enforceUIPermissions === 'function') {
                    enforceUIPermissions();
                }
            }
        }
    } catch (e) {
        showToast(e.message || 'Error updating user', 'error');
    }
}

function deleteUser(userId, username) {
    const content = `<p>Are you sure you want to delete <strong>${escapeHtml(username)}</strong>?</p><p>This action cannot be undone.</p>`;
    createModal('Delete User', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Delete', type: 'danger', onclick: `confirmDeleteUser(${userId})` }
    ]);
}

async function confirmDeleteUser(userId) {
    try {
        await apiDeleteUser(userId);
        showToast('User deleted successfully', 'success');
        closeModal();
        loadUsers();
    } catch (e) {
        showToast(e.message || 'Error deleting user', 'error');
    }
}

/**
 * Show audit trail modal - styled to match ABAC Audit Trail exactly.
 * Can be filtered by resourceType (e.g., 'user', 'role', 'template') and customized per page.
 */
async function showAuditTrail(options) {
    const opts = options || {};
    const resourceType = opts.resourceType || null;
    if (!resourceType) {
        if (typeof showToast === 'function') {
            showToast('Audit trail type is required', 'error');
        }
        return;
    }
    
    // Store current resource type for filters
    window.__currentAuditResourceType = resourceType;
    window.__auditCurrentPage = 1;
    window.__auditPageSize = 20;
    
    const subjectLabel = opts.subjectLabel || (resourceType === 'role' ? 'Role' : resourceType === 'template' ? 'Template' : 'User');
    const title = opts.title || (resourceType === 'role'
        ? 'Roles & Permissions Audit Trail'
        : resourceType === 'template'
            ? 'Form Templates Audit Trail'
            : 'User Management Audit Trail');
    
    // Store subject label for row rendering
    window.__currentAuditSubjectLabel = subjectLabel;

    // Remove existing modal if any
    const existingModal = document.getElementById('auditTrailModalGeneric');
    if (existingModal) {
        existingModal.remove();
    }

    // Create ABAC-style modal structure
    const modalHtml = `
        <div id="auditTrailModalGeneric" class="modal" style="display: flex;">
            <div class="modal-content" style="max-width: 900px; max-height: 80vh;">
                <div class="modal-header">
                    <h2>${escapeHtml(title)}</h2>
                    <button class="modal-close" onclick="closeAuditTrailModalGeneric()">&times;</button>
                </div>
                <div class="modal-body" style="max-height: 60vh; overflow-y: auto;">
                    <!-- Filters -->
                    <div class="audit-filters" style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                        <div class="form-group" style="flex: 1; min-width: 150px;">
                            <label for="auditActionFilterGeneric">Action Type</label>
                            <select id="auditActionFilterGeneric" onchange="loadAuditTrail({resourceType: '${resourceType}'})">
                                <option value="">All Actions</option>
                                <option value="created">Created</option>
                                <option value="updated">Updated</option>
                                <option value="deleted">Deleted</option>
                            </select>
                        </div>
                        <div class="form-group" style="flex: 1; min-width: 150px;">
                            <label for="auditDateFromGeneric">From Date</label>
                            <input type="date" id="auditDateFromGeneric" onchange="loadAuditTrail({resourceType: '${resourceType}'})">
                        </div>
                        <div class="form-group" style="flex: 1; min-width: 150px;">
                            <label for="auditDateToGeneric">To Date</label>
                            <input type="date" id="auditDateToGeneric" onchange="loadAuditTrail({resourceType: '${resourceType}'})">
                        </div>
                        <div class="form-group" style="flex: 0; min-width: 100px; display: flex; align-items: flex-end;">
                            <button class="btn btn-secondary btn-sm" onclick="clearAuditFiltersGeneric('${resourceType}')">Clear</button>
                        </div>
                    </div>
                    
                    <!-- Batch Operations -->
                    <div class="audit-batch-actions" style="display: flex; gap: 8px; margin-bottom: 16px; padding: 12px; background: #f8f9fa; border-radius: 6px;">
                        <span style="line-height: 32px; font-weight: 500; color: #666;">Batch Operations:</span>
                        <button class="btn btn-sm btn-primary" onclick="exportAuditLogsGeneric('${resourceType}')" title="Export audit logs as JSON or CSV">
                            📤 Export
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="showAuditStatisticsGeneric('${resourceType}')" title="View audit statistics">
                            📊 Statistics
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="archiveAuditLogsGeneric('${resourceType}')" title="Archive old audit logs">
                            📦 Archive Old
                        </button>
                    </div>
                    
                    <!-- Audit Log Table -->
                    <div class="table-container">
                        <table class="data-table" id="auditTableGeneric">
                            <thead>
                                <tr>
                                    <th style="width: 15%;">Timestamp</th>
                                    <th style="width: 12%;">Action</th>
                                    <th style="width: 15%;">${escapeHtml(subjectLabel)}</th>
                                    <th style="width: 15%;">Performed By</th>
                                    <th style="width: 43%;">Changes</th>
                                </tr>
                            </thead>
                            <tbody id="auditTrailTableBody">
                                <tr><td colspan="5" style="text-align: center; padding: 24px;">Loading audit logs...</td></tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Pagination -->
                    <div class="pagination" id="auditPaginationGeneric" style="display: flex; justify-content: center; gap: 8px; margin-top: 16px;">
                        <!-- Pagination will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Load audit trail data
    await loadAuditTrail({ resourceType });
}

/**
 * Close the generic audit trail modal
 */
function closeAuditTrailModalGeneric() {
    const modal = document.getElementById('auditTrailModalGeneric');
    if (modal) {
        modal.remove();
    }
}

/**
 * Clear audit filters and reload
 */
function clearAuditFiltersGeneric(resourceType) {
    document.getElementById('auditActionFilterGeneric').value = '';
    document.getElementById('auditDateFromGeneric').value = '';
    document.getElementById('auditDateToGeneric').value = '';
    window.__auditCurrentPage = 1;
    loadAuditTrail({ resourceType });
}

/**
 * Export audit logs as JSON or CSV
 */
function exportAuditLogsGeneric(resourceType) {
    // Remove existing export modal if any
    const existingModal = document.getElementById('exportFormatModal');
    if (existingModal) existingModal.remove();
    
    const modalHtml = `
        <div id="exportFormatModal" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10002;
        ">
            <div style="
                background: white;
                border-radius: 8px;
                padding: 24px;
                min-width: 300px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            ">
                <h3 style="margin: 0 0 16px 0; font-size: 1.1em;">Export Format</h3>
                <p style="color: #666; margin-bottom: 20px;">Choose export format:</p>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="btn btn-secondary" onclick="document.getElementById('exportFormatModal').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="doExportAuditLogs('${resourceType}', 'json')">JSON</button>
                    <button class="btn btn-success" onclick="doExportAuditLogs('${resourceType}', 'csv')">CSV</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

/**
 * Perform the actual export
 */
async function doExportAuditLogs(resourceType, format) {
    document.getElementById('exportFormatModal').remove();
    
    try {
        const response = resourceType === 'user'
            ? await apiGetUsersAuditTrail(0, 1000)
            : await apiGetAllAuditLogs(0, 1000, resourceType);
        
        const logs = Array.isArray(response) ? response : [];
        
        if (format === 'json') {
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `audit_${resourceType}_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } else {
            // CSV export
            const headers = ['Timestamp', 'Action', 'Resource ID', 'Performed By', 'Changes'];
            const rows = logs.map(log => [
                log.created_at || '',
                log.action || '',
                log.resource_id || '',
                log.created_by || log.user_id || '',
                JSON.stringify(log.changes || {})
            ]);
            const csv = [headers.join(','), ...rows.map(r => r.map(c => '"' + String(c).replace(/"/g, '""') + '"').join(','))].join('\\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `audit_${resourceType}_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        showToast('Audit logs exported successfully', 'success');
    } catch (e) {
        console.error('Export error:', e);
        showToast('Failed to export audit logs', 'error');
    }
}

/**
 * Show audit statistics modal
 */
async function showAuditStatisticsGeneric(resourceType) {
    try {
        const response = resourceType === 'user'
            ? await apiGetUsersAuditTrail(0, 1000)
            : await apiGetAllAuditLogs(0, 1000, resourceType);
        
        const logs = Array.isArray(response) ? response : [];
        
        // Calculate statistics
        const now = new Date();
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        const totalLogs = logs.length;
        const last24h = logs.filter(l => new Date(l.created_at) >= oneDayAgo).length;
        const last7d = logs.filter(l => new Date(l.created_at) >= oneWeekAgo).length;
        const last30d = logs.filter(l => new Date(l.created_at) >= oneMonthAgo).length;
        
        // Count by action
        const actionCounts = {};
        logs.forEach(l => {
            const action = l.action || 'unknown';
            actionCounts[action] = (actionCounts[action] || 0) + 1;
        });
        
        const resourceTitle = resourceType === 'user' ? 'User Management' : resourceType === 'role' ? 'Roles & Permissions' : 'Form Templates';
        
        // Remove existing modal
        const existingModal = document.getElementById('auditStatsModal');
        if (existingModal) existingModal.remove();
        
        const modalHtml = `
            <div id="auditStatsModal" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.6);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10002;
            ">
                <div style="
                    background: white;
                    border-radius: 8px;
                    padding: 24px;
                    min-width: 400px;
                    max-width: 500px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; font-size: 1.1em;">${resourceTitle} Audit Statistics</h3>
                        <button onclick="document.getElementById('auditStatsModal').remove()" style="background: none; border: none; font-size: 1.5em; cursor: pointer; color: #666;">&times;</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                        <div style="background: #e8f5e9; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #c8e6c9;">
                            <div style="font-size: 1.8em; font-weight: bold; color: #2e7d32;">${totalLogs}</div>
                            <div style="color: #666; font-size: 0.9em;">Total Logs</div>
                        </div>
                        <div style="background: #e8f5e9; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #c8e6c9;">
                            <div style="font-size: 1.8em; font-weight: bold; color: #d32f2f;">${last24h}</div>
                            <div style="color: #666; font-size: 0.9em;">Last 24 Hours</div>
                        </div>
                        <div style="background: #fff3e0; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #ffe0b2;">
                            <div style="font-size: 1.8em; font-weight: bold; color: #ef6c00;">${last7d}</div>
                            <div style="color: #666; font-size: 0.9em;">Last 7 Days</div>
                        </div>
                        <div style="background: #fce4ec; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #f8bbd9;">
                            <div style="font-size: 1.8em; font-weight: bold; color: #c2185b;">${last30d}</div>
                            <div style="color: #666; font-size: 0.9em;">Last 30 Days</div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <strong style="display: block; margin-bottom: 8px;">Logs by Action</strong>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${Object.entries(actionCounts).map(([action, count]) => 
                                `<span class="badge badge-secondary" style="padding: 6px 12px;">${escapeHtml(action)}: ${count}</span>`
                            ).join('')}
                        </div>
                    </div>
                    
                    <div style="text-align: right;">
                        <button class="btn btn-secondary" onclick="document.getElementById('auditStatsModal').remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
    } catch (e) {
        console.error('Statistics error:', e);
        showToast('Failed to load audit statistics', 'error');
    }
}

/**
 * Archive old audit logs modal
 */
function archiveAuditLogsGeneric(resourceType) {
    // Remove existing modal
    const existingModal = document.getElementById('archiveAuditModal');
    if (existingModal) existingModal.remove();
    
    const modalHtml = `
        <div id="archiveAuditModal" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10002;
        ">
            <div style="
                background: white;
                border-radius: 8px;
                padding: 24px;
                min-width: 350px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            ">
                <h3 style="margin: 0 0 8px 0; font-size: 1.1em;">📦 Archive Old Logs</h3>
                <p style="color: #666; margin-bottom: 16px;">Archive audit logs older than a specified number of days.</p>
                
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="archiveDaysInput">Days old:</label>
                    <input type="number" id="archiveDaysInput" value="90" min="1" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                </div>
                
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="btn btn-secondary" onclick="document.getElementById('archiveAuditModal').remove()">Cancel</button>
                    <button class="btn btn-warning" onclick="doArchiveAuditLogs('${resourceType}')">Archive</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

/**
 * Perform the archive operation (placeholder - would need backend support)
 */
function doArchiveAuditLogs(resourceType) {
    const days = document.getElementById('archiveDaysInput').value;
    document.getElementById('archiveAuditModal').remove();
    
    // This would typically call a backend API to archive old logs
    showToast(`Archive functionality for logs older than ${days} days is not yet implemented on the backend.`, 'info');
}

/**
 * Load and display audit trail (optionally filtered by resource type)
 */
async function loadAuditTrail(options) {
    const opts = options || {};
    const resourceType = opts.resourceType || window.__currentAuditResourceType || null;
    const tbody = document.getElementById('auditTrailTableBody');
    const pagination = document.getElementById('auditPaginationGeneric');
    
    if (!tbody) return;
    
    // Clear the changes store when loading new data
    window.__auditChangesStore = [];
    window.__auditLogStore = [];
    
    // Show loading state
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px;">Loading audit logs...</td></tr>';
    
    // Get filter values
    const actionType = document.getElementById('auditActionFilterGeneric')?.value || '';
    const dateFrom = document.getElementById('auditDateFromGeneric')?.value || '';
    const dateTo = document.getElementById('auditDateToGeneric')?.value || '';
    
    try {
        if (!resourceType) {
            throw new Error('Missing resource type for audit trail');
        }

        // Fetch audit logs
        const response = resourceType === 'user'
            ? await apiGetUsersAuditTrail(0, 100)
            : await apiGetAllAuditLogs(0, 100, resourceType);
        
        // Handle null or empty response
        let logs = Array.isArray(response) ? response : [];
        
        // Apply client-side filters (if API doesn't support them)
        if (actionType) {
            logs = logs.filter(l => {
                const action = (l.action || '').toLowerCase();
                return action.includes(actionType.toLowerCase());
            });
        }
        if (dateFrom) {
            const fromDate = new Date(dateFrom + 'T00:00:00');
            logs = logs.filter(l => new Date(l.created_at) >= fromDate);
        }
        if (dateTo) {
            const toDate = new Date(dateTo + 'T23:59:59');
            logs = logs.filter(l => new Date(l.created_at) <= toDate);
        }

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px; color: #666;">No audit logs found</td></tr>';
            if (pagination) pagination.innerHTML = '';
            return;
        }

        // Build a map of user_id -> username for "Performed By" column
        let userMap = {};
        try {
            const usersResponse = await apiGetUsers();
            const users = Array.isArray(usersResponse) ? usersResponse : (usersResponse && usersResponse.data ? usersResponse.data : []);
            users.forEach(u => {
                if (u && typeof u.id === 'number' && u.username) {
                    userMap[u.id] = u.username;
                }
            });
        } catch (e) {
            console.warn('Failed to load users for audit trail performer mapping:', e);
        }

        // Render audit logs - using ABAC-style row rendering
        tbody.innerHTML = logs.map(log => renderAuditLogRow(log, userMap)).join('');
        
        // Render pagination (simple version showing record count)
        const totalLogs = logs.length;
        if (pagination) {
            pagination.innerHTML = `<span style="color: #666;">${totalLogs} record(s)</span>`;
        }
        
    } catch (e) {
        console.error('Error loading audit trail:', e);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px; color: #dc3545;">Error loading audit logs: ' + escapeHtml(e.message || 'Unknown error') + '</td></tr>';
        if (typeof showToast === 'function') {
            showToast('Failed to load audit trail', 'error');
        }
    }
}

/**
 * Render a single audit log row (ABAC-style)
 */
function renderAuditLogRow(log, userMap = {}) {
    // Use common formatDateTime from utils.js for consistent date format
    const timestamp = log.created_at 
        ? formatDateTime(log.created_at)
        : 'N/A';
    
    // Format action badge
    let actionBadge = '';
    const action = (log.action || '').toLowerCase();
    if (action.includes('created')) {
        actionBadge = '<span class="badge badge-success">Created</span>';
    } else if (action.includes('updated')) {
        actionBadge = '<span class="badge badge-warning">Updated</span>';
    } else if (action.includes('deleted')) {
        actionBadge = '<span class="badge badge-danger">Deleted</span>';
    } else {
        actionBadge = `<span class="badge badge-secondary">${escapeHtml(log.action || 'Unknown')}</span>`;
    }
    
    // Format resource info (subject)
    const resourceType = log.resource_type || 'unknown';
    const resourceId = log.resource_id || 'N/A';
    let resourceName = '';
    
    // Try to get resource name from various fields
    if (log.username) {
        resourceName = log.username;
    } else if (log.details && log.details.name) {
        resourceName = log.details.name;
    } else if (log.changes && log.changes.after && log.changes.after.name) {
        resourceName = log.changes.after.name;
    } else if (log.changes && log.changes.before && log.changes.before.name) {
        resourceName = log.changes.before.name;
    }
    
    const resourceInfo = resourceName 
        ? `<strong>${escapeHtml(resourceName)}</strong><br><small style="color: #666;">${resourceType} #${resourceId}</small>`
        : `${resourceType} #${resourceId}`;
    
    // Format performed by info (ABAC-style)
    let userInfo = 'Unknown';
    if (log.details && log.details.performed_by) {
        const performer = log.details.performed_by;
        const username = performer.username || 'Unknown';
        const role = performer.role || '';
        userInfo = role 
            ? `<strong>${escapeHtml(username)}</strong><br><small style="color: #666;">${escapeHtml(role)}</small>`
            : escapeHtml(username);
    } else {
        // Fallback to legacy method using actor_id fields
        const actorId = log.created_by || log.updated_by || log.deleted_by || log.user_id;
        if (actorId) {
            const actorName = userMap[actorId];
            if (actorName) {
                userInfo = `<strong>${escapeHtml(actorName)}</strong><br><small style="color: #666;">ID: ${actorId}</small>`;
            } else {
                userInfo = `User ID: ${actorId}`;
            }
        }
    }
    
    // Format changes - add View Changes button
    let changesHtml = '-';
    if (log.changes && typeof log.changes === 'object') {
        const idx = window.__auditChangesStore.push(log.changes) - 1;
        window.__auditLogStore.push(log);
        changesHtml = `<button class="btn btn-sm btn-secondary" onclick="showChangesDetailFromIndex(${idx})" style="border: 1px solid #ccc;">View Changes</button>`;
    }
    
    return `
        <tr>
            <td style="font-size: 0.85em;">${timestamp}</td>
            <td>${actionBadge}</td>
            <td>${resourceInfo}</td>
            <td>${userInfo}</td>
            <td style="font-size: 0.85em;">${changesHtml}</td>
        </tr>
    `;
}

/**
 * Helper to look up changes object from in-memory store
 * @param {number} index
 */
function showChangesDetailFromIndex(index) {
    if (!window.__auditChangesStore || !window.__auditChangesStore[index]) {
        console.error('No changes data found for index', index);
        if (typeof showToast === 'function') {
            showToast('No change details available for this entry', 'error');
        }
        return;
    }
    const auditLog = window.__auditLogStore ? window.__auditLogStore[index] : {};
    showChangesDetail(window.__auditChangesStore[index], auditLog);
}

/**
 * Show detailed changes in a modal
 * @param {object} changes - Changes object
 * @param {object} auditLog - Full audit log entry (optional) for accessing details.performed_by
 */
function showChangesDetail(changes, auditLog = {}) {
    const before = changes.before || {};
    const after = changes.after || {};
    const allKeys = Array.from(new Set([
        ...Object.keys(before),
        ...Object.keys(after)
    ])).sort();

    const formatValue = (value) => {
        if (value === null || value === undefined || value === '') {
            return '<span class="text-muted">—</span>';
        }
        if (typeof value === 'object') {
            return `<pre class="json-block">${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
        }
        return escapeHtml(String(value));
    };

    let content = '<div class="changes-detail">';
    
    // Show action badge (using ABAC color scheme)
    if (changes.action) {
        let actionBadgeClass = 'badge-secondary';
        const actionLower = (changes.action || '').toLowerCase();
        if (actionLower.includes('created') || actionLower === 'created') actionBadgeClass = 'badge-success';
        else if (actionLower.includes('updated') || actionLower === 'updated') actionBadgeClass = 'badge-warning';
        else if (actionLower.includes('deleted') || actionLower === 'deleted') actionBadgeClass = 'badge-danger';
        
        content += `<div class="changes-meta" style="margin-bottom: 15px;"><span class="badge ${actionBadgeClass}">${escapeHtml(changes.action)}</span></div>`;
    }
    
    // Show performed_by info from details (ABAC pattern)
    if (auditLog.details && auditLog.details.performed_by) {
        const performer = auditLog.details.performed_by;
        content += `
            <div class="changes-performer" style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                <strong>Performed By:</strong> ${escapeHtml(performer.username || 'Unknown')}
                <span class="badge badge-secondary" style="margin-left: 5px;">${escapeHtml(performer.role || 'unknown')}</span>
                <span class="text-muted" style="margin-left: 10px;">(ID: ${performer.user_id || '-'})</span>
            </div>
        `;
    }

    if (allKeys.length === 0) {
        content += '<p class="text-muted">No field-level changes recorded.</p>';
    } else {
        content += `
            <div class="changes-grid">
                <div class="changes-header">Field</div>
                <div class="changes-header">Before</div>
                <div class="changes-header">After</div>
        `;

        allKeys.forEach((key) => {
            const beforeVal = before[key];
            const afterVal = after[key];
            const changed = JSON.stringify(beforeVal) !== JSON.stringify(afterVal);
            content += `
                <div class="change-key ${changed ? 'change-key--changed' : ''}">${escapeHtml(key)}</div>
                <div class="change-before ${changed ? 'change-cell--changed' : ''}">${formatValue(beforeVal)}</div>
                <div class="change-after ${changed ? 'change-cell--changed' : ''}">${formatValue(afterVal)}</div>
            `;
        });

        content += '</div>';
    }

    content += '</div>';
    
    // Use ABAC-style modal for consistency
    showChangesDetailModal('Change Details', content);
}

/**
 * Create and show the changes detail modal (ABAC-style)
 * @param {string} title - Modal title
 * @param {string} content - Modal body content
 */
function showChangesDetailModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.getElementById('changesDetailModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHtml = `
        <div id="changesDetailModal" class="modal-overlay" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        ">
            <div class="modal-content" style="
                background: white;
                border-radius: 8px;
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 20px;
                    border-bottom: 1px solid #e0e0e0;
                    background: white;
                ">
                    <h3 style="margin: 0; font-size: 1.1em; background: #ffc107; color: #000; padding: 4px 12px; border-radius: 4px;">${escapeHtml(title)}</h3>
                    <button onclick="document.getElementById('changesDetailModal').remove()" style="
                        background: none;
                        border: none;
                        font-size: 1.5em;
                        cursor: pointer;
                        color: #666;
                        padding: 0 8px;
                        line-height: 1;
                    ">&times;</button>
                </div>
                <div style="
                    padding: 20px;
                    overflow-y: auto;
                    flex: 1;
                ">
                    ${content}
                </div>
                <div style="
                    padding: 12px 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: right;
                ">
                    <button class="btn btn-secondary" onclick="document.getElementById('changesDetailModal').remove()">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}


