function toggleAdminTheme() {
    var body = document.body;
    var btn = document.getElementById('adminThemeBtn');
    const key = 'uniyo_admin_theme';
    const current = localStorage.getItem(key) || 'dark';
    const newTheme = current === 'light' ? 'dark' : 'light';
    
    localStorage.setItem(key, newTheme);
    
    if (newTheme === 'light') {
        body.classList.add('light-mode');
        if (btn) btn.textContent = '☀️ Light';
    } else {
        body.classList.remove('light-mode');
        if (btn) btn.textContent = '🌙 Dark';
    }
}
