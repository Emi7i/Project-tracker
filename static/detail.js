// Motivational Footer Logic
const motivationalMessages = [
    "You got this! 🐈‍⬛",
    "Just a bit more today! 🐛☕",
    "You'll get there! ⛳",
];

function setRandomFooter() {
    const el = document.getElementById('motivational-footer');
    if (el) {
        const index = Math.floor(Math.random() * motivationalMessages.length);
        el.innerText = motivationalMessages[index];
    }
}

// Utility to set text color based on background brightness
function getContrastColor(colorStr) {
    if (!colorStr || colorStr === 'transparent') return '#111827';
    
    let r, g, b;
    if (colorStr.startsWith('rgb')) {
        const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (match) {
            r = parseInt(match[1]);
            g = parseInt(match[2]);
            b = parseInt(match[3]);
        } else return '#111827';
    } else {
        // Hex handling
        let hex = colorStr.replace('#', '');
        if (hex.length === 3) hex = hex.split('').map(s => s + s).join('');
        r = parseInt(hex.slice(0, 2), 16);
        g = parseInt(hex.slice(2, 4), 16);
        b = parseInt(hex.slice(4, 6), 16);
    }

    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return (brightness > 150) ? '#111827' : '#ffffff';
}

function setPillTextColor(pill) {
    let bgColor = pill.style.backgroundColor;
    if (!bgColor || bgColor === '') {
        bgColor = window.getComputedStyle(pill).backgroundColor;
    }
    pill.style.color = getContrastColor(bgColor);
}

function updateAllPillColors() {
    document.querySelectorAll('.status-pill').forEach(pill => {
        setPillTextColor(pill);
    });
}

// UI Interaction Helpers
function selectAndFocus(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.contentEditable = "true";
    el.focus();
    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}

function enterEditMode(container) {
    container.classList.add('editing');
    const input = container.querySelector('.edit-input');
    if (input) input.focus();
}

function exitEditMode(container) {
    container.classList.remove('editing');
}

function formatDisplayDate(isoDate) {
    if (!isoDate) return '—';
    const parts = isoDate.split('-');
    return `${parts[2]}. ${parts[1]}. ${parts[0]}.`;
}

// API Calls
async function apiPost(url, data) {
    const formData = new FormData();
    for (const key in data) formData.append(key, data[key]);
    
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': document.getElementById('global-csrf-token').value }
    });
    return await response.json();
}

async function updateProjectName(newName) {
    const el = document.getElementById('project-name-heading');
    el.contentEditable = "false";
    const data = await apiPost(`/api/project/${projectId}/update-name/`, { name: newName });
    if (data.success) document.title = `${newName} - Project Tracker`;
}

async function updateSectionName(sectionId, newName) {
    const el = document.getElementById(`section-name-${sectionId}`);
    el.contentEditable = "false";
    await apiPost(`/api/section/${sectionId}/update/`, { name: newName });
}

async function deleteSection(sectionId) {
    if (!confirm('Are you sure you want to delete this section and all its tasks?')) return;
    const data = await apiPost(`/api/section/${sectionId}/delete/`, {});
    if (data.success) document.getElementById(`section-${sectionId}`).remove();
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    const data = await apiPost(`/api/task/${taskId}/delete/`, {});
    if (data.success) document.getElementById(`task-${taskId}`).remove();
}

function openStatusModal() {
    document.getElementById('status-modal').style.display = 'flex';
}

function closeStatusModal() {
    document.getElementById('status-modal').style.display = 'none';
}

async function addNewStatus() {
    const name = prompt('Enter status name:');
    if (!name) return;
    const data = await apiPost(`/api/project/${projectId}/status/create/`, { name });
    if (data.success) window.location.reload();
}

async function updateStatus(statusId, field, value) {
    await apiPost(`/api/status/${statusId}/update/`, { [field]: value });
}

async function deleteStatus(statusId) {
    if (!confirm('Are you sure? Tasks with this status will have no status.')) return;
    const data = await apiPost(`/api/status/${statusId}/delete/`, {});
    if (data.success) window.location.reload();
}

async function updateTask(taskId, field, value, container = null) {
    if (field === 'name') {
        const el = document.getElementById(`task-name-${taskId}`);
        if (el) el.contentEditable = "false";
    }
    const data = await apiPost(`/api/task/${taskId}/update/`, { field, value });
    if (data.success && container) {
        const displayText = container.querySelector('.display-text');
        if (field === 'due_date') {
            displayText.innerText = formatDisplayDate(value);
        } else if (field === 'time_tracked') {
            displayText.innerText = `${value}h`;
        } else if (field === 'status') {
            const select = container.querySelector('select');
            const opt = select.options[select.selectedIndex];
            displayText.innerText = opt.text;
            displayText.style.backgroundColor = opt.getAttribute('data-color');
            displayText.style.color = opt.getAttribute('data-text-color');
            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-chevron-down';
            icon.style.fontSize = '0.75rem';
            icon.style.marginLeft = '0.25rem';
            displayText.appendChild(icon);
        } else if (field === 'waiting_on') {
            if (value) {
                const select = container.querySelector('select');
                displayText.innerText = select.options[select.selectedIndex].text;
                displayText.style.color = '#2563eb';
                displayText.style.fontWeight = '500';
            } else {
                displayText.innerHTML = '<i class="fa-solid fa-plus-circle" style="font-size: 0.75rem;"></i> Add';
                displayText.style.color = '#9ca3af';
                displayText.style.fontWeight = '400';
            }
        }
    } else if (!data.success) {
        alert('Failed to update task');
    }
}

