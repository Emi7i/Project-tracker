let editingId = null;
let draggedItem = null;
let openDropdownId = null;

// Generic dropdown functionality
function toggleDropdown(dropdownId, projectId, event) {
    event.stopPropagation();
    
    // Close any open dropdown
    if (openDropdownId) {
        var openDropdown = document.getElementById(openDropdownId);
        if (openDropdown) openDropdown.style.display = 'none';
    }
    
    const dropdown = document.getElementById(dropdownId);
    const isVisible = dropdown.style.display === 'block';
    
    if (isVisible) {
        dropdown.style.display = 'none';
        openDropdownId = null;
    } else {
        dropdown.style.display = 'block';
        openDropdownId = dropdownId;
    }
}

async function updateDropdown(dropdownId, projectId, value, updateUrl, color) {
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        
        // Determine field name based on updateUrl
        if (updateUrl.includes('status')) {
            formData.append('status', value || '');
        } else if (updateUrl.includes('priority')) {
            formData.append('priority', value);
        }
        
        const response = await fetch(updateUrl + projectId + '/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to update');
        }
    } catch (error) {
        alert('Error updating');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    if (openDropdownId) {
        var dropdown = document.getElementById(openDropdownId);
        if (dropdown && !dropdown.contains(e.target) && !e.target.closest('.badge')) {
            dropdown.style.display = 'none';
            openDropdownId = null;
        }
    }
});

// Sort dropdown functionality
let sortDropdownOpen = false;

function toggleSortDropdown(event) {
    event.stopPropagation();
    
    // Close any open dropdown
    if (openDropdownId) {
        var openDropdown = document.getElementById(openDropdownId);
        if (openDropdown) openDropdown.style.display = 'none';
    }
    
    const dropdown = document.getElementById('sort-dropdown');
    const isVisible = dropdown.style.display === 'block';
    
    if (isVisible) {
        dropdown.style.display = 'none';
        sortDropdownOpen = false;
    } else {
        dropdown.style.display = 'block';
        sortDropdownOpen = true;
    }
}

async function setSort(sortValue, sortLabel) {
    document.getElementById('sort-label').textContent = sortLabel;
    document.getElementById('sort-dropdown').style.display = 'none';
    sortDropdownOpen = false;
    
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        formData.append('sort_by', sortValue);
        
        const response = await fetch('/set-sort/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to set sort');
        }
    } catch (error) {
        alert('Error setting sort');
    }
}

// Group dropdown functionality
let groupDropdownOpen = false;

function toggleGroupDropdown(event) {
    event.stopPropagation();
    
    // Close any open dropdown
    if (openDropdownId) {
        var openDropdown = document.getElementById(openDropdownId);
        if (openDropdown) openDropdown.style.display = 'none';
    }
    
    const dropdown = document.getElementById('group-dropdown');
    const isVisible = dropdown.style.display === 'block';
    
    if (isVisible) {
        dropdown.style.display = 'none';
        groupDropdownOpen = false;
    } else {
        dropdown.style.display = 'block';
        groupDropdownOpen = true;
    }
}

async function setGroup(groupValue, groupLabel) {
    document.getElementById('group-label').textContent = groupLabel;
    document.getElementById('group-dropdown').style.display = 'none';
    groupDropdownOpen = false;
    
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        formData.append('group_by', groupValue);
        
        const response = await fetch('/set-group/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to set group');
        }
    } catch (error) {
        alert('Error setting group');
    }
}

async function swapTypeOrder() {
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        
        const response = await fetch('/swap-type-order/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to swap order');
        }
    } catch (error) {
        alert('Error swapping order');
    }
}

// Settings modal functions
function openSettings() {
    const modal = document.getElementById('settings-modal');
    modal.style.display = 'flex';
    
    // Load settings content
    fetch('/settings/')
        .then(response => response.text())
        .then(html => {
            document.getElementById('settings-content').innerHTML = html;
        });
}

function closeSettings() {
    const modal = document.getElementById('settings-modal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        // Add click listener to content box to prevent modal closing
        const contentBox = modal.querySelector('div');
        if (contentBox) {
            contentBox.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
        
        modal.addEventListener('click', function(e) {
            // Only close if clicking directly on the modal overlay (background)
            if (e.target === modal) {
                closeSettings();
            }
        });
    }
});

