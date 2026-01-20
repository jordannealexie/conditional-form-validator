// ReBAC Management Module
// Handles relationship-based access control functionality using the real API

/**
 * Initialize ReBAC page
 */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    loadRelationships();
    setupMobileMenu();
});

/**
 * Load current user info for sidebar
 */
async function loadUserInfo() {
    try {
        const currentUser = await apiGetCurrentUser();
        if (currentUser) {
            document.getElementById('userName').textContent = currentUser.full_name || currentUser.username;
            document.getElementById('userRole').textContent = currentUser.roles?.join(', ') || 'User';
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Setup mobile menu
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

/**
 * Toggle add relationship form visibility
 */
function toggleAddRelationshipForm() {
    const form = document.getElementById('addRelationshipForm');
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Load and display all relationships
 */
async function loadRelationships() {
    try {
        const relationships = await apiGetRelationships();
        const tableBody = document.getElementById('relationshipsTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (!relationships || relationships.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No relationships found</td></tr>';
            return;
        }

        relationships.forEach(relationship => {
            const row = createRelationshipRow(relationship);
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading relationships:', error);
        showToast('Error loading relationships', 'error');
    }
}

/**
 * Create a table row for a relationship
 * @param {object} relationship 
 * @returns {HTMLElement}
 */
function createRelationshipRow(relationship) {
    const row = document.createElement('tr');

    const subject = `${relationship.source_type}: ${relationship.source_name || relationship.source_id}`;
    const object = `${relationship.target_type}: ${relationship.target_name || relationship.target_id}`;

    row.innerHTML = `
        <td>${escapeHtml(subject)}</td>
        <td><span class="badge badge-secondary">${relationship.relation}</span></td>
        <td>${escapeHtml(object)}</td>
        <td>${new Date(relationship.created_at).toLocaleDateString()}</td>
        <td>
            <button class="btn btn-sm btn-danger" onclick="deleteRelationship(${relationship.id})">Delete</button>
        </td>
    `;

    return row;
}

/**
 * Handle relationship creation
 */
const addRelationshipForm = document.getElementById('addRelationshipForm');
if (addRelationshipForm) {
    addRelationshipForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const subjectType = document.getElementById('subjectType').value;
        const subjectId = document.getElementById('subjectId').value;
        const relation = document.getElementById('relation').value;
        const objectType = document.getElementById('objectType').value;
        const objectId = document.getElementById('objectId').value;

        try {
            await apiCreateRelationship({
                source_type: subjectType,
                source_id: subjectId,
                relation: relation,
                target_type: objectType,
                target_id: objectId
            });

            showToast('Relationship created successfully', 'success');
            e.target.reset();
            toggleAddRelationshipForm();
            loadRelationships();
        } catch (error) {
            console.error('Error creating relationship:', error);
            showToast(error.message || 'Error creating relationship', 'error');
        }
    });
}

/**
 * Delete a relationship
 */
async function deleteRelationship(relationshipId) {
    if (confirm('Are you sure you want to delete this relationship?')) {
        try {
            await apiDeleteRelationship(relationshipId);
            showToast('Relationship deleted successfully', 'success');
            loadRelationships();
        } catch (error) {
            console.error('Error deleting relationship:', error);
            showToast(error.message || 'Error deleting relationship', 'error');
        }
    }
}

/**
 * Check relationship path between two entities
 */
async function checkRelationshipPath(sourceId, targetId) {
    try {
        const result = await apiCheckPath(sourceId, targetId);
        if (result.has_path) {
            showToast(`Path found with ${result.path.length} steps`, 'success');
        } else {
            showToast('No relationship path found', 'info');
        }
    } catch (error) {
        console.error('Error checking path:', error);
        showToast('Error checking relationship path', 'error');
    }
}