function toggleSection(sectionId) {
    const content = document.getElementById(`section-content-${sectionId}`);
    if (content) content.classList.toggle('collapsed');
}

async function addNewSection() {
    const name = prompt('Enter section name:');
    if (!name) return;
    const data = await apiPost(`/api/project/${projectId}/section/create/`, { name });
    if (data.success) window.location.reload();
}

async function addNewTask(sectionId) {
    const name = prompt('Enter task name:');
    if (!name) return;
    const data = await apiPost(`/api/section/${sectionId}/task/create/`, { name });
    if (data.success) window.location.reload();
}

async function updateProjectSort(sortBy) {
    const sections = document.querySelectorAll('section[data-section-id]');
    for (const section of sections) {
        const sectionId = section.getAttribute('data-section-id');
        await apiPost(`/api/section/${sectionId}/set-sort/`, { sort_by: sortBy });
    }
    window.location.reload();
}

async function setNextTask(taskId) {
    const data = await apiPost(`/api/project/${projectId}/set-next-task/`, { task_id: taskId });
    if (data.success) window.location.reload();
}

// Drag and Drop Logic
let draggedItem = null;
let dragType = null;

// Dynamically enable/disable dragging to allow text selection
document.addEventListener('mousedown', (e) => {
    const target = e.target;
    const editable = target.closest('[contenteditable="true"], input, select, .click-to-edit, .status-pill, .action-icons, .next-task-arrow');
    
    const taskRow = target.closest('.task-row');
    const sectionRow = target.closest('.project-section');
    
    if (editable) {
        if (taskRow) taskRow.setAttribute('draggable', 'false');
        if (sectionRow) sectionRow.setAttribute('draggable', 'false');
    } else {
        if (taskRow) taskRow.setAttribute('draggable', 'true');
        if (sectionRow) {
            // Only allow dragging section if we're in the header area or the specific drag handle
            if (target.closest('.section-header-container')) {
                sectionRow.setAttribute('draggable', 'true');
            } else {
                sectionRow.setAttribute('draggable', 'false');
            }
        }
    }
});

document.addEventListener('dragstart', (e) => {
    if (e.target.classList.contains('task-row')) {
        draggedItem = e.target;
        dragType = 'task';
        e.target.style.opacity = '0.5';
    } else if (e.target.classList.contains('project-section')) {
        draggedItem = e.target;
        dragType = 'section';
        e.target.style.opacity = '0.5';
    }
});

document.addEventListener('dragend', (e) => {
    if (draggedItem) {
        draggedItem.style.opacity = '1';
        draggedItem = null;
        dragType = null;
    }
});

document.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (!draggedItem) return;

    if (dragType === 'task') {
        const container = e.target.closest('.tasks-container');
        if (!container) return;
        const afterElement = getDragAfterElement(container, e.clientY, '.task-row');
        if (afterElement == null) container.appendChild(draggedItem);
        else container.insertBefore(draggedItem, afterElement);
    } else if (dragType === 'section') {
        const container = document.getElementById('sections-container');
        const afterElement = getDragAfterElement(container, e.clientY, '.project-section');
        if (afterElement == null) container.appendChild(draggedItem);
        else container.insertBefore(draggedItem, afterElement);
    }
});

document.addEventListener('drop', async (e) => {
    e.preventDefault();
    if (!draggedItem) return;

    if (dragType === 'task') {
        const container = draggedItem.closest('.tasks-container');
        const tasks = Array.from(container.querySelectorAll('.task-row'));
        const orderData = tasks.map((task, index) => ({
            id: task.getAttribute('data-task-id'),
            order: index
        }));
        await apiPost('/api/task/reorder/', { order_data: JSON.stringify(orderData) });
    } else if (dragType === 'section') {
        const container = document.getElementById('sections-container');
        const sections = Array.from(container.querySelectorAll('.project-section'));
        const orderData = sections.map((section, index) => ({
            id: section.getAttribute('data-section-id'),
            order: index
        }));
        await apiPost('/api/section/reorder/', { order_data: JSON.stringify(orderData) });
    }
});

function getDragAfterElement(container, y, selector) {
    const draggableElements = [...container.querySelectorAll(`${selector}:not([style*="opacity: 0.5"])`)];
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) return { offset: offset, element: child };
        else return closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Initialization
window.addEventListener('DOMContentLoaded', () => {
    setRandomFooter();
    updateAllPillColors();
});
