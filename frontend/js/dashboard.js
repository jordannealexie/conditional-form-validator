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
        const [users, roles, abacStats, relationships] = await Promise.all([
            apiGetUsers().catch(() => []),
            apiGetRoles().catch(() => []),
            apiGetAbacStats().catch(() => ({ total_policies: 0, applied_policies: 0 })),
            apiGetRelationships().catch(() => [])
        ]);

        // Update stats cards
        document.getElementById('totalUsers').textContent = users.length;
        document.getElementById('totalRoles').textContent = roles.length;
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
    card.className = 'application-card';
    // Removed card.onclick to prevent conflict with button click


    if (bank.primary_color) {
        card.style = `border-left: 5px solid ${bank.primary_color};`;
    } else {
        const bankColors = {
            'BDO': 'border-left: 5px solid #ec1c24;',
            'MAYA': 'border-left: 5px solid #00ff00;',
            'SECB': 'border-left: 5px solid #004a99;'
        };
        card.style = bankColors[bank.code] || '';
    }

    // Simplified Card for Dashboard (Text Only, No Logos)
    const bankBadge = `<span class="bank-tag bank-${bank.code.toLowerCase()}">${bank.name}</span>`;

    card.innerHTML = `
        <div class="app-card-header">
            ${bankBadge}
            <span class="version-badge">v${template.version}</span>
        </div>
        <h3 class="app-title">${template.name}</h3>
        <p class="app-description">${template.description || 'Fill out your application details online.'}</p>
        <div class="app-card-footer">
            <button class="btn-apply" onclick="handleTemplateClick(event, ${template.id}, '${template.bank_id}')">
                Apply Now <i class="fas fa-arrow-right"></i>
            </button>
        </div>
    `;

    return card;
}

async function handleTemplateClick(event, templateId, templateBankId) {
    event.stopPropagation();

    // 1. Check for submissions:create permission
    // We can use the 'hasPermission' function from auth.js if available, or check manual list
    if (typeof hasPermission === 'function' && !hasPermission('submissions:create')) {
        showToast('You are not authorized to submit this form.', 'error');
        return;
    }

    // 2. Check ReBAC (Bank matching) for consistency with backend
    // Get current user details from API or local storage
    try {
        const user = await apiGetCurrentUser();
        // If user is supervisor/user (fieldman) and has a bank_id, it must match
        if (user.user_role !== 'admin' && !user.is_superuser && user.bank_id && user.bank_id != templateBankId) {
            showToast('You can only submit forms for your assigned bank.', 'error');
            return;
        }
    } catch (e) {
        console.error("Error verifying bank access", e);
        // Fallthrough - backend will catch it if we fail here, but better to let them try if we aren't sure
    }

    // 3. Navigate
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