// Settings functions
function getCsrfToken() {
    // Try to get CSRF token from settings content first, then from global
    const settingsCsrf = document.querySelector('#settings-content input[name="csrfmiddlewaretoken"]');
    if (settingsCsrf) {
        return settingsCsrf.value;
    }
    const globalCsrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (globalCsrf) {
        return globalCsrf.value;
    }
    // Fallback to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

function toggleProfileDetails(profileId) {
    const details = document.getElementById(`profile-details-${profileId}`);
    if (details) {
        details.style.display = details.style.display === 'none' ? 'block' : 'none';
    }
}

function createProfile() {
    const name = document.getElementById('new-profile-name').value.trim();
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('name', name);
    
    fetch('/settings/create-profile/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                    // Re-attach content box click listener
                    const modal = document.getElementById('settings-modal');
                    const contentBox = modal.querySelector('div');
                    if (contentBox) {
                        contentBox.addEventListener('click', function(e) {
                            e.stopPropagation();
                        });
                    }
                });
        } else {
            alert(result.error || 'Failed to create profile');
        }
    })
    .catch(error => {
        console.error('Error creating profile:', error);
        alert('Error creating profile: ' + error.message);
    });
}

function activateProfile(profileId) {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch(`/settings/activate-profile/${profileId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                })
                .catch(error => {
                    console.error('Error fetching settings:', error);
                });
        } else {
            alert(result.error || 'Failed to activate profile');
        }
    })
    .catch(error => {
        console.error('Error activating profile:', error);
        alert('Error activating profile: ' + error.message);
    });
}

function deleteProfile(profileId) {
    if (!confirm('Are you sure you want to delete this profile?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch(`/settings/delete-profile/${profileId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to delete profile');
        }
    })
    .catch(error => {
        console.error('Error deleting profile:', error);
        alert('Error deleting profile: ' + error.message);
    });
}

function createTypeDefinition(profileId) {
    const name = document.getElementById(`type-name-${profileId}`).value.trim();
    const color = document.getElementById(`type-color-${profileId}`).value;
    
    if (!name) {
        alert('Please enter name');
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('profile_id', profileId);
    formData.append('name', name);
    formData.append('color', color);
    
    fetch('/settings/create-type-definition/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to create type definition');
        }
    })
    .catch(error => {
        console.error('Error creating type definition:', error);
        alert('Error creating type definition: ' + error.message);
    });
}

function createStatusDefinition(profileId) {
    const name = document.getElementById(`status-name-${profileId}`).value.trim();
    const color = document.getElementById(`status-color-${profileId}`).value;
    
    if (!name) {
        alert('Please enter name');
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('profile_id', profileId);
    formData.append('name', name);
    formData.append('color', color);
    
    fetch('/settings/create-status-definition/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to create status definition');
        }
    })
    .catch(error => {
        console.error('Error creating status definition:', error);
        alert('Error creating status definition: ' + error.message);
    });
}

function createPriorityDefinition(profileId) {
    const name = document.getElementById(`priority-name-${profileId}`).value.trim();
    const color = document.getElementById(`priority-color-${profileId}`).value;
    
    if (!name) {
        alert('Please enter name');
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    formData.append('profile_id', profileId);
    formData.append('name', name);
    formData.append('color', color);
    
    fetch('/settings/create-priority-definition/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to create priority definition');
        }
    })
    .catch(error => {
        console.error('Error creating priority definition:', error);
        alert('Error creating priority definition: ' + error.message);
    });
}

function deleteTypeDefinition(defId) {
    if (!confirm('Are you sure you want to delete this type?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch(`/settings/delete-type-definition/${defId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to delete type definition');
        }
    })
    .catch(error => {
        console.error('Error deleting type definition:', error);
        alert('Error deleting type definition: ' + error.message);
    });
}

function deleteStatusDefinition(defId) {
    if (!confirm('Are you sure you want to delete this status?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch(`/settings/delete-status-definition/${defId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to delete status definition');
        }
    })
    .catch(error => {
        console.error('Error deleting status definition:', error);
        alert('Error deleting status definition: ' + error.message);
    });
}

function deletePriorityDefinition(defId) {
    if (!confirm('Are you sure you want to delete this priority?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    fetch(`/settings/delete-priority-definition/${defId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Reload settings content instead of full page
            fetch('/settings/')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('settings-content').innerHTML = html;
                });
        } else {
            alert(result.error || 'Failed to delete priority definition');
        }
    })
    .catch(error => {
        console.error('Error deleting priority definition:', error);
        alert('Error deleting priority definition: ' + error.message);
    });
}

