let currentUserRole = null;

async function loadUsers() {
    try {
        const users = await apiRequest('/users/');
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.full_name}</td>
                <td>${u.login}</td>
                <td><span class="status-badge" style="background:rgba(255,107,0,0.12); color:#E65100">${u.role_name || '—'}</span></td>
                <td><span style="color:${u.is_active ? '#10b981' : '#f5576c'}">${u.is_active ? 'активен' : 'заблокирован'}</span></td>
                <td class="action-buttons">
                    <button class="action-btn" onclick="openUserModal(${u.id})">✏️</button>
                    <button class="action-btn delete" onclick="deleteUser(${u.id})">🗑️</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function loadRoles() {
    try {
        const roles = await apiRequest('/users/roles/list');
        const select = document.getElementById('userRoleId');
        select.innerHTML = roles.map(r => `<option value="${r.id}">${r.name === 'admin' ? 'администратор' : r.name === 'senior_manager' ? 'старший менеджер' : 'менеджер'}</option>`).join('');
    } catch (err) {
        console.error(err);
    }
}

async function openUserModal(id = null) {
    document.getElementById('userModalTitle').textContent = id ? 'редактировать пользователя' : 'новый пользователь';
    document.getElementById('userEditId').value = id || '';
    await loadRoles();
    
    if (id) {
        try {
            const user = await apiRequest(`/users/${id}`);
            document.getElementById('userFullName').value = user.full_name;
            document.getElementById('userLogin').value = user.login;
            document.getElementById('userPassword').value = '';
            document.getElementById('userRoleId').value = user.role_id;
            document.getElementById('userIsActive').checked = user.is_active;
        } catch (err) {
            showNotification(err.message, true);
            return;
        }
    } else {
        document.getElementById('userFullName').value = '';
        document.getElementById('userLogin').value = '';
        document.getElementById('userPassword').value = '';
        document.getElementById('userIsActive').checked = true;
    }
    document.getElementById('userModal').classList.add('active');
}

async function saveUser() {
    const id = document.getElementById('userEditId').value;
    const data = {
        full_name: document.getElementById('userFullName').value,
        login: document.getElementById('userLogin').value,
        role_id: parseInt(document.getElementById('userRoleId').value),
        is_active: document.getElementById('userIsActive').checked
    };
    
    const password = document.getElementById('userPassword').value;
    if (password) data.password = password;
    
    if (!data.full_name || !data.login) {
        showNotification('заполните обязательные поля', true);
        return;
    }
    
    try {
        if (id) {
            await apiRequest(`/users/${id}`, 'PUT', data);
        } else {
            if (!password) {
                showNotification('укажите пароль для нового пользователя', true);
                return;
            }
            await apiRequest('/users/', 'POST', data);
        }
        closeUserModal();
        loadUsers();
        showNotification('пользователь сохранен');
    } catch (err) {
        showNotification(err.message, true);
    }
}

async function deleteUser(id) {
    if (!confirm('удалить пользователя?')) return;
    try {
        await apiRequest(`/users/${id}`, 'DELETE');
        loadUsers();
        showNotification('пользователь удален');
    } catch (err) {
        showNotification(err.message, true);
    }
}

function closeUserModal() {
    document.getElementById('userModal').classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.role !== 'admin') {
        document.body.innerHTML = '<div style="text-align:center; padding:50px"><h2>доступ запрещен</h2><a href="requests.html">вернуться к заявкам</a></div>';
        return;
    }
    loadUsers();
});