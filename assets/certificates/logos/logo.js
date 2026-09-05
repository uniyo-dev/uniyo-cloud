/* ============================================
   UNIYO LOGO — Complete Interactive Features
   ============================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c UNIYO LOGO SYSTEM ', 'background: #6D28D9; color: #FCD34D; font-size: 24px; font-weight: bold; padding: 15px 30px; border-radius: 8px;');
    console.log('%c University Made for YOU ', 'color: #14B8A6; font-size: 14px;');
    
    initLogoInteractions();
    initModeToggle();
    initWordmarkAnimation();
    initKeyboardShortcuts();
});

/* ============================================
   1. LOGO INTERACTIONS
   ============================================ */
function initLogoInteractions() {
    const logoContainer = document.getElementById('uniyoLogo');
    const logoIcon = document.getElementById('logoIcon');
    
    if (!logoContainer) return;
    
    // Click - Celebration
    logoContainer.addEventListener('click', (event) => {
        triggerCelebration(event);
    });
    
    // Double click - Rotate
    logoContainer.addEventListener('dblclick', () => {
        if (logoIcon) {
            logoIcon.style.transform = 'rotate(360deg)';
            logoIcon.style.transition = 'transform 1s ease';
            setTimeout(() => {
                logoIcon.style.transform = '';
            }, 1000);
        }
    });
    
    // Hover - Tilt effect
    logoContainer.addEventListener('mousemove', (event) => {
        const rect = logoContainer.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        
        logoContainer.style.transform = `perspective(800px) rotateX(${-y * 5}deg) rotateY(${x * 5}deg)`;
    });
    
    logoContainer.addEventListener('mouseleave', () => {
        logoContainer.style.transform = '';
    });
}

/* ============================================
   2. MODE TOGGLE
   ============================================ */
function initModeToggle() {
    const toggle = document.getElementById('modeToggle');
    if (!toggle) return;
    
    toggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        
        const isDark = document.body.classList.contains('dark-mode');
        toggle.textContent = isDark ? '☀' : '◐';
        
        showToast(isDark ? 'Dark Mode Activated' : 'Light Mode Activated');
    });
}

/* ============================================
   3. WORDMARK ANIMATION
   ============================================ */
function initWordmarkAnimation() {
    const letters = document.querySelectorAll('.uniyo-letter');
    
    letters.forEach((letter, index) => {
        letter.style.animation = `letterFloat 3s ease-in-out ${index * 0.15}s infinite`;
    });
    
    // Add animation to document
    if (!document.getElementById('wordmark-style')) {
        const style = document.createElement('style');
        style.id = 'wordmark-style';
        style.textContent = `
            @keyframes letterFloat {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   4. CELEBRATION
   ============================================ */
function triggerCelebration(event) {
    const logoContainer = document.getElementById('uniyoLogo');
    if (!logoContainer) return;
    
    const rect = logoContainer.getBoundingClientRect();
    const x = event.clientX || rect.left + rect.width / 2;
    const y = event.clientY || rect.top + rect.height / 2;
    
    createParticles(x, y, 30);
    showToast('UNIYO — University Made for YOU! 🎓');
}

function createParticles(x, y, count) {
    const colors = ['#6D28D9', '#7C3AED', '#F59E0B', '#FCD34D', '#14B8A6', '#2DD4BF'];
    
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        const angle = (Math.PI * 2 * i) / count;
        const velocity = Math.random() * 80 + 30;
        const size = Math.random() * 6 + 2;
        
        particle.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            animation: particleBurst 0.8s ease-out;
            --vx: ${Math.cos(angle) * velocity}px;
            --vy: ${Math.sin(angle) * velocity}px;
        `;
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 800);
    }
    
    if (!document.getElementById('particle-style')) {
        const style = document.createElement('style');
        style.id = 'particle-style';
        style.textContent = `
            @keyframes particleBurst {
                from { transform: translate(0, 0) scale(1); opacity: 1; }
                to { transform: translate(var(--vx), var(--vy)) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   5. KEYBOARD SHORTCUTS
   ============================================ */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        if (event.key === 'd' || event.key === 'D') {
            document.body.classList.toggle('dark-mode');
        }
        if (event.key === '?' ) {
            showToast('Shortcuts: D = Dark Mode, Click = Celebrate');
        }
    });
}

/* ============================================
   6. TOAST NOTIFICATIONS
   ============================================ */
function showToast(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: #6D28D9;
        color: white;
        padding: 12px 24px;
        border-radius: 25px;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 8px 25px rgba(109, 40, 217, 0.4);
        z-index: 10000;
        animation: toastIn 0.3s ease;
        pointer-events: none;
    `;
    
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
    
    if (!document.getElementById('toast-style')) {
        const style = document.createElement('style');
        style.id = 'toast-style';
        style.textContent = `
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
}
