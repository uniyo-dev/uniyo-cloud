// ============================================
// UNIYO LMS - Admin Theme Toggle
// ============================================

function toggleAdminTheme() {
    var body = document.body;
    var btn = document.getElementById('adminThemeBtn');
    
    if (body.classList.contains('light-mode')) {
        // Switch to DARK
        body.classList.remove('light-mode');
        body.style.backgroundColor = '#0B0F19';
        body.style.color = '#F8FAFC';
        localStorage.setItem('uniyo_admin_dark_mode', 'true');
        if (btn) btn.textContent = '🌙 Dark';
    } else {
        // Switch to LIGHT
        body.classList.add('light-mode');
        body.style.backgroundColor = '#F8FAFC';
        body.style.color = '#0B0F19';
        localStorage.setItem('uniyo_admin_dark_mode', 'false');
        if (btn) btn.textContent = '☀️ Light';
    }
}

(function() {
    var savedMode = localStorage.getItem('uniyo_admin_dark_mode');
    var btn = document.getElementById('adminThemeBtn');
    
    if (savedMode === 'false') {
        document.body.classList.add('light-mode');
        if (btn) btn.textContent = '☀️ Light';
    } else {
        if (btn) btn.textContent = '🌙 Dark';
    }
})();
