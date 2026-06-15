const API_URL = (window.location.port === '5500' || window.location.port === '3000')
    ? 'http://localhost:8000'
    : '';

async function doLogin(loginName, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login: loginName, password }),
    });

    if (!response.ok) {
        let error;
        try { error = await response.json(); } catch { error = { detail: 'ошибка входа' }; }
        let msg = error.detail;
        if (Array.isArray(msg)) msg = msg.map(e => e.msg || JSON.stringify(e)).join('; ');
        if (typeof msg !== 'string') msg = 'ошибка входа';
        throw new Error(msg);
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify({
        id: data.user_id,
        full_name: data.full_name,
        role: data.role,
    }));
    return data;
}

function togglePassword() {
    const input = document.getElementById('password');
    input.type = input.type === 'password' ? 'text' : 'password';
}

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const loginName = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');
    const btn = e.target.querySelector('.btn-login');
    errorDiv.textContent = '';
    btn.disabled = true;
    btn.textContent = 'вход...';

    try {
        await doLogin(loginName, password);
        window.location.href = 'requests.html';
    } catch (err) {
        errorDiv.textContent = err.message;
        btn.disabled = false;
        btn.textContent = 'войти в систему';
    }
});
