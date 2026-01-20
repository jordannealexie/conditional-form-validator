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
        const fullName = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim() || currentUser.username;
        document.getElementById('userName').textContent = fullName;
        document.getElementById('userRole').textContent = currentUser.user_role || 'User';

        // Update system info section
        if (document.getElementById('currentUserName')) {
            document.getElementById('currentUserName').textContent = currentUser.username;
            document.getElementById('currentUserRoles').textContent = currentUser.user_role || 'None';
            document.getElementById('currentUserDept').textContent = currentUser.bank_id ? `Bank #${currentUser.bank_id}` : 'N/A';
            document.getElementById('currentUserLevel').textContent = currentUser.active ? 'Active' : 'Inactive';
        }

        // Fetch counts from various APIs
        const [users, roles, policies, relationships] = await Promise.all([
            apiGetUsers().catch(() => []),
            apiGetRoles().catch(() => []),
            apiGetPolicies().catch(() => []),
            apiGetRelationships().catch(() => [])
        ]);

        // Update stats cards
        document.getElementById('totalUsers').textContent = users.length;
        document.getElementById('totalRoles').textContent = roles.length;
        document.getElementById('totalPolicies').textContent = policies.length;
        document.getElementById('totalRelationships').textContent = relationships.length;

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
    card.onclick = () => {
        window.location.href = `/form-fill.html?template_id=${template.id}`;
    };

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

    card.innerHTML = `
        <div class="app-card-header">
            <span class="bank-tag bank-${bank.code.toLowerCase()}">${bank.name}</span>
            <span class="version-badge">v${template.version}</span>
        </div>
        <h3 class="app-title">${template.name}</h3>
        <p class="app-description">${template.description || 'Fill out your application details online.'}</p>
        <div class="app-card-footer">
            <span class="action-link">Apply Now ➔</span>
        </div>
    `;

    return card;
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

