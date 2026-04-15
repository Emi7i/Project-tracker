let editingId = null;
let draggedItem = null;
let openDropdownId = null;

// Status dropdown functionality
function toggleStatusDropdown(projectId, event) {
    event.stopPropagation();
    
    // Close any open dropdown
    if (openDropdownId) {
        var openDropdown = document.getElementById(openDropdownId);
        if (openDropdown) openDropdown.style.display = 'none';
    }
    
    const dropdown = document.getElementById('status-dropdown-' + projectId);
    const isVisible = dropdown.style.display === 'block';
    
    if (isVisible) {
        dropdown.style.display = 'none';
        openDropdownId = null;
    } else {
        dropdown.style.display = 'block';
        openDropdownId = 'status-dropdown-' + projectId;
    }
}

async function setStatus(projectId, status) {
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        formData.append('status', status || '');
        
        const response = await fetch('/update-status/' + projectId + '/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to update status');
        }
    } catch (error) {
        alert('Error updating status');
    }
}

// Priority dropdown functionality
function togglePriorityDropdown(projectId, event) {
    event.stopPropagation();
    
    // Close any open dropdown
    if (openDropdownId) {
        var openDropdown = document.getElementById(openDropdownId);
        if (openDropdown) openDropdown.style.display = 'none';
    }
    
    const dropdown = document.getElementById('priority-dropdown-' + projectId);
    const isVisible = dropdown.style.display === 'block';
    
    if (isVisible) {
        dropdown.style.display = 'none';
        openDropdownId = null;
    } else {
        dropdown.style.display = 'block';
        openDropdownId = 'priority-dropdown-' + projectId;
    }
}

async function setPriority(projectId, priority) {
    try {
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.getElementById('global-csrf-token').value);
        formData.append('priority', priority);
        
        const response = await fetch('/update-priority/' + projectId + '/', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            window.location.reload();
        } else {
            alert(result.error || 'Failed to update priority');
        }
    } catch (error) {
        alert('Error updating priority');
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
    document.getElementById('f-type').value = 'corporate';
    document.getElementById('save-btn').textContent = 'save project';
    document.getElementById('date-hint').textContent = '(required for corporate)';
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
    
    // Fetch project data
    try {
        const response = await fetch('/api/project/' + id + '/');
        const project = await response.json();
        
        document.getElementById('f-name').value = project.name;
        document.getElementById('f-type').value = project.project_type;
        document.getElementById('f-date').value = project.due_date || '';
        document.getElementById('f-action').value = project.next_action || '';
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
