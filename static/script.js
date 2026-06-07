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

async function updateDropdown(dropdownId, projectId, value, updateUrl, event) {
    if (event) event.stopPropagation();
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

async function setSort(sortValue, sortLabel, event) {
    if (event) event.stopPropagation();
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

async function setGroup(groupValue, groupLabel, event) {
    if (event) event.stopPropagation();
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

// Drag and drop functionality
const projectList = document.getElementById('project-list');

projectList.addEventListener('dragstart', function(e) {
    // Prevent dragging when interacting with editable fields
    if (e.target.closest('[contenteditable="true"]') || e.target.closest('input') || e.target.closest('select')) {
        e.preventDefault();
        return;
    }

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
    document.getElementById('f-type').value = 'corporate';
    document.getElementById('save-btn').textContent = 'save project';
    document.getElementById('date-hint').textContent = '(required for corporate)';
    
    // Reset next action field to text input for new projects
    document.getElementById('f-action').style.display = 'block';
    document.getElementById('f-task-select').style.display = 'none';
    
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
    document.getElementById('date-hint').textContent = t === 'corporate' ? '(required)' : '(optional)';
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
    
    try {
        const response = await fetch('/api/project/' + id + '/');
        const project = await response.json();
        
        document.getElementById('f-name').value = project.name;
        document.getElementById('f-type').value = project.project_type;
        document.getElementById('f-date').value = project.due_date || '';
        
        // Setup Task Dropdown for editing
        const select = document.getElementById('f-task-select');
        const input = document.getElementById('f-action');
        
        select.innerHTML = '<option value="">(no next task)</option>';
        if (project.all_tasks) {
            project.all_tasks.forEach(task => {
                const opt = document.createElement('option');
                opt.value = task.id;
                opt.textContent = task.name;
                if (task.id == project.next_task_id) opt.selected = true;
                select.appendChild(opt);
            });
        }
        
        input.style.display = 'none';
        select.style.display = 'block';
        
        document.getElementById('save-btn').textContent = 'update project';
        document.getElementById('date-hint').textContent = project.project_type === 'corporate' ? '(required)' : '(optional)';
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
