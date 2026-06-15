const API_URL = (window.location.port === '5500' || window.location.port === '3000')
    ? 'http://localhost:8000'
    : '';

function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
}

function getCurrentUser() {
    return JSON.parse(localStorage.getItem('user') || '{}');
}

function isAdmin() {
    return getCurrentUser().role === 'admin';
}

function canManageCourses() {
    return getCurrentUser().role === 'admin';
}

function canDeleteRequests() {
    const role = getCurrentUser().role;
    return role === 'admin' || role === 'senior_manager';
}

function checkAuth() {
    const token = getToken();
    const isLoginPage = window.location.pathname.includes('login.html');
    if (!token && !isLoginPage) {
        window.location.href = 'login.html';
        return false;
    }
    if (token && isLoginPage) {
        window.location.href = 'requests.html';
        return false;
    }
    return true;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function parseErrorDetail(error) {
    if (!error) return 'ошибка запроса';
    if (typeof error.detail === 'string') return error.detail;
    if (Array.isArray(error.detail)) {
        return error.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
    }
    return JSON.stringify(error);
}

async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const response = await fetch(`${API_URL}${endpoint}`, config);

    if (response.status === 401) {
        removeToken();
        window.location.href = 'login.html';
        throw new Error('сессия истекла, войдите снова');
    }

    if (response.status === 204) return null;

    if (!response.ok) {
        let error;
        try { error = await response.json(); } catch { error = { detail: response.statusText }; }
        throw new Error(parseErrorDetail(error));
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
        return response.json();
    }
    return response;
}

async function apiDownload(endpoint, filename) {
    const token = getToken();
    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
    if (!response.ok) throw new Error('ошибка загрузки файла');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function formatDate(dateString) {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleDateString('ru-RU');
}

function formatDateTime(dateString) {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString('ru-RU');
}

function showNotification(message, isError = false) {
    document.querySelectorAll('.toast-notification').forEach(t => t.remove());
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position:fixed; bottom:24px; right:24px; z-index:9999;
        background:${isError ? '#DC2626' : '#FF6B00'}; color:white;
        padding:14px 28px; border-radius:16px; font-weight:600;
        box-shadow:0 8px 24px rgba(0,0,0,0.15);
        animation:fadeIn 0.3s ease-out; max-width:400px;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

function showLoading(show = true) {
    let el = document.getElementById('globalLoader');
    if (show) {
        if (!el) {
            el = document.createElement('div');
            el.id = 'globalLoader';
            el.className = 'global-loader';
            el.innerHTML = '<div class="loader-spinner"></div>';
            document.body.appendChild(el);
        }
        el.style.display = 'flex';
    } else if (el) {
        el.style.display = 'none';
    }
}

function logout() {
    removeToken();
    window.location.href = 'login.html';
}

function initAppHeader() {
    const user = getCurrentUser();
    const roleMap = {
        admin: 'администратор',
        senior_manager: 'ст. менеджер',
        manager: 'менеджер',
    };

    const userNameSpan = document.getElementById('userName');
    const userRoleSpan = document.getElementById('userRole');
    if (userNameSpan) userNameSpan.textContent = user.full_name || 'пользователь';
    if (userRoleSpan) userRoleSpan.textContent = roleMap[user.role] || user.role;

    document.querySelectorAll('#usersNav, #usersNavLink, #importNav').forEach(el => {
        if (el) el.style.display = isAdmin() ? '' : 'none';
    });

    const todaySpan = document.getElementById('todayDate');
    if (todaySpan) {
        todaySpan.textContent = new Date().toLocaleDateString('ru-RU', {
            weekday: 'long', day: 'numeric', month: 'long',
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (checkAuth() && !window.location.pathname.includes('login.html')) {
        initAppHeader();
    }
});