// Reordering functionality
let draggedDefinitionItem = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop for reorderable items
    document.addEventListener('dragstart', function(e) {
        if (e.target.classList.contains('reorderable-item')) {
            draggedDefinitionItem = e.target;
            e.target.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        }
    });
    
    document.addEventListener('dragend', function(e) {
        if (e.target.classList.contains('reorderable-item')) {
            e.target.style.opacity = '1';
            draggedDefinitionItem = null;
        }
    });
    
    document.addEventListener('dragover', function(e) {
        if (e.target.classList.contains('reorderable-item') && draggedDefinitionItem) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }
    });
    
    document.addEventListener('drop', function(e) {
        if (e.target.classList.contains('reorderable-item') && draggedDefinitionItem) {
            e.preventDefault();
            
            // Get the parent container
            const container = draggedDefinitionItem.parentElement;
            const type = draggedDefinitionItem.dataset.type;
            const profileId = draggedDefinitionItem.dataset.profile;
            
            // Reorder the items
            const items = Array.from(container.querySelectorAll('.reorderable-item'));
            const fromIndex = items.indexOf(draggedDefinitionItem);
            const toIndex = items.indexOf(e.target);
            
            if (fromIndex !== toIndex) {
                // Reorder in DOM
                if (fromIndex < toIndex) {
                    container.insertBefore(draggedDefinitionItem, e.target.nextSibling);
                } else {
                    container.insertBefore(draggedDefinitionItem, e.target);
                }
                
                // Update order on server
                const newOrder = Array.from(container.querySelectorAll('.reorderable-item')).map(item => item.dataset.id);
                
                let endpoint;
                if (type === 'type') {
                    endpoint = '/settings/reorder-type-definitions/';
                } else if (type === 'status') {
                    endpoint = '/settings/reorder-status-definitions/';
                } else if (type === 'priority') {
                    endpoint = '/settings/reorder-priority-definitions/';
                }
                
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', getCsrfToken());
                formData.append('order', JSON.stringify(newOrder));
                
                fetch(endpoint, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(result => {
                    if (!result.success) {
                        alert(result.error || 'Failed to reorder');
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error reordering:', error);
                    alert('Error reordering: ' + error.message);
                    location.reload();
                });
            }
        }
    });
});

// Drag and drop functionality
const projectList = document.getElementById('project-list');

projectList.addEventListener('dragstart', function(e) {
    const card = e.target.closest('.proj-card');
    if (card) {
        draggedItem = card;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    }
});

projectList.addEventListener('dragend', function(e) {
    const card = e.target.closest('.proj-card');
    if (card) {
        card.classList.remove('dragging');
        draggedItem = null;
        saveNewOrder();
    }
});

projectList.addEventListener('dragover', function(e) {
    e.preventDefault();
    const card = e.target.closest('.proj-card');
    if (card && card !== draggedItem) {
        const rect = card.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        
        if (e.clientY < midY) {
            projectList.insertBefore(draggedItem, card);
        } else {
            projectList.insertBefore(draggedItem, card.nextSibling);
        }
    }
});

async function saveNewOrder() {
    const cards = document.querySelectorAll('.proj-card');
    const orderData = [];
    
    cards.forEach((card, index) => {
        const id = card.getAttribute('data-id');
        orderData.push({ id: parseInt(id), order: index });
    });

    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        formData.append('order_data', JSON.stringify(orderData));
        
        const response = await fetch('/reorder/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!result.success) {
            console.error('Failed to save order');
        }
    } catch (error) {
        console.error('Error saving order:', error);
    }
}

function toggleForm() {
    editingId = null;
    document.getElementById('project-form').reset();
    // Set first type option as default
    const typeSelect = document.getElementById('f-type');
    if (typeSelect && typeSelect.options.length > 0) {
        typeSelect.value = typeSelect.options[0].value;
    }
    document.getElementById('save-btn').textContent = 'save project';
    document.getElementById('date-hint').textContent = '(optional)';
    const w = document.getElementById('form-wrap');
    w.style.display = w.style.display === 'none' ? 'block' : 'none';
    if (w.style.display === 'block') {
        document.getElementById('f-name').focus();
    }
}

function cancelForm() {
    editingId = null;
    document.getElementById('form-wrap').style.display = 'none';
}

function onTypeChange() {
    const t = document.getElementById('f-type').value;
    document.getElementById('date-hint').textContent = '(optional)';
}

document.getElementById('project-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    // Ensure CSRF token is included from the form itself
    const csrfToken = document.getElementById('global-csrf-token').value;
    formData.set('csrfmiddlewaretoken', csrfToken);
    
    const url = editingId ? '/update/' + editingId + '/' : '/create/';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'An error occurred');
        }
    } catch (error) {
        alert('An error occurred');
    }
});

async function editProject(id) {
    editingId = id;
    
    // Fetch project data
    try {
        const response = await fetch('/api/project/' + id + '/');
        const project = await response.json();
        
        document.getElementById('f-name').value = project.name;
        document.getElementById('f-type').value = project.project_type;
        document.getElementById('f-date').value = project.due_date || '';
        document.getElementById('f-action').value = project.next_action || '';
        document.getElementById('save-btn').textContent = 'update project';
        document.getElementById('date-hint').textContent = '(optional)';
        document.getElementById('form-wrap').style.display = 'block';
        document.getElementById('f-name').focus();
    } catch (error) {
        alert('Failed to load project data');
    }
}

async function deleteProject(id) {
    if (!confirm('Are you sure you want to delete this project?')) {
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        
        const response = await fetch('/delete/' + id + '/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'An error occurred');
        }
    } catch (error) {
        alert('An error occurred');
    }
}
