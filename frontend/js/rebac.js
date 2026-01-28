// ReBAC Management Module
// Handles relationship-based access control functionality using the real API

let relationshipsData = [];
let editingRelationshipId = null;
let rebacOptions = null;

/**
 * Initialize ReBAC page
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireAuth === 'function') requireAuth();
    loadUserInfo();
    
    // Load ReBAC options first
    try {
        rebacOptions = await apiGetRebacOptions();
        // Populate dropdowns with options
        populateDropdowns();
    } catch (error) {
        console.error('Error loading ReBAC options:', error);
    }
    
    loadRelationships();
    setupMobileMenu();
    
    // Enforce UI permissions after a short delay to ensure everything is loaded
    if (typeof enforceUIPermissions === 'function') {
        setTimeout(enforceUIPermissions, 100);
    }
});

/**
 * Populate dropdowns with data from API
 */
function populateDropdowns() {
    if (!rebacOptions) return;
    
    // Populate subject type
    const subjectTypeSelect = document.getElementById('subjectType');
    if (subjectTypeSelect && rebacOptions.subject_types) {
        subjectTypeSelect.innerHTML = '<option value="">Select Type</option>' +
            rebacOptions.subject_types.map(type => 
                `<option value="${escapeHtml(type)}">${escapeHtml(type.charAt(0).toUpperCase() + type.slice(1))}</option>`
            ).join('');
    }
    
    // Populate relationship type
    const relationSelect = document.getElementById('relation');
    if (relationSelect && rebacOptions.relationship_types) {
        relationSelect.innerHTML = '<option value="">Select Relationship</option>' +
            rebacOptions.relationship_types.map(type => 
                `<option value="${escapeHtml(type)}">${escapeHtml(type.charAt(0).toUpperCase() + type.slice(1))}</option>`
            ).join('');
    }
    
    // Populate resource type
    const objectTypeSelect = document.getElementById('objectType');
    if (objectTypeSelect && rebacOptions.resource_types) {
        objectTypeSelect.innerHTML = '<option value="">Select Type</option>' +
            rebacOptions.resource_types.map(type => 
                `<option value="${escapeHtml(type)}">${escapeHtml(type.charAt(0).toUpperCase() + type.slice(1))}</option>`
            ).join('');
    }
    
    // Populate parent resource type (same as resource types)
    const parentTypeSelect = document.getElementById('parentResourceType');
    if (parentTypeSelect && rebacOptions.resource_types) {
        parentTypeSelect.innerHTML = '<option value="">Select Type</option>' +
            rebacOptions.resource_types.map(type => 
                `<option value="${escapeHtml(type)}">${escapeHtml(type.charAt(0).toUpperCase() + type.slice(1))}</option>`
            ).join('');
    }
}

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

    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.textContent = 'Add New Relationship';
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
        
        // Enforce permissions after loading
        if (typeof enforceUIPermissions === 'function') {
            enforceUIPermissions();
        }
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
    
    // Add badge styling to relationship type
    const relationshipClass = relationship.relationship_type.toLowerCase();

    const createdAt = relationship.created_at ? new Date(relationship.created_at).toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'}) : 'N/A';
    const updatedAt = relationship.updated_at ? new Date(relationship.updated_at).toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'}) : 'N/A';

    row.innerHTML = `
        <td>${relationship.id}</td>
        <td>${escapeHtml(subject)}</td>
        <td><span class="relationship-badge ${relationshipClass}">${escapeHtml(relationship.relationship_type)}</span></td>
        <td>${escapeHtml(object)}</td>
        <td style="font-size: 0.85em;">${createdAt}</td>
        <td style="font-size: 0.85em;">${updatedAt}</td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="editRelationship(${relationship.id})" data-permission="relationships" data-action="update">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteRelationship(${relationship.id})" data-permission="relationships" data-action="delete">Delete</button>
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
    document.getElementById('parentResourceType').value = rel.parent_resource_type;
    document.getElementById('parentResourceId').value = rel.parent_resource_id;

    // Update UI
    const btn = document.querySelector('#addRelationshipForm button[type="submit"]');
    if (btn) btn.textContent = 'Update Relationship';
    
    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.textContent = 'Edit Relationship';

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
        const parentResourceType = document.getElementById('parentResourceType').value;
        const parentResourceId = document.getElementById('parentResourceId').value;

        const payload = {
            subject_type: subjectType,
            subject_id: subjectId,
            relationship_type: relation,
            resource_type: objectType,
            resource_id: objectId,
            parent_resource_type: parentResourceType,
            parent_resource_id: parentResourceId
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
            resetForm();
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
