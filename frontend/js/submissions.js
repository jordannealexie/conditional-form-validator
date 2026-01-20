/**
 * submissions.js: Controller for the submissions management page.
 */

let currentPage = 1;
let currentFilters = {
    bank_id: '',
    status: '',
    search: ''
};

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Check Authentication
    if (!isAuthenticated()) {
        window.location.href = '/index.html';
        return;
    }

    // 2. Load User Info
    try {
        const user = await apiGetCurrentUser();
        document.getElementById('userName').textContent = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
        document.getElementById('userRole').textContent = user.roles && user.roles.length > 0 ? user.roles[0] : 'User';
    } catch (error) {
        console.error('Failed to load user info:', error);
    }

    // 3. Setup Filters
    await setupFilters();

    // 4. Load Submissions
    await loadSubmissions();

    // 5. Event Listeners
    document.getElementById('bankFilter').addEventListener('change', handleFilterChange);
    document.getElementById('statusFilter').addEventListener('change', handleFilterChange);
    document.getElementById('searchInput').addEventListener('input', debounce(handleFilterChange, 500));
    document.getElementById('refreshBtn').addEventListener('click', () => loadSubmissions());
});

async function setupFilters() {
    const bankFilter = document.getElementById('bankFilter');
    try {
        const banks = await apiGetBanks();
        banks.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank.id;
            option.textContent = bank.name;
            bankFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load banks for filter:', error);
    }
}

async function loadSubmissions() {
    const body = document.getElementById('submissionsBody');
    body.innerHTML = '<tr><td colspan="6" class="text-center py-10"><i class="fas fa-spinner fa-spin mr-2"></i> Loading submissions...</td></tr>';

    try {
        // Note: The API might not support all filters directly in the URL search yet,
        // but we'll fetch and filter client-side for now or implement backend filtering.
        const response = await apiGetSubmissions(currentPage, 10);

        // Response wrapper check
        const submissions = response.items || response;

        // Client-side filtering as fallback
        let filtered = submissions;
        if (currentFilters.bank_id) {
            filtered = filtered.filter(s => s.template.bank_id == currentFilters.bank_id);
        }
        if (currentFilters.status) {
            filtered = filtered.filter(s => s.status === currentFilters.status);
        }
        if (currentFilters.search) {
            const q = currentFilters.search.toLowerCase();
            filtered = filtered.filter(s =>
                s.fieldman_id.toLowerCase().includes(q) ||
                s.template.name.toLowerCase().includes(q) ||
                s.id.toString().includes(q)
            );
        }

        renderTable(filtered);
        updatePagination(response);

    } catch (error) {
        console.error('Failed to load submissions:', error);
        body.innerHTML = '<tr><td colspan="6" class="text-center py-10 text-red-500">Error loading submissions</td></tr>';
    }
}

function renderTable(submissions) {
    const body = document.getElementById('submissionsBody');
    body.innerHTML = '';

    if (submissions.length === 0) {
        body.innerHTML = '<tr><td colspan="6" class="text-center py-10 text-gray-500">No submissions found</td></tr>';
        return;
    }

    submissions.forEach(sub => {
        const row = document.createElement('tr');
        row.className = 'border-b hover:bg-gray-50 transition-colors';

        const statusClass = {
            'draft': 'bg-gray-100 text-gray-700',
            'submitted': 'bg-blue-100 text-blue-700',
            'processed': 'bg-green-100 text-green-700'
        }[sub.status] || 'bg-gray-100 text-gray-700';

        row.innerHTML = `
            <td class="px-6 py-4 font-medium">${sub.fieldman_id}</td>
            <td class="px-6 py-4">${sub.template.name}</td>
            <td class="px-6 py-4">${sub.template.bank ? sub.template.bank.name : 'Unknown Bank'}</td>
            <td class="px-6 py-4">
                <span class="px-3 py-1 rounded-full text-xs font-bold ${statusClass}">
                    ${sub.status.toUpperCase()}
                </span>
            </td>
            <td class="px-6 py-4 text-gray-500 text-sm">
                ${new Date(sub.created_at).toLocaleDateString()}
            </td>
            <td class="px-6 py-4">
                <button onclick="viewSubmission(${sub.id})" class="text-indigo-600 hover:text-indigo-800 font-medium">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        `;
        body.appendChild(row);
    });
}

async function viewSubmission(id) {
    const modal = document.getElementById('viewModal');
    const content = document.getElementById('modalContent');

    content.innerHTML = '<div class="text-center py-10"><i class="fas fa-spinner fa-spin text-3xl text-indigo-300"></i></div>';
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    try {
        const sub = await apiGetSubmission(id);

        let html = `
            <div class="space-y-6">
                <div class="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-2xl">
                    <div>
                        <p class="text-xs text-gray-400 uppercase font-bold tracking-wider">Fieldman</p>
                        <p class="font-medium">${sub.fieldman_id}</p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-400 uppercase font-bold tracking-wider">Status</p>
                        <p class="font-medium">${sub.status.toUpperCase()}</p>
                    </div>
                </div>
                
                <div>
                    <h4 class="font-bold text-gray-700 mb-4 border-b pb-2">Form Data</h4>
                    <div class="space-y-3">
        `;

        for (const [key, value] of Object.entries(sub.data_json)) {
            html += `
                <div class="flex justify-between border-b border-gray-100 pb-2">
                    <span class="text-gray-500 text-sm capitalize">${key.replace(/_/g, ' ')}</span>
                    <span class="font-medium text-sm">${value === true ? 'Yes' : (value === false ? 'No' : value)}</span>
                </div>
            `;
        }

        html += `
                    </div>
                </div>
            </div>
        `;

        content.innerHTML = html;

        // Show approve button for supervisors/admins if submitted
        const userRole = (document.getElementById('userRole').textContent || '').toLowerCase();
        if (sub.status === 'submitted' && (userRole === 'supervisor' || userRole === 'admin')) {
            document.getElementById('approveBtn').classList.remove('hidden');
        } else {
            document.getElementById('approveBtn').classList.add('hidden');
        }

    } catch (error) {
        content.innerHTML = `<p class="text-red-500">Error loading details: ${error.message}</p>`;
    }
}

function closeModal() {
    document.getElementById('viewModal').classList.add('hidden');
    document.getElementById('viewModal').classList.remove('flex');
}

function handleFilterChange() {
    currentFilters.bank_id = document.getElementById('bankFilter').value;
    currentFilters.status = document.getElementById('statusFilter').value;
    currentFilters.search = document.getElementById('searchInput').value;
    currentPage = 1;
    loadSubmissions();
}

function updatePagination(response) {
    const info = document.getElementById('paginationInfo');
    const btns = document.getElementById('paginationBtns');

    const total = response.total || 0;
    const itemsPerPage = 10;
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, total);

    info.textContent = total > 0 ? `Showing ${start} to ${end} of ${total} entries` : 'No entries found';

    btns.innerHTML = '';
    const totalPages = Math.ceil(total / itemsPerPage);

    if (totalPages > 1) {
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.className = `px-3 py-1 rounded-lg ${i === currentPage ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'} border transition-colors`;
            btn.textContent = i;
            btn.onclick = () => {
                currentPage = i;
                loadSubmissions();
            };
            btns.appendChild(btn);
        }
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
