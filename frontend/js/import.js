let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!isAdmin()) {
        document.body.innerHTML = '<div class="access-denied"><h2>доступ запрещён</h2><p>импорт доступен только администратору</p><a href="requests.html">← к заявкам</a></div>';
        return;
    }

    const input = document.getElementById('fileInput');
    const zone = document.getElementById('uploadZone');

    input.addEventListener('change', () => handleFile(input.files[0]));
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        handleFile(e.dataTransfer.files[0]);
    });
});

function handleFile(file) {
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['xlsx', 'xls', 'csv'].includes(ext)) {
        showNotification('поддерживаются только .xlsx, .xls, .csv', true);
        return;
    }
    selectedFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('importBtn').disabled = false;
}

async function uploadFile() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    showLoading(true);
    document.getElementById('importBtn').disabled = true;

    try {
        const token = getToken();
        const response = await fetch(`${API_URL}/import/excel`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData,
        });

        const data = await response.json();
        if (!response.ok) throw new Error(parseErrorDetail(data));

        const result = document.getElementById('importResult');
        result.style.display = 'block';
        result.className = 'import-result success';
        result.innerHTML = `
            <strong>✓ ${escapeHtml(data.message)}</strong>
            ${data.errors?.length ? `<details><summary>ошибки (${data.errors.length})</summary><ul>${data.errors.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul></details>` : ''}
        `;
        showNotification('импорт завершён');
    } catch (err) {
        showNotification(err.message, true);
    } finally {
        showLoading(false);
        document.getElementById('importBtn').disabled = false;
    }
}

async function downloadTemplate() {
    try {
        await apiDownload('/import/template/csv', 'umax_import_template.csv');
        showNotification('шаблон скачан');
    } catch (err) {
        showNotification(err.message, true);
    }
}
