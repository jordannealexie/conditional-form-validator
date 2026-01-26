/**
 * submissions.js: Controller for the submissions management page.
 */

let currentPage = 1;
let currentFilters = {
    bank_id: '',
    template_id: '',
    status: '',
    search: ''
};
let currentSubmissionId = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Check Authentication
    if (typeof requireAuth === 'function') requireAuth();

    // 2. Load User Info
    await loadUserInfo();

    // 3. Setup Filters
    await setupFilters();

    // 4. Load Submissions
    await loadSubmissions();

    // 5. Event Listeners
    document.getElementById('bankFilter').addEventListener('change', handleBankChange);
    document.getElementById('templateFilter').addEventListener('change', handleFilterChange);
    document.getElementById('statusFilter').addEventListener('change', handleFilterChange);
    document.getElementById('searchInput').addEventListener('input', debounce(handleFilterChange, 500));
    document.getElementById('refreshBtn').addEventListener('click', () => loadSubmissions());

    // 6. Setup Mobile Menu
    setupMobileMenu();

    // 7. Enforce UI permissions
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

async function loadUserInfo() {
    try {
        const user = await apiGetCurrentUser();
        if (user) {
            const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
            document.getElementById('userName').textContent = fullName;
            document.getElementById('userRole').textContent = user.user_role || 'User';
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
}

async function setupFilters() {
    const bankFilter = document.getElementById('bankFilter');
    if (!bankFilter) return;
    bankFilter.innerHTML = '<option value="">All Banks</option>';

    try {
        const banks = await apiGetBanks();
        const list = Array.isArray(banks) ? banks : (banks && banks.data ? banks.data : []);
        list.forEach(bank => {
            const option = document.createElement('option');
            option.value = bank.id;
            option.textContent = bank.name;
            bankFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load banks for filter:', error);
    }
}

async function handleBankChange() {
    const bankId = document.getElementById('bankFilter').value;
    currentFilters.bank_id = bankId;
    currentFilters.template_id = ''; // Reset template filter when bank changes

    // Update template filter options
    const templateFilter = document.getElementById('templateFilter');
    if (templateFilter) {
        templateFilter.innerHTML = '<option value="">All Templates</option>';
        // Load templates (filtered by bank or all if no bank selected)
        try {
            const templates = await apiGetTemplates(bankId);
            const list = Array.isArray(templates) ? templates : (templates && templates.data ? templates.data : []);
            list.forEach(t => {
                const option = document.createElement('option');
                option.value = t.id;
                option.textContent = t.name;
                templateFilter.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load templates for filter:', error);
        }
    }

    handleFilterChange();
}

async function loadSubmissions() {
    const body = document.getElementById('submissionsBody');
    body.innerHTML = '<tr><td colspan="7" class="text-center"><div class="loading-spinner">Loading submissions...</div></td></tr>';

    try {
        const response = await apiGetSubmissions(currentPage, 10, currentFilters);

        // Handle response wrapper
        const submissions = response.data || response.items || response;
        const total = response.total || 0;

        // Client-side filtering as fallback (already handled by server if apiGetSubmissions is updated)
        let filtered = submissions;
        if (currentFilters.bank_id && !response.filtered_by_bank) { // only filter if server didn't
            filtered = filtered.filter(s => s.template && s.template.bank_id == currentFilters.bank_id);
        }
        if (currentFilters.template_id && !response.filtered_by_template) {
            filtered = filtered.filter(s => s.template_id == currentFilters.template_id);
        }
        if (currentFilters.status && !response.filtered_by_status) {
            filtered = filtered.filter(s => s.status === currentFilters.status);
        }
        if (currentFilters.search) {
            const q = currentFilters.search.toLowerCase();
            filtered = filtered.filter(s =>
                (s.fieldman_id && s.fieldman_id.toLowerCase().includes(q)) ||
                (s.template && s.template.name && s.template.name.toLowerCase().includes(q)) ||
                s.id.toString().includes(q)
            );
        }

        renderTable(filtered);
        updatePagination(total);

    } catch (error) {
        console.error('Failed to load submissions:', error);
        body.innerHTML = '<tr><td colspan="7" class="text-center error-message">Error loading submissions. Please try again.</td></tr>';
    }
}

function renderTable(submissions) {
    const body = document.getElementById('submissionsBody');
    body.innerHTML = '';

    if (!submissions || submissions.length === 0) {
        body.innerHTML = '<tr><td colspan="7" class="text-center empty-state"><p>No submissions found</p></td></tr>';
        return;
    }

    submissions.forEach(sub => {
        const row = document.createElement('tr');
        row.className = 'submission-row';

        const statusClass = getStatusClass(sub.status);
        const bankName = sub.template && sub.template.bank ? sub.template.bank.name : 'Unknown';
        const templateName = sub.template ? sub.template.name : 'Unknown Template';

        row.innerHTML = `
            <td><strong>#${sub.id}</strong></td>
            <td>${sub.fieldman_id || 'N/A'}</td>
            <td>${templateName}</td>
            <td>${bankName}</td>
            <td><span class="badge ${statusClass}">${(sub.status || '').toUpperCase()}</span></td>
            <td>${formatDate(sub.created_at)}</td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-sm btn-outline" onclick="viewSubmission(${sub.id})" data-permission="submissions" data-action="read">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSubmission(${sub.id})" data-permission="submissions" data-action="delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        body.appendChild(row);
    });

    if (typeof enforceUIPermissions === 'function') {
        enforceUIPermissions();
    }
}

function getStatusClass(status) {
    const statusClasses = {
        'draft': 'badge-secondary',
        'submitted': 'badge-primary',
        'validated': 'badge-success',
        'rejected': 'badge-danger',
        'approved': 'badge-success'
    };
    return statusClasses[status] || 'badge-secondary';
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-PH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function viewSubmission(id) {
    const modal = document.getElementById('viewModal');
    const content = document.getElementById('modalContent');
    const approveBtn = document.getElementById('approveBtn');
    const rejectBtn = document.getElementById('rejectBtn');

    currentSubmissionId = id;
    content.innerHTML = '<div class="loading-spinner">Loading submission details...</div>';
    modal.classList.add('active');

    try {
        const sub = await apiGetSubmission(id);
        const bankName = sub.template && sub.template.bank ? sub.template.bank.name : 'Unknown Bank';
        const templateName = sub.template ? sub.template.name : 'Unknown Template';

        // 1. Applicant & Meta Info
        let html = `
            <div class="detail-group">
                <h4>Application Metadata</h4>
                <div class="detail-row">
                    <span class="detail-label">Submission ID</span>
                    <span class="detail-value">#${sub.id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status</span>
                    <span class="detail-value"><span class="badge ${getStatusClass(sub.status)}">${sub.status.toUpperCase()}</span></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Submitted On</span>
                    <span class="detail-value">${formatDate(sub.created_at)}</span>
                </div>
                 <div class="detail-row">
                    <span class="detail-label">Applicant/Fieldman</span>
                    <span class="detail-value">${sub.fieldman_id}</span>
                </div>
            </div>

            <div class="detail-group">
                <h4>Template Information</h4>
                <div class="detail-row">
                    <span class="detail-label">Form Template</span>
                    <span class="detail-value">${templateName}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Target Bank</span>
                    <span class="detail-value">${bankName}</span>
                </div>
            </div>
        `;

        // 2. Form Data
        html += '<div class="detail-group"><h4>Form Data</h4>';
        if (sub.data_json && Object.keys(sub.data_json).length > 0) {
            html += '<div class="form-data-grid">';
            for (const [key, value] of Object.entries(sub.data_json)) {
                const displayValue = value === true ? 'Yes' : (value === false ? 'No' : (value || '-'));
                html += `
                    <div class="data-card">
                        <span class="data-label">${formatFieldName(key)}</span>
                        <span class="data-value">${escapeHtml(displayValue)}</span>
                    </div>
                `;
            }
            html += '</div>';
        } else {
            html += '<p class="text-muted">No additional form data provided.</p>';
        }
        html += '</div>';

        content.innerHTML = html;

        // Show approve/reject buttons if user has submissions:review permission
        // Only show for submitted or validated submissions
        const currentUser = typeof getCurrentUser === 'function' ? getCurrentUser() : null;
        
        console.log('Button visibility check:', {
            user: currentUser?.username,
            status: sub.status,
            is_admin: currentUser?.is_admin,
            is_superuser: currentUser?.is_superuser,
            permissions: currentUser?.permissions,
            hasPermissionFunc: typeof hasPermission === 'function'
        });
        
        // Check permission using both formats for compatibility
        let hasReviewPerm = false;
        if (typeof hasPermission === 'function') {
            // Try format 1: 'submissions:review'
            hasReviewPerm = hasPermission('submissions:review');
            console.log('hasPermission("submissions:review"):', hasReviewPerm);
            
            // Try format 2: resource, action separately
            if (!hasReviewPerm) {
                hasReviewPerm = hasPermission('submissions', 'review');
                console.log('hasPermission("submissions", "review"):', hasReviewPerm);
            }
        }
        
        const canReview = currentUser && (
            currentUser.is_admin || 
            currentUser.is_superuser ||
            hasReviewPerm
        );
        
        console.log('Can review?', canReview, 'Status check:', (sub.status === 'submitted' || sub.status === 'validated'));
        
        if ((sub.status === 'submitted' || sub.status === 'validated') && canReview) {
            console.log('Showing approve/reject buttons');
            approveBtn.style.display = 'inline-block';
            rejectBtn.style.display = 'inline-block';
        } else {
            console.log('Hiding approve/reject buttons. Reason:', 
                !canReview ? 'No review permission' : 'Status not submitted/validated');
            approveBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        }

    } catch (error) {
        content.innerHTML = `<div class="alert alert-error">Failed to load details: ${error.message}</div>`;
    }
}



function formatFieldName(fieldId) {
    return fieldId
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

function escapeHtml(text) {
    if (typeof text !== 'string') return text;
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function approveSubmission() {
    if (!currentSubmissionId) return;

    try {
        await apiReviewSubmission(currentSubmissionId, { action: 'approve' });
        showToast('Submission approved successfully', 'success');
        closeModal();
        loadSubmissions();
    } catch (error) {
        showToast(error.message || 'Failed to approve submission', 'error');
    }
}

async function rejectSubmission() {
    if (!currentSubmissionId) return;

    const comment = prompt('Please provide a reason for rejection:');
    if (comment === null) return; // Cancelled

    try {
        await apiReviewSubmission(currentSubmissionId, { action: 'reject', comment: comment || 'Rejected' });
        showToast('Submission rejected', 'success');
        closeModal();
        loadSubmissions();
    } catch (error) {
        showToast(error.message || 'Failed to reject submission', 'error');
    }
}

async function deleteSubmission(id) {
    if (!confirm('Are you sure you want to delete this draft submission?')) return;

    try {
        await apiDeleteSubmission(id);
        showToast('Submission deleted successfully', 'success');
        loadSubmissions();
    } catch (error) {
        showToast(error.message || 'Failed to delete submission', 'error');
    }
}

function closeModal() {
    const modal = document.getElementById('viewModal');
    modal.classList.remove('active');
    currentSubmissionId = null;
}

function handleFilterChange() {
    currentFilters.bank_id = document.getElementById('bankFilter').value;
    const tfilter = document.getElementById('templateFilter');
    currentFilters.template_id = tfilter ? tfilter.value : '';
    currentFilters.status = document.getElementById('statusFilter').value;
    currentFilters.search = document.getElementById('searchInput').value;
    currentPage = 1;
    loadSubmissions();
}

function updatePagination(total) {
    const info = document.getElementById('paginationInfo');
    const btns = document.getElementById('paginationBtns');
    const itemsPerPage = 10;

    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, total);

    info.textContent = total > 0 ? `Showing ${start} to ${end} of ${total} entries` : 'No entries found';

    btns.innerHTML = '';
    const totalPages = Math.ceil(total / itemsPerPage);

    if (totalPages > 1) {
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = `btn btn-sm ${currentPage === 1 ? 'btn-secondary' : 'btn-outline'}`;
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {
            if (currentPage > 1) {
                currentPage--;
                loadSubmissions();
            }
        };
        btns.appendChild(prevBtn);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.className = `btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline'}`;
            btn.textContent = i;
            btn.onclick = () => {
                currentPage = i;
                loadSubmissions();
            };
            btns.appendChild(btn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = `btn btn-sm ${currentPage === totalPages ? 'btn-secondary' : 'btn-outline'}`;
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                loadSubmissions();
            }
        };
        btns.appendChild(nextBtn);
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

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('viewModal');
    if (e.target === modal) {
        closeModal();
    }
});

