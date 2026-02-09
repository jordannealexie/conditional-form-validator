// Banks Management - Form Submission
// Edit, Delete, Add banks with full CRUD
// Uses /banks API

document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    initBanksManagement();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Load and display user info in sidebar
 * First shows session data, then updates with fresh API data
 */
async function loadUserInfo() {
    // First, update display with session data immediately
    const sessionUser = getCurrentUser();
    if (sessionUser && typeof updateAppUserDisplay === 'function') {
        updateAppUserDisplay(sessionUser);
    }
    
    // Then try to get fresh data from API
    try {
        const u = await apiGetCurrentUser();
        if (u && typeof updateAppUserDisplay === 'function') {
            updateAppUserDisplay(u);
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
    } catch (e) {
        console.error('loadUserInfo API call failed, using session data:', e);
        // Display stays with session data, which is already set above
    }
}

async function initBanksManagement() {
    await loadBanks();
}

async function loadBanks() {
    const tbody = document.getElementById('banksTableBody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">Loading…</td></tr>';
    try {
        const banks = await apiGetBanks();
        const list = Array.isArray(banks) ? banks : (banks && banks.data ? banks.data : []);
        tbody.innerHTML = '';
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">No banks found</td></tr>';
            return;
        }
        list.forEach(bank => tbody.appendChild(createBankRow(bank)));
    } catch (e) {
        console.error('loadBanks', e);
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:var(--danger);">Error loading banks</td></tr>';
        if (typeof showToast === 'function') showToast('Failed to load banks', 'error');
    }
}

function createBankRow(bank) {
    const tr = document.createElement('tr');
    tr.id = `bank-row-${bank.id}`;
    tr.dataset.bankId = bank.id;
    
    const statusHtml = bank.active !== false ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-secondary">Inactive</span>';
    const logoHtml = bank.logo_url ? `<img src="${escapeHtml(bank.logo_url)}" alt="Logo" style="max-width: 50px; max-height: 30px;">` : '—';
    const colorHtml = bank.primary_color ? `<div style="width: 20px; height: 20px; background-color: ${escapeHtml(bank.primary_color)}; border-radius: 50%; display: inline-block;"></div> ${escapeHtml(bank.primary_color)}` : '—';
    
    // Format audit fields
    const createdAt = bank.created_at ? formatDateTime(bank.created_at) : '-';
    const updatedAt = bank.updated_at ? formatDateTime(bank.updated_at) : '-';
    
    tr.innerHTML = `
        <td class="sticky-col"><strong>${escapeHtml(bank.name)}</strong></td>
        <td>${escapeHtml(bank.code)}</td>
        <td>${escapeHtml(bank.description || '—')}</td>
        <td>${logoHtml}</td>
        <td>${colorHtml}</td>
        <td>${statusHtml}</td>
        <td>${createdAt}</td>
        <td>${updatedAt}</td>
        <td class="table-actions">
            <button class="btn btn-sm btn-primary" onclick="editBank(${bank.id})" data-permission="banks" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteBank(${bank.id}, '${escapeHtml(bank.name).replace(/'/g, "\\'")}')" data-permission="banks" data-action="delete">Delete</button>
        </td>
    `;
    return tr;
}

function showAddBankModal() {
    const titleEl = document.getElementById('bankModalTitle');
    if (titleEl) {
        titleEl.textContent = 'Add Bank';
    }
    const formEl = document.getElementById('bankForm');
    if (formEl) {
        formEl.reset();
    }
    const modalEl = document.getElementById('bankModal');
    if (modalEl) {
        modalEl.classList.add('active');
    }
    const nameEl = document.getElementById('bankName');
    if (nameEl) {
        nameEl.focus();
    }
}

function closeBankModal() {
    document.getElementById('bankModal').classList.remove('active');
    document.getElementById('bankForm').reset();
}

async function editBank(bankId) {
    try {
        const bank = await apiGetBank(bankId);
        document.getElementById('bankModalTitle').textContent = 'Edit Bank';
        document.getElementById('bankName').value = bank.name || '';
        document.getElementById('bankCode').value = bank.code || '';
        document.getElementById('bankDescription').value = bank.description || '';
        document.getElementById('bankLogoUrl').value = bank.logo_url || '';
        document.getElementById('bankPrimaryColor').value = bank.primary_color || '#007bff';
        document.getElementById('bankActive').checked = bank.active !== false;
        
        // Store bank ID for update
        document.getElementById('bankForm').dataset.bankId = bankId;
        
        document.getElementById('bankModal').classList.add('active');
    } catch (e) {
        console.error('editBank', e);
        if (typeof showToast === 'function') showToast('Failed to load bank details', 'error');
    }
}

function deleteBank(bankId, bankName) {
    const content = `<p>Are you sure you want to delete <strong>${escapeHtml(bankName)}</strong>?</p><p>This action cannot be undone.</p>`;
    createModal('Delete Bank', content, [
        { label: 'Cancel', type: 'secondary', onclick: 'closeModal()' },
        { label: 'Delete', type: 'danger', onclick: `confirmDeleteBank(${bankId})` }
    ]);
}

async function confirmDeleteBank(bankId) {
    try {
        await apiDeleteBank(bankId);
        document.getElementById(`bank-row-${bankId}`).remove();
        if (typeof showToast === 'function') showToast('Bank deleted successfully', 'success');
        closeModal();
    } catch (e) {
        console.error('confirmDeleteBank', e);
        const errorMessage = e.message || 'Failed to delete bank';
        if (typeof showToast === 'function') showToast(errorMessage, 'error');
    }
}

// Form submission handler
document.getElementById('bankForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const bankData = {
        name: formData.get('name'),
        code: formData.get('code'),
        description: formData.get('description') || null,
        logo_url: formData.get('logo_url') || null,
        primary_color: formData.get('primary_color') || null,
        active: formData.get('active') === 'on'
    };
    
    const bankId = e.target.dataset.bankId;
    
    try {
        if (bankId) {
            // Update existing bank
            await apiUpdateBank(bankId, bankData);
            if (typeof showToast === 'function') showToast('Bank updated successfully', 'success');
        } else {
            // Create new bank
            await apiCreateBank(bankData);
            if (typeof showToast === 'function') showToast('Bank created successfully', 'success');
        }
        
        closeBankModal();
        await loadBanks(); // Reload the table
    } catch (e) {
        console.error('saveBank', e);
        if (typeof showToast === 'function') showToast('Failed to save bank', 'error');
    }
});

function setupMobileMenu() {
    const t = document.getElementById('menuToggle'), s = document.getElementById('sidebar');
    if (t && s) t.addEventListener('click', () => s.classList.toggle('active'));
}