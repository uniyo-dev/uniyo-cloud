// ============================================
// UNIYO LMS - Settings JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Theme toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        // Set current theme state
        const currentTheme = ThemeManager.getTheme();
        darkModeToggle.checked = currentTheme === 'dark';
        
        // Listen for toggle change
        darkModeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            ThemeManager.apply(newTheme);
            showToast(newTheme === 'dark' ? 'Dark mode enabled' : 'Light mode enabled', 'success');
        });
    }
    
    // Font size
    const savedFontSize = localStorage.getItem('uniyo_font_size');
    if (savedFontSize) {
        applyFontSize(parseInt(savedFontSize));
    }
    
    // Language
    const savedLanguage = localStorage.getItem('uniyo_language');
    if (savedLanguage) {
        const langSelect = document.getElementById('languageSelect');
        if (langSelect) langSelect.value = savedLanguage;
    }
});

let currentFontSize = 16;

function changeFontSize(direction) {
    currentFontSize += direction;
    if (currentFontSize < 12) currentFontSize = 12;
    if (currentFontSize > 24) currentFontSize = 24;
    applyFontSize(currentFontSize);
}

function applyFontSize(size) {
    currentFontSize = size;
    document.documentElement.style.fontSize = size + 'px';
    const fontSizeValue = document.getElementById('fontSizeValue');
    if (fontSizeValue) fontSizeValue.textContent = size + 'px';
    localStorage.setItem('uniyo_font_size', size);
}

function changeLanguage(language) {
    localStorage.setItem('uniyo_language', language);
    
    const messages = {
        'en': 'Language changed to English',
        'am': 'ቋንቋ ወደ አማርኛ ተቀይሯል',
        'om': 'Afaan Oromootti jijjiirame'
    };
    
    showToast(messages[language] || 'Language changed', 'success');
}

function viewOfflineStorage() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
        navigator.storage.estimate().then(estimate => {
            const usedMB = (estimate.usage / 1024 / 1024).toFixed(2);
            showToast(`Storage: ${usedMB}MB used`, 'info');
        });
    } else {
        showToast('Storage info not available', 'info');
    }
}

function clearOfflineData() {
    const confirmClear = confirm('Clear all offline data?');
    if (confirmClear) {
        if ('indexedDB' in window) {
            indexedDB.deleteDatabase('UNIYO_OFFLINE_DB');
        }
        localStorage.clear();
        showToast('Offline data cleared', 'success');
    }
}
