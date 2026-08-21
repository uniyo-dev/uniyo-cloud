// ============================================
// UNIYO LMS - ADVANCED THEME MANAGER v2
// Features: No flicker, instant, persistent, smooth
// ============================================

const ThemeManager = {
    // Get correct key based on page type
    getKey() {
        return window.location.pathname.includes('/admin') 
            ? 'uniyo_admin_theme' 
            : 'uniyo_dark_mode';
    },
    
    // Get current theme
    getTheme() {
        return localStorage.getItem(this.getKey()) || 'dark';
    },
    
    // Apply theme instantly (no flicker)
    apply(theme, instant = false) {
        const body = document.body;
        const html = document.documentElement;
        
        if (theme === 'light') {
            body.classList.add('light-mode');
            html.style.colorScheme = 'light';
            html.style.backgroundColor = '#F8FAFC';
        } else {
            body.classList.remove('light-mode');
            html.style.colorScheme = 'dark';
            html.style.backgroundColor = '#0B0F19';
        }
        
        // Update all toggle buttons on page
        this.updateButtons(theme);
        
        // Save preference
        localStorage.setItem(this.getKey(), theme);
    },
    
    // Toggle between themes
    toggle() {
        const current = this.getTheme();
        const next = current === 'light' ? 'dark' : 'light';
        this.apply(next);
        return next;
    },
    
    // Update button text/icons
    updateButtons(theme) {
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            if (theme === 'light') {
                btn.textContent = '☀️ Light';
                btn.classList.add('active-light');
            } else {
                btn.textContent = '🌙 Dark';
                btn.classList.remove('active-light');
            }
        });
    },
    
    // Initialize on page load
    init() {
        const theme = this.getTheme();
        
        // Apply BEFORE page renders (no flicker)
        this.apply(theme, true);
        
        // Set up toggle buttons
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggle();
                });
            });
            this.updateButtons(theme);
        });
        
        // Listen for storage changes (sync across tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === this.getKey()) {
                this.apply(e.newValue || 'dark', true);
            }
        });
    }
};

// Run immediately - before page renders
ThemeManager.init();
