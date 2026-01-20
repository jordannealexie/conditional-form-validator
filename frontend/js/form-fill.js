/**
 * form-fill.js: Controller for the dynamic form application page.
 */

let renderer = null;
let currentTemplate = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Check Authentication
    if (!isAuthenticated()) {
        window.location.href = '/index.html';
        return;
    }

    // 2. Extract Template ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get('template_id');

    if (!templateId) {
        alert('No template selected. Returning to dashboard.');
        window.location.href = '/dashboard.html';
        return;
    }

    // 3. Load User Info
    try {
        const user = await apiGetCurrentUser();
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
        document.getElementById('userName').textContent = fullName;
    } catch (error) {
        console.error('Failed to load user info:', error);
    }

    // 4. Load Template and Initialize Renderer
    await loadTemplate(templateId);

    // 5. Setup Buttons
    document.getElementById('submitBtn').addEventListener('click', handleSubmit);
    document.getElementById('saveDraftBtn').addEventListener('click', handleSaveDraft);
});

async function loadTemplate(templateId) {
    const container = document.getElementById('renderer-container');

    try {
        currentTemplate = await apiGetTemplate(templateId);

        // Update Page UI
        document.getElementById('formTitle').textContent = currentTemplate.name;
        document.getElementById('formDescription').textContent = currentTemplate.description || 'Please fill out all the required information below.';

        const bankBadge = document.getElementById('bankBadge');
        // We might need to fetch bank info if not in template, but usually we know the bank from ID/Context
        // For now, use a generic color scheme or look at bank_id
        bankBadge.textContent = currentTemplate.bank ? currentTemplate.bank.name : `Bank ID: ${currentTemplate.bank_id}`;
        bankBadge.classList.add('bg-indigo-100', 'text-indigo-800');

        // Initialize Renderer
        renderer = new FormRenderer('renderer-container', {
            onChanged: (data) => console.log('Form data changed:', data)
        });

        // Use the fields from the template
        renderer.render(currentTemplate.fields);

    } catch (error) {
        console.error('Failed to load template:', error);
        container.innerHTML = `
            <div class="p-8 text-center text-red-600 bg-red-50 rounded-xl">
                <i class="fas fa-exclamation-triangle text-3xl mb-2"></i>
                <p class="font-bold">Error loading form template</p>
                <p class="text-sm opacity-80">${error.message}</p>
            </div>
        `;
    }
}

async function handleSubmit() {
    if (!renderer || !currentTemplate) return;

    renderer.clearErrors();
    const data = renderer.getData();

    // Simple client-side check before API call
    // Note: The API does its own validation via FormValidator

    try {
        const payload = {
            template_id: currentTemplate.id,
            fieldman_id: getCurrentUser().username,
            data_json: data,
            status: 'submitted'
        };

        const result = await apiSubmitForm(payload);

        if (result.is_valid) {
            showSuccessModal();
        } else {
            // Show validation errors from server
            result.validation_errors.forEach(err => {
                renderer.showError(err.field, err.message);
            });
            alert('Please correct the errors in the form.');
        }
    } catch (error) {
        console.error('Submission error:', error);
        alert('Failed to submit application: ' + error.message);
    }
}

async function handleSaveDraft() {
    if (!renderer || !currentTemplate) return;

    const data = renderer.getData();

    try {
        const payload = {
            template_id: currentTemplate.id,
            fieldman_id: getCurrentUser().username,
            data_json: data,
            status: 'draft'
        };

        await apiSubmitForm(payload);
        alert('Draft saved successfully!');
    } catch (error) {
        console.error('Draft save error:', error);
        alert('Failed to save draft: ' + error.message);
    }
}

function showSuccessModal() {
    document.getElementById('successModal').classList.remove('hidden');
    document.getElementById('successModal').classList.add('flex');
}
