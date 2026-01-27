// Dashboard Module
// Handles dashboard statistics and user overview using the real API

/**
 * Initialize the dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadDashboard();
    loadApplications();
    setupMobileMenu();

    // Enforce UI permissions after a short delay to ensure everything is loaded
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Load dashboard statistics from the real API
 */
async function loadDashboard() {
    try {
        const currentUser = await apiGetCurrentUser();
        if (!currentUser) {
            window.location.href = 'index.html';
            return;
        }

        // Update user info in sidebar
        updateAppUserDisplay(currentUser);

        // Update system info section
        if (document.getElementById('currentUserName')) {
            document.getElementById('currentUserName').textContent = currentUser.username;
            document.getElementById('currentUserRoles').textContent = currentUser.user_role || 'None';
            document.getElementById('currentUserDept').textContent = currentUser.department || 'N/A';
            document.getElementById('currentUserLevel').textContent = currentUser.active ? 'Active' : 'Inactive';
        }

        // Fetch counts from various APIs
        // Only call admin APIs if user has permission to avoid unnecessary 403 errors
        const isAdmin = currentUser.is_admin || currentUser.is_superuser || currentUser.user_role === 'admin';
        const canReadUsers = isAdmin || (typeof hasPermission === 'function' && hasPermission('users:read'));
        const canReadRoles = isAdmin || (typeof hasPermission === 'function' && hasPermission('roles:read'));
        
        const [users, roles, abacStats, relationships] = await Promise.all([
            canReadUsers ? apiGetUsers().catch(() => []) : Promise.resolve([]),
            canReadRoles ? apiGetRoles().catch(() => []) : Promise.resolve([]),
            isAdmin ? apiGetAbacStats().catch(() => ({ total_policies: 0, applied_policies: 0 })) : Promise.resolve({ total_policies: 0, applied_policies: 0 }),
            isAdmin ? apiGetRelationships().catch(() => []) : Promise.resolve([])
        ]);

        // Update stats cards (show '-' for unavailable data)
        const totalUsersEl = document.getElementById('totalUsers');
        const totalRolesEl = document.getElementById('totalRoles');
        if (totalUsersEl) totalUsersEl.textContent = canReadUsers ? users.length : '-';
        if (totalRolesEl) totalRolesEl.textContent = canReadRoles ? roles.length : '-';
        // document.getElementById('totalPolicies').textContent = `${abacStats.total_policies} (${abacStats.applied_policies} Applied)`;
        // document.getElementById('totalRelationships').textContent = relationships.length;

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error loading some dashboard statistics', 'warning');
    }
}

async function loadApplications() {
    const grid = document.getElementById('applicationsGrid');
    if (!grid) return;

    try {
        const banks = await apiGetBanks();
        grid.innerHTML = '';

        for (const bank of banks) {
            const templates = await apiGetTemplates(bank.id);
            templates.forEach(template => {
                const card = createApplicationCard(template, bank);
                grid.appendChild(card);
            });
        }

        if (grid.innerHTML === '') {
            grid.innerHTML = '<p class="text-muted">No applications available at the moment.</p>';
        }
    } catch (error) {
        console.error('Failed to load applications:', error);
        grid.innerHTML = '<p class="text-error">Error loading applications. Please try again later.</p>';
    }
}

function createApplicationCard(template, bank) {
    const card = document.createElement('div');
    card.className = 'application-card';

    // Apply consistent border color based on bank
    if (bank.primary_color) {
        card.style.borderLeft = `5px solid ${bank.primary_color}`;
    } else {
        const bankColors = {
            'BDO': '#ec1c24',
            'MAYA': '#00ff00',
            'SECB': '#004a99'
        };
        const color = bankColors[bank.code] || '#6c757d';
        card.style.borderLeft = `5px solid ${color}`;
    }

    // Consistent card structure for all templates
    const bankBadge = `<span class="bank-tag bank-${bank.code.toLowerCase()}">${escapeHtml(bank.name)}</span>`;
    const description = template.description || 'Fill out your application details online.';

    card.innerHTML = `
        <div class="app-card-header">
            ${bankBadge}
            <span class="version-badge">v${template.version}</span>
        </div>
        <h3 class="app-title">${escapeHtml(template.name)}</h3>
        <p class="app-description">${escapeHtml(description)}</p>
        <div class="app-card-footer">
            <button class="btn-apply" onclick="handleTemplateClick(event, ${template.id}, ${template.bank_id})">
                Apply Now <i class="fas fa-arrow-right"></i>
            </button>
        </div>
    `;

    return card;
}

async function handleTemplateClick(event, templateId, templateBankId) {
    event.stopPropagation();

    // Check for submissions:create permission
    // The backend will handle all authorization including bank restrictions if needed
    if (typeof hasPermission === 'function' && !hasPermission('submissions', 'create')) {
        showToast('You are not authorized to submit this form.', 'error');
        return;
    }

    // Navigate to form fill page
    // Backend will perform final authorization checks
    window.location.href = `/form-fill.html?template_id=${templateId}`;
}

/**
 * Setup mobile menu toggle
 */
function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
}

