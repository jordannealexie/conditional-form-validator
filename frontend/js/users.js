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
 * Initialize user management - load dropdowns then users
 */
async function initUserManagement() {
    try {
        console.log('[users.js] initUserManagement started, DropdownLoader:', typeof DropdownLoader);
        // Load dropdown data first using shared DropdownLoader
        await DropdownLoader.loadAll();
        console.log('[users.js] DropdownLoader.loadAll() completed');
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
    console.log('[users.js] buildRoleOptions called, DropdownLoader:', typeof DropdownLoader);
    const options = DropdownLoader.buildOptions('roles', selectedRole, { emptyLabel: 'Select Role' });
    console.log('[users.js] Role options built:', options.substring(0, 100));
    return options;
}

/**
 * Build department options HTML using DropdownLoader
 * @param {string} [selectedDept] - Currently selected department
 * @returns {string} HTML options string
 */
function buildDepartmentOptions(selectedDept = '') {
    return DropdownLoader.buildOptions('departments', selectedDept, { emptyLabel: 'Select Department' });
}

/**
 * Build location options HTML using DropdownLoader
 * @param {string} [selectedLoc] - Currently selected location
 * @returns {string} HTML options string
 */
function buildLocationOptions(selectedLoc = '') {
    return DropdownLoader.buildOptions('locations', selectedLoc, { emptyLabel: 'Select Location' });
}

/**
 * Build level options HTML using DropdownLoader
 * @param {number|string} [selectedLevel] - Currently selected level
 * @returns {string} HTML options string
 */
function buildLevelOptions(selectedLevel = '') {
    return DropdownLoader.buildOptions('levels', selectedLevel, { emptyLabel: 'Select Level' });
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
 * Show audit trail modal.
 * Can be filtered by resourceType (e.g., 'user', 'role', 'template') and customized per page.
 */
async function showAuditTrail(options) {
    const opts = options || {};
    const resourceType = opts.resourceType || null;
    const subjectLabel = opts.subjectLabel || (resourceType === 'role' ? 'Role' : resourceType === 'template' ? 'Template' : 'User');
    const title = opts.title || (resourceType === 'role'
        ? 'Roles & Permissions Audit Trail'
        : resourceType === 'template'
            ? 'Form Templates Audit Trail'
            : 'User Management Audit Trail');
    const subtitle = opts.subtitle || (resourceType === 'role'
        ? 'Roles & Permissions Audit Trail - All Activities'
        : resourceType === 'template'
            ? 'Form Templates Audit Trail - All Activities'
            : 'User Management Audit Trail - All Activities');

    const content = `
        <div class="audit-trail-container">
            <p class="audit-trail-subtitle">${escapeHtml(subtitle)}</p>
            <div id="auditTrailLoading" style="text-align: center; padding: 20px;">
                <p>Loading audit logs...</p>
            </div>
            <div id="auditTrailContent" style="display: none;">
                <div class="table-wrapper table-responsive" style="max-height: 500px; overflow-y: auto;">
                    <table class="table table-striped table-sm audit-table mb-0" style="width: 100%;">
                        <thead>
                            <tr>
                                <th>${escapeHtml(subjectLabel)}</th>
                                <th>Action</th>
                                <th>Date/Time</th>
                                <th>Performed By</th>
                                <th>Changes</th>
                            </tr>
                        </thead>
                        <tbody id="auditTrailTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
            <div id="auditTrailError" style="display: none; text-align: center; padding: 20px; color: var(--danger);">
                <p>Failed to load audit trail</p>
            </div>
        </div>
    `;
    
    createModal(title, content, [
        { label: 'Close', type: 'secondary', onclick: 'closeModal()' }
    ], 'large');
    
    // Load audit trail data
    await loadAuditTrail({ resourceType });
}

/**
 * Load and display audit trail (optionally filtered by resource type)
 */
async function loadAuditTrail(options) {
    const opts = options || {};
    const resourceType = opts.resourceType || null;
    const loading = document.getElementById('auditTrailLoading');
    const content = document.getElementById('auditTrailContent');
    const error = document.getElementById('auditTrailError');
    const tbody = document.getElementById('auditTrailTableBody');
    
    try {
        const response = await apiGetAllAuditLogs(0, 100);
        
        if (loading) loading.style.display = 'none';
        
        // Handle null or empty response
        const logs = Array.isArray(response) ? response : [];

        // Optionally filter by resource type for page-specific audit views
        const filteredLogs = resourceType
            ? logs.filter(log => {
                  if (!log) return false;
                  const rt = (log.resource_type || '').toLowerCase();
                  const actionName = (log.action || '').toLowerCase();
                  const target = resourceType.toLowerCase();

                  // Primary filter: exact resource_type match
                  if (rt === target) return true;

                  // User-specific logs: allow legacy/null resource_type but user_* actions
                  if (target === 'user') {
                      if (rt === 'users') return true;
                      if (actionName.startsWith('user_')) return true;
                      return false;
                  }

                  // Role-specific logs: match by resource_type or role_* actions
                  if (target === 'role') {
                      if (rt === 'roles') return true;
                      if (actionName.startsWith('role_')) return true;
                      return false;
                  }

                  // Template-specific logs: be tolerant to legacy keys and missing resource_type
                  if (target === 'template') {
                      // Backwards/alias compatibility for templates
                      if (rt === 'templates' || rt === 'forms' || rt === 'form_template') return true;

                      // Fallback: infer from action naming when resource_type is missing
                      if (actionName.startsWith('template_') || actionName.includes('form_template')) {
                          return true;
                      }

                      return false;
                  }

                  // Default: strict resource_type match only
                  return false;
              })
            : logs;

        if (filteredLogs.length === 0) {
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No audit logs found</td></tr>';
            }
            if (content) content.style.display = 'block';
            return;
        }
        
        // Reset in-memory changes store
        window.__auditChangesStore = [];

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

        // Populate audit trail table
        tbody.innerHTML = '';
        filteredLogs.forEach(log => {
            const tr = document.createElement('tr');
            
            // Format subject (user/role/template/etc.)
            let targetSubject = '-';
            if (log.username) {
                targetSubject = escapeHtml(log.username);
            } else if (log.resource_id) {
                let prefix = 'User ID';
                if (log.resource_type === 'role') prefix = 'Role ID';
                else if (log.resource_type === 'template') prefix = 'Template ID';
                targetSubject = `${prefix}: ${log.resource_id}`;
            }
            
            // Format action (support both top-level action and changes.action)
            let rawAction = (log && (log.action || (log.changes && log.changes.action))) || 'Unknown';
            const actionLower = String(rawAction).toLowerCase();
            let actionLabel = rawAction;
            let actionBadge = 'badge-secondary';

            if (actionLower.includes('created')) {
                actionLabel = 'Created';
                actionBadge = 'badge-success';
            } else if (actionLower.includes('updated')) {
                actionLabel = 'Updated';
                actionBadge = 'badge-primary';
            } else if (actionLower.includes('deleted')) {
                actionLabel = 'Deleted';
                actionBadge = 'badge-danger';
            }
            
            // Format date/time
            const dateTime = log.created_at ? formatDateTime(log.created_at) : '-';
            
            // Format performed by (who made the change)
            let performedBy = '-';
            const actorId = log.created_by || log.updated_by || log.deleted_by || log.user_id;
            if (actorId) {
                const actorName = userMap[actorId];
                if (actorName) {
                    performedBy = escapeHtml(actorName) + ` (ID: ${actorId})`;
                } else {
                    performedBy = `User ID: ${actorId}`;
                }
            }
            
            // Format changes (JSON)
            let changesHtml = '-';
            if (log.changes && typeof log.changes === 'object') {
                const idx = window.__auditChangesStore.push(log.changes) - 1;
                changesHtml = `<button class="btn btn-sm btn-info" onclick="showChangesDetailFromIndex(${idx})">View Changes</button>`;
            }
            
            tr.innerHTML = `
                <td>${targetSubject}</td>
                <td><span class="badge ${actionBadge}">${actionLabel}</span></td>
                <td>${dateTime}</td>
                <td>${performedBy}</td>
                <td>${changesHtml}</td>
            `;
            
            tbody.appendChild(tr);
        });
        
        if (content) content.style.display = 'block';
        
    } catch (e) {
        console.error('Error loading audit trail:', e);
        if (loading) loading.style.display = 'none';
        if (error) error.style.display = 'block';
        if (typeof showToast === 'function') {
            showToast('Failed to load audit trail', 'error');
        }
    }
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
    showChangesDetail(window.__auditChangesStore[index]);
}

/**
 * Show detailed changes in a modal
 * @param {object} changes - Changes object
 */
function showChangesDetail(changes) {
    let content = '<div class="changes-detail">';
    
    if (changes.action) {
        content += `<p><strong>Action:</strong> ${escapeHtml(changes.action)}</p>`;
    }
    
    if (changes.before) {
        content += '<div style="margin-top: 15px;"><strong>Before:</strong><pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">' + escapeHtml(JSON.stringify(changes.before, null, 2)) + '</pre></div>';
    }
    
    if (changes.after) {
        content += '<div style="margin-top: 15px;"><strong>After:</strong><pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">' + escapeHtml(JSON.stringify(changes.after, null, 2)) + '</pre></div>';
    }
    
    content += '</div>';
    
    createModal('Change Details', content, [
        { label: 'Close', type: 'secondary', onclick: 'closeModal()' }
    ], 'large');
}


