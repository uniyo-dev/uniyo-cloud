// ============================================
// UNIYO LMS - Global JavaScript Utilities
// ============================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = 'padding:12px 20px;border-radius:8px;font-weight:600;animation:slideDown 0.3s ease;';
    
    if (type === 'success') toast.style.background = '#14B8A6';
    if (type === 'danger') toast.style.background = '#EC4899';
    if (type === 'warning') toast.style.background = '#F59E0B';
    if (type === 'info') toast.style.background = '#38BDF8';
    toast.style.color = type === 'warning' || type === 'info' ? '#0B0F19' : 'white';
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function checkServerHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy') {
                console.log('✓ Server connected');
            } else {
                showToast('Connection issues detected', 'warning');
            }
        })
        .catch(() => {
            console.log('Offline mode');
        });
}

document.addEventListener('DOMContentLoaded', function() {
    checkServerHealth();
    
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// ============================================
// DYNAMIC SVG THEME SWITCHING
// ============================================

function updateSvgTheme(isLightMode) {
    const allSvgs = document.querySelectorAll('svg');
    
    allSvgs.forEach(svg => {
        // Change rect backgrounds
        svg.querySelectorAll('rect[fill="#111827"]').forEach(rect => {
            rect.setAttribute('fill', isLightMode ? '#FFFFFF' : '#111827');
        });
        
        svg.querySelectorAll('rect[fill="#1a2332"]').forEach(rect => {
            rect.setAttribute('fill', isLightMode ? '#F1F5F9' : '#1a2332');
        });
        
        // Change text colors
        svg.querySelectorAll('text[fill="#f8fafc"], text[fill="#F8FAFC"]').forEach(text => {
            text.setAttribute('fill', isLightMode ? '#0B0F19' : '#f8fafc');
        });
        
        svg.querySelectorAll('text[fill="#94a3b8"]').forEach(text => {
            text.setAttribute('fill', isLightMode ? '#475569' : '#94a3b8');
        });
        
        // Change lines that are dark
        svg.querySelectorAll('line[stroke="#1a2332"]').forEach(line => {
            line.setAttribute('stroke', isLightMode ? '#CBD5E1' : '#1a2332');
        });
        
        // Change circles with dark fill
        svg.querySelectorAll('circle[fill="#0B0F19"]').forEach(circle => {
            circle.setAttribute('fill', isLightMode ? '#F8FAFC' : '#0B0F19');
        });
    });
}

// Listen for theme changes
document.addEventListener('DOMContentLoaded', function() {
    // Check current theme
    const savedDarkMode = localStorage.getItem('uniyo_dark_mode');
    const isLightMode = savedDarkMode === 'false';
    
    // Update SVG theme after page loads
    setTimeout(() => updateSvgTheme(isLightMode), 500);
    
    // Listen for theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const isLight = document.body.classList.contains('light-mode');
                updateSvgTheme(isLight);
            }
        });
    });
    
    observer.observe(document.body, { attributes: true });
});
