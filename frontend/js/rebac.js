// ReBAC Management Module
// Handles relationship-based access control functionality using the real API

let relationshipsData = [];
let editingRelationshipId = null;

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
        updateAppUserDisplay(currentUser);
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
 * Toggle add relationship form visibility and reset
 */
function toggleAddRelationshipForm(show = null) {
    const form = document.getElementById('addRelationshipForm');
    if (form) {
        const isHidden = form.style.display === 'none';
        const shouldShow = show !== null ? show : isHidden;

        form.style.display = shouldShow ? 'block' : 'none';

        if (!shouldShow) {
            resetForm();
        }
    }
}

function resetForm() {
    editingRelationshipId = null;
    const form = document.getElementById('addRelationshipForm');
    if (form) form.reset();

    const btn = document.querySelector('#addRelationshipForm button[type="submit"]');
    if (btn) btn.textContent = 'Create Relationship';

    const header = document.querySelector('.section-header h2');
    if (header) header.innerText = 'Add New Relationship'; // Reset header if changed
}

/**
 * Load and display all relationships
 */
async function loadRelationships() {
    try {
        relationshipsData = await apiGetRelationships();
        const tableBody = document.getElementById('relationshipsTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (!relationshipsData || relationshipsData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No relationships found</td></tr>';
            return;
        }

        relationshipsData.forEach(relationship => {
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

    // Use backend field names: subject_type, relationship_type, resource_type
    const subject = `${relationship.subject_type}: ${relationship.subject_id}`;
    const object = `${relationship.resource_type}: ${relationship.resource_id}`;

    row.innerHTML = `
        <td>${relationship.id}</td>
        <td>${escapeHtml(subject)}</td>
        <td><span class="badge badge-secondary">${escapeHtml(relationship.relationship_type)}</span></td>
        <td>${escapeHtml(object)}</td>
        <td>${new Date(relationship.created_at).toLocaleDateString()}</td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="editRelationship(${relationship.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteRelationship(${relationship.id})">Delete</button>
        </td>
    `;

    return row;
}

/**
 * Edit Relationship
 */
function editRelationship(id) {
    const rel = relationshipsData.find(r => r.id === id);
    if (!rel) return;

    editingRelationshipId = id;

    // Populate form
    document.getElementById('subjectType').value = rel.subject_type;
    document.getElementById('subjectId').value = rel.subject_id;
    document.getElementById('relation').value = rel.relationship_type;
    document.getElementById('objectType').value = rel.resource_type;
    document.getElementById('objectId').value = rel.resource_id;

    // Update UI
    const btn = document.querySelector('#addRelationshipForm button[type="submit"]');
    if (btn) btn.textContent = 'Update Relationship';

    // We might want to change the header text too 
    // document.querySelector('.section-header h2').innerText = 'Edit Relationship';

    toggleAddRelationshipForm(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Handle relationship creation/update
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

        // Backend expects: subject_type, subject_id, relationship_type, resource_type, resource_id
        // And parent_resource_type/id (we will default these or let backend handle)
        // I'll send them equal to resource for flat structure if backend requires them.

        const payload = {
            subject_type: subjectType,
            subject_id: subjectId,
            relationship_type: relation,
            resource_type: objectType,
            resource_id: objectId,
            // Provide defaults for strict backend requirements if needed
            parent_resource_type: objectType,
            parent_resource_id: objectId
        };

        try {
            if (editingRelationshipId) {
                await apiUpdateRelationship(editingRelationshipId, payload);
                showToast('Relationship updated successfully', 'success');
            } else {
                await apiCreateRelationship(payload);
                showToast('Relationship created successfully', 'success');
            }

            e.target.reset();
            toggleAddRelationshipForm(false);
            loadRelationships();
        } catch (error) {
            console.error('Error saving relationship:', error);
            showToast(error.message || 'Error saving relationship', 'error');
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
