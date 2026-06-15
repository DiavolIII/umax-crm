async function loadCourses() {
    const isAdmin = canManageCourses();
    const createBtn = document.getElementById('createCourseBtn');
    if (createBtn) createBtn.style.display = isAdmin ? '' : 'none';

    try {
        const courses = await apiRequest('/courses/?limit=200');
        const container = document.getElementById('coursesGrid');
        container.innerHTML = courses.map(c => `
            <div class="course-card">
                <h3>${c.name}</h3>
                <div class="course-info">
                    <span class="course-badge">${c.subject}</span>
                    <span class="course-badge">${c.exam_type}</span>
                    <span class="course-badge">${c.grade} класс</span>
                    <span class="course-badge">${c.format}</span>
                </div>
                <div class="course-price">${c.price.toLocaleString()} ₽</div>
                <div>свободных мест: ${c.free_seats}</div>
                ${c.free_seats === 0 ? '<div class="seats-warning">⚠️ мест нет</div>' : c.free_seats <= 3 ? '<div class="seats-warning">⚠️ осталось мало мест</div>' : ''}
                ${c.start_date ? `<div style="font-size:12px; color:#9CA3AF; margin-top:8px">старт: ${formatDate(c.start_date)}</div>` : ''}
                ${isAdmin ? `<div style="margin-top:16px; display:flex; gap:8px; justify-content:flex-end">
                    <button class="action-btn" onclick="openCourseModal(${c.id})">✏️</button>
                    <button class="action-btn delete" onclick="deleteCourse(${c.id})">🗑️</button>
                </div>` : ''}
            </div>
        `).join('');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function openCourseModal(id = null) {
    document.getElementById('courseModalTitle').textContent = id ? 'редактировать курс' : 'новый курс';
    document.getElementById('courseEditId').value = id || '';
    if (id) {
        try {
            const course = await apiRequest(`/courses/${id}`);
            document.getElementById('courseName').value = course.name;
            document.getElementById('courseSubject').value = course.subject;
            document.getElementById('courseExamType').value = course.exam_type;
            document.getElementById('courseGrade').value = course.grade;
            document.getElementById('courseFormat').value = course.format;
            document.getElementById('coursePrice').value = course.price;
            document.getElementById('courseFreeSeats').value = course.free_seats;
            document.getElementById('courseStartDate').value = course.start_date || '';
        } catch (err) {
            showNotification(err.message, true);
            return;
        }
    } else {
        document.getElementById('courseName').value = '';
        document.getElementById('courseSubject').value = '';
        document.getElementById('courseExamType').value = 'ОГЭ';
        document.getElementById('courseGrade').value = '9';
        document.getElementById('courseFormat').value = 'Онлайн';
        document.getElementById('coursePrice').value = '0';
        document.getElementById('courseFreeSeats').value = '0';
        document.getElementById('courseStartDate').value = '';
    }
    document.getElementById('courseModal').classList.add('active');
}

async function saveCourse() {
    const id = document.getElementById('courseEditId').value;
    const data = {
        name: document.getElementById('courseName').value,
        subject: document.getElementById('courseSubject').value,
        exam_type: document.getElementById('courseExamType').value,
        grade: parseInt(document.getElementById('courseGrade').value),
        format: document.getElementById('courseFormat').value,
        price: parseInt(document.getElementById('coursePrice').value),
        free_seats: parseInt(document.getElementById('courseFreeSeats').value),
        start_date: document.getElementById('courseStartDate').value || null,
        is_active: true
    };
    
    if (!data.name || !data.subject || !data.grade) {
        showNotification('заполните обязательные поля', true);
        return;
    }
    
    try {
        if (id) {
            await apiRequest(`/courses/${id}`, 'PUT', data);
        } else {
            await apiRequest('/courses/', 'POST', data);
        }
        closeCourseModal();
        loadCourses();
        showNotification('курс сохранен');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function deleteCourse(id) {
    if (!confirm('удалить курс?')) return;
    try {
        await apiRequest(`/courses/${id}`, 'DELETE');
        loadCourses();
        showNotification('курс удален');
    } catch (err) {
        showNotification(err.message, true);
    }
}

function closeCourseModal() {
    document.getElementById('courseModal').classList.remove('active');
}

document.addEventListener('DOMContentLoaded', loadCourses);