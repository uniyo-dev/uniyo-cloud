// ============================================
// UNIYO LMS - MASTER THEME MANAGER
// EQUAL TOGGLE: Dark and Light have equal priority
// ============================================

function applyMasterTheme(mode) {
    const body = document.body;
    const html = document.documentElement;
    
    if (mode === 'light') {
        body.classList.add('light-mode');
        html.style.colorScheme = 'light';
        
        (function() {
            // Apply light mode to all elements
            document.querySelectorAll('.course-card, .question-card, .vip-question-card, .lesson-content, .admin-section, .admin-header, .settings-section, .payment-container, .dashboard-header, .worksheet-header, .progress-tracker, .self-check-section, .chapter-nav, .stat-card, .announcement-card, .auth-card, .notification-item, .leaderboard-entry, .worksheet-link-section, .vip-progress-section, .payment-card, .payment-method-card, .past-vip-card, .upcoming-vip-card, .active-vip-card, .highlight-box, .cheat-notes, .example-box, .definition-box, .self-check-question').forEach(el => {
                el.style.backgroundColor = '#FFFFFF';
                el.style.borderColor = '#E2E8F0';
                el.style.color = '#334155';
            });
            
            document.querySelectorAll('h1, h2, h3, h4, .course-title, .lesson-meta h1, .question-number, .vip-question-number').forEach(el => {
                el.style.color = '#0B0F19';
            });
            
            document.querySelectorAll('p, .lesson-body, .question-text, .vip-question-text, .course-details, .worksheet-meta, .text-muted, .leaderboard-info small, .highlight-box, .cheat-notes, .cheat-notes li, .example-box, .definition-box').forEach(el => {
                el.style.color = '#334155';
            });
            
            // Highlight box strong tags
            document.querySelectorAll('.highlight-box strong, .definition-box strong').forEach(el => {
                el.style.color = '#6D28D9';
            });
            
            document.querySelectorAll('.cheat-notes h4').forEach(el => {
                el.style.color = '#D97706';
            });
            
            document.querySelectorAll('input, select, textarea').forEach(el => {
                el.style.backgroundColor = '#F8FAFC';
                el.style.borderColor = '#CBD5E1';
                el.style.color = '#0B0F19';
            });
            
            document.querySelectorAll('.option-btn, .vip-option-btn, .part-btn').forEach(el => {
                el.style.backgroundColor = '#F8FAFC';
                el.style.color = '#0B0F19';
                el.style.borderColor = '#CBD5E1';
            });
            
            document.querySelectorAll('.admin-table th, .content-table th, .table-container th').forEach(el => {
                el.style.backgroundColor = '#F1F5F9';
                el.style.color = '#0B0F19';
            });
            
            document.querySelectorAll('.admin-table td, .content-table td, .table-container td').forEach(el => {
                el.style.color = '#334155';
            });
            
            // SVG diagrams
            document.querySelectorAll('svg rect[fill="#111827"]').forEach(el => {
                el.setAttribute('fill', '#FFFFFF');
            });
            document.querySelectorAll('svg rect[fill="#1a2332"]').forEach(el => {
                el.setAttribute('fill', '#F1F5F9');
            });
            document.querySelectorAll('svg text[fill="#f8fafc"], svg text[fill="#F8FAFC"]').forEach(el => {
                el.setAttribute('fill', '#0B0F19');
            });
            document.querySelectorAll('svg text[fill="#94a3b8"]').forEach(el => {
                el.setAttribute('fill', '#475569');
            });
        })();
        
    } else {
        // DARK MODE
        body.classList.remove('light-mode');
        html.style.colorScheme = 'dark';
        
        (function() {
            // Remove inline styles to let CSS dark mode work
            document.querySelectorAll('[style*="background-color: #FFFFFF"]').forEach(el => {
                el.style.backgroundColor = '';
            });
            document.querySelectorAll('[style*="background-color: #F8FAFC"]').forEach(el => {
                el.style.backgroundColor = '';
            });
            document.querySelectorAll('[style*="background-color: #F1F5F9"]').forEach(el => {
                el.style.backgroundColor = '';
            });
            document.querySelectorAll('[style*="color: #0B0F19"]').forEach(el => {
                el.style.color = '';
            });
            document.querySelectorAll('[style*="color: #334155"]').forEach(el => {
                el.style.color = '';
            });
            document.querySelectorAll('[style*="color: #475569"]').forEach(el => {
                el.style.color = '';
            });
            document.querySelectorAll('[style*="border-color: #E2E8F0"]').forEach(el => {
                el.style.borderColor = '';
            });
            document.querySelectorAll('[style*="border-color: #CBD5E1"]').forEach(el => {
                el.style.borderColor = '';
            });
            
            // Reset SVG
            document.querySelectorAll('svg rect[fill="#FFFFFF"]').forEach(el => {
                el.setAttribute('fill', '#111827');
            });
            document.querySelectorAll('svg rect[fill="#F1F5F9"]').forEach(el => {
                el.setAttribute('fill', '#1a2332');
            });
            document.querySelectorAll('svg text[fill="#0B0F19"]').forEach(el => {
                el.setAttribute('fill', '#f8fafc');
            });
            document.querySelectorAll('svg text[fill="#475569"]').forEach(el => {
                el.setAttribute('fill', '#94a3b8');
            });
        })();
    }
}

// Initialize based on SAVED preference only
(function() {
    const savedDarkMode = localStorage.getItem('uniyo_dark_mode');
    
    if (savedDarkMode === 'false') {
        applyMasterTheme('light');
    } else if (savedDarkMode === 'true') {
        applyMasterTheme('dark');
    }
    // If null (first visit), do nothing - CSS defaults apply
})();

window.applyMasterTheme = applyMasterTheme;
