let currentCommentsRequestId = null;

const STATUS_TEXT_COLORS = {
    '#e3f2fd': '#1565C0',
    '#fff9c4': '#F57F17',
    '#fff3e0': '#E65100',
    '#c8e6c9': '#2E7D32',
    '#ffebee': '#C62828',
    '#eeeeee': '#616161',
};

function getStatusTextColor(color) {
    return STATUS_TEXT_COLORS[color] || '#E65100';
}

async function loadStats() {
    try {
        const stats = await apiRequest('/requests/stats/summary');
        const map = {
            statTotal: stats.total,
            statNew: stats.new,
            statProgress: stats.in_progress,
            statOverdue: stats.overdue,
            statEnrolled: stats.enrolled,
        };
        for (const [id, val] of Object.entries(map)) {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        }
    } catch (err) {
        console.error('stats:', err);
    }
}

async function loadRequests() {
    const search = document.getElementById('searchInput')?.value || '';
    const statusId = document.getElementById('statusFilter')?.value || '';
    const subject = document.getElementById('subjectFilter')?.value || '';
    const sourceId = document.getElementById('sourceFilter')?.value || '';
    const managerId = document.getElementById('managerFilter')?.value || '';
    const onlyOverdue = document.getElementById('overdueOnly')?.checked || false;
    const sortBy = document.getElementById('sortBy')?.value || 'created_at';
    const sortOrder = document.getElementById('sortOrder')?.value || 'desc';

    let url = `/requests/?limit=200&offset=0&sort_by=${sortBy}&sort_order=${sortOrder}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (statusId) url += `&status_id=${statusId}`;
    if (subject) url += `&subject=${encodeURIComponent(subject)}`;
    if (sourceId) url += `&source_id=${sourceId}`;
    if (managerId) url += `&manager_id=${managerId}`;
    if (onlyOverdue) url += `&only_overdue=true`;

    showLoading(true);
    try {
        const requests = await apiRequest(url);
        const tbody = document.getElementById('requestsTableBody');
        const empty = document.getElementById('emptyState');
        tbody.innerHTML = '';

        if (!requests.length) {
            if (empty) empty.style.display = 'block';
            return;
        }
        if (empty) empty.style.display = 'none';

        for (const req of requests) {
            const row = tbody.insertRow();
            row.className = 'fade-in';
            const bg = req.is_overdue ? '#ffebee' : (req.status_color || 'transparent');
            row.style.backgroundColor = bg;

            row.insertCell(0).textContent = req.application_number;
            row.insertCell(1).textContent = formatDate(req.created_at);
            row.insertCell(2).textContent = req.student_full_name;
            row.insertCell(3).textContent = req.student_grade;
            row.insertCell(4).textContent = req.course_name || '—';

            const statusCell = row.insertCell(5);
            const textColor = getStatusTextColor(req.status_color);
            const label = req.is_overdue ? `${req.status_name} ⚠` : req.status_name;
            statusCell.innerHTML = `<span class="status-badge" style="background:${bg}; color:${textColor}; border:1px solid ${textColor}30">${escapeHtml(label || '—')}</span>`;

            row.insertCell(6).textContent = req.manager_name || '—';
            const contactCell = row.insertCell(7);
            contactCell.textContent = formatDate(req.next_contact_date);
            if (req.is_overdue) contactCell.style.color = '#C62828';

            const actions = row.insertCell(8);
            actions.className = 'action-buttons';
            actions.innerHTML = `
                <button class="action-btn" onclick="openCommentsModal(${req.id})" title="комментарии">💬</button>
                <button class="action-btn" onclick="openEditModal(${req.id})" title="редактировать">✏️</button>
                ${canDeleteRequests() ? `<button class="action-btn delete" onclick="deleteRequest(${req.id})" title="удалить">🗑️</button>` : ''}
            `;
        }
        loadStats();
    } catch (err) {
        showNotification(err.message, true);
    } finally {
        showLoading(false);
    }
}

async function exportRequests() {
    try {
        await apiDownload('/requests/export/csv', 'umax_заявки.csv');
        showNotification('файл экспортирован');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function loadSelectData() {
    const [sources, statuses, managers, courses, subjects] = await Promise.all([
        apiRequest('/requests/sources/list'),
        apiRequest('/requests/statuses/list'),
        apiRequest('/requests/managers/list'),
        apiRequest('/courses/?limit=200'),
        apiRequest('/courses/subjects/list'),
    ]);

    const fill = (id, options, placeholder) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = (placeholder || '') + options;
    };

    fill('sourceId', sources.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`), '<option value="">-- выберите --</option>');
    fill('statusId', statuses.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`));
    fill('statusFilter', statuses.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`), '<option value="">все</option>');
    fill('managerId', managers.map(m => `<option value="${m.id}">${escapeHtml(m.full_name)}</option>`));
    fill('managerFilter', managers.map(m => `<option value="${m.id}">${escapeHtml(m.full_name)}</option>`), '<option value="">все</option>');
    fill('courseId', courses.map(c => `<option value="${c.id}" data-seats="${c.free_seats}">${escapeHtml(c.name)} (${c.price}₽, мест: ${c.free_seats})</option>`));
    fill('subjectFilter', subjects.map(s => `<option value="${s}">${escapeHtml(s)}</option>`), '<option value="">все</option>');
    fill('sourceFilter', sources.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`), '<option value="">все</option>');
}

async function openCreateModal() {
    document.getElementById('modalTitle').textContent = 'новая заявка';
    document.getElementById('editId').value = '';
    ['studentName', 'parentName', 'phone', 'email', 'nextContact', 'comment'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('studentGrade').value = '9';
    document.getElementById('seatsWarning').style.display = 'none';
    await loadSelectData();

    const user = getCurrentUser();
    if (user.role === 'manager') {
        document.getElementById('managerId').value = user.id;
    }

    document.getElementById('requestModal').classList.add('active');
}

async function openEditModal(id) {
    try {
        const req = await apiRequest(`/requests/${id}`);
        document.getElementById('modalTitle').textContent = 'редактирование заявки';
        document.getElementById('editId').value = req.id;
        document.getElementById('studentName').value = req.student_full_name;
        document.getElementById('studentGrade').value = req.student_grade;
        document.getElementById('parentName').value = req.parent_full_name || '';
        document.getElementById('phone').value = req.phone;
        document.getElementById('email').value = req.email || '';
        document.getElementById('nextContact').value = req.next_contact_date || '';
        document.getElementById('comment').value = req.comment || '';
        await loadSelectData();
        document.getElementById('courseId').value = req.course_id;
        document.getElementById('sourceId').value = req.source_id;
        document.getElementById('statusId').value = req.status_id;
        document.getElementById('managerId').value = req.manager_id;
        checkCourseSeats();
        document.getElementById('requestModal').classList.add('active');
    } catch (err) {
        showNotification(err.message, true);
    }
}

function checkCourseSeats() {
    const select = document.getElementById('courseId');
    const warning = document.getElementById('seatsWarning');
    if (!select || !warning) return;
    const opt = select.options[select.selectedIndex];
    const seats = parseInt(opt?.dataset.seats || '0');
    if (seats <= 0) {
        warning.textContent = '⚠️ на этом курсе нет свободных мест';
        warning.style.display = 'block';
    } else if (seats <= 3) {
        warning.textContent = `⚠️ осталось мало мест: ${seats}`;
        warning.style.display = 'block';
    } else {
        warning.style.display = 'none';
    }
}

async function saveRequest() {
    const id = document.getElementById('editId').value;
    const data = {
        student_full_name: document.getElementById('studentName').value.trim(),
        student_grade: parseInt(document.getElementById('studentGrade').value),
        parent_full_name: document.getElementById('parentName').value.trim() || null,
        phone: document.getElementById('phone').value.trim(),
        email: document.getElementById('email').value.trim() || null,
        course_id: parseInt(document.getElementById('courseId').value),
        source_id: parseInt(document.getElementById('sourceId').value),
        status_id: parseInt(document.getElementById('statusId').value),
        manager_id: parseInt(document.getElementById('managerId').value),
        next_contact_date: document.getElementById('nextContact').value || null,
        comment: document.getElementById('comment').value.trim() || null,
    };

    if (!data.student_full_name || !data.phone || !data.course_id || !data.source_id || !data.status_id || !data.manager_id) {
        showNotification('заполните обязательные поля', true);
        return;
    }

    showLoading(true);
    try {
        if (id) {
            await apiRequest(`/requests/${id}`, 'PUT', data);
        } else {
            await apiRequest('/requests/', 'POST', data);
        }
        closeModal();
        loadRequests();
        showNotification('заявка сохранена');
    } catch (err) {
        showNotification(err.message, true);
    } finally {
        showLoading(false);
    }
}

async function deleteRequest(id) {
    if (!confirm('Удалить заявку? Действие необратимо.')) return;
    try {
        await apiRequest(`/requests/${id}`, 'DELETE');
        loadRequests();
        showNotification('заявка удалена');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function openCommentsModal(requestId) {
    currentCommentsRequestId = requestId;
    await loadComments(requestId);
    document.getElementById('commentsModal').classList.add('active');
}

async function loadComments(requestId) {
    const comments = await apiRequest(`/requests/${requestId}/comments`);
    const container = document.getElementById('commentsList');
    container.innerHTML = comments.length
        ? comments.map(c => `
            <div class="comment-item">
                <div class="comment-author">${escapeHtml(c.user_name || 'менеджер')}</div>
                <div class="comment-text">${escapeHtml(c.comment)}</div>
                <div class="comment-date">${formatDateTime(c.created_at)}</div>
            </div>`).join('')
        : '<p class="empty-text">нет комментариев</p>';
}

async function addComment() {
    const comment = document.getElementById('newComment').value.trim();
    if (!comment) return;
    try {
        await apiRequest(`/requests/${currentCommentsRequestId}/comments`, 'POST', { comment });
        document.getElementById('newComment').value = '';
        await loadComments(currentCommentsRequestId);
        showNotification('комментарий добавлен');
    } catch (err) {
        showNotification(err.message, true);
    }
}

function closeModal() {
    document.getElementById('requestModal').classList.remove('active');
}

function closeCommentsModal() {
    document.getElementById('commentsModal').classList.remove('active');
}

function resetFilters() {
    ['searchInput'].forEach(id => document.getElementById(id).value = '');
    ['statusFilter', 'subjectFilter', 'sourceFilter', 'managerFilter'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('overdueOnly').checked = false;
    document.getElementById('sortBy').value = 'created_at';
    document.getElementById('sortOrder').value = 'desc';
    loadRequests();
}

document.addEventListener('DOMContentLoaded', () => {
    loadSelectData();
    loadStats();
    loadRequests();

    document.getElementById('courseId')?.addEventListener('change', checkCourseSeats);
    document.getElementById('searchInput')?.addEventListener('keydown', e => {
        if (e.key === 'Enter') loadRequests();
    });
});
