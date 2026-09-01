/* ============================================
   UNIYO APP ICON — Interactive Features
   ============================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c UNIYO APP ICON ', 'background: #6D28D9; color: #FCD34D; font-size: 22px; font-weight: bold; padding: 12px 25px; border-radius: 8px;');
    console.log('%c University Made for YOU ', 'color: #14B8A6; font-size: 13px;');
    
    initIconInteractions();
    initPulseAnimation();
    initKeyboardShortcuts();
});

/* ============================================
   1. ICON INTERACTIONS
   ============================================ */
function initIconInteractions() {
    const appIcon = document.getElementById('appIcon');
    
    if (!appIcon) return;
    
    // Click - Celebration
    appIcon.addEventListener('click', (event) => {
        triggerIconCelebration(event);
        animateIconClick();
    });
    
    // Double click - Rotate
    appIcon.addEventListener('dblclick', () => {
        appIcon.style.transform = 'rotate(360deg) scale(1.1)';
        appIcon.style.transition = 'transform 1s ease';
        setTimeout(() => {
            appIcon.style.transform = '';
        }, 1000);
    });
    
    // Touch support
    appIcon.addEventListener('touchstart', (event) => {
        event.preventDefault();
        triggerIconCelebration(event);
    }, { passive: false });
}

/* ============================================
   2. ICON CLICK ANIMATION
   ============================================ */
function animateIconClick() {
    const appIcon = document.getElementById('appIcon');
    if (!appIcon) return;
    
    appIcon.style.transform = 'scale(0.92)';
    appIcon.style.transition = 'transform 0.15s ease';
    
    setTimeout(() => {
        appIcon.style.transform = 'scale(1)';
        appIcon.style.transition = 'transform 0.4s ease';
    }, 150);
}

/* ============================================
   3. GENTLE PULSE ANIMATION
   ============================================ */
function initPulseAnimation() {
    const appIcon = document.getElementById('appIcon');
    if (!appIcon) return;
    
    // Subtle breathing effect
    setInterval(() => {
        if (!appIcon.matches(':hover')) {
            appIcon.style.transform = 'scale(1.02)';
            appIcon.style.transition = 'transform 1s ease';
            
            setTimeout(() => {
                appIcon.style.transform = 'scale(1)';
                appIcon.style.transition = 'transform 1s ease';
            }, 1000);
        }
    }, 5000);
}

/* ============================================
   4. CELEBRATION PARTICLES
   ============================================ */
function triggerIconCelebration(event) {
    const appIcon = document.getElementById('appIcon');
    if (!appIcon) return;
    
    const rect = appIcon.getBoundingClientRect();
    const x = event.clientX || rect.left + rect.width / 2;
    const y = event.clientY || rect.top + rect.height / 2;
    
    createIconParticles(x, y, 40);
    showIconToast('UNIYO App! 🎓✨');
}

function createIconParticles(x, y, count) {
    const colors = ['#6D28D9', '#7C3AED', '#F59E0B', '#FCD34D', '#14B8A6', '#2DD4BF', '#FFFFFF'];
    
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        const angle = (Math.PI * 2 * i) / count;
        const velocity = Math.random() * 100 + 40;
        const size = Math.random() * 7 + 3;
        
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
            animation: iconBurst 1s ease-out;
            --vx: ${Math.cos(angle) * velocity}px;
            --vy: ${Math.sin(angle) * velocity}px;
            box-shadow: 0 0 10px ${colors[Math.floor(Math.random() * colors.length)]};
        `;
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 1000);
    }
    
    if (!document.getElementById('icon-particle-style')) {
        const style = document.createElement('style');
        style.id = 'icon-particle-style';
        style.textContent = `
            @keyframes iconBurst {
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
        switch(event.key.toLowerCase()) {
            case 'p':
                const appIcon = document.getElementById('appIcon');
                if (appIcon) {
                    appIcon.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        appIcon.style.transform = 'scale(1)';
                    }, 300);
                }
                break;
            case '?':
                showIconToast('Press P to Pulse, Click to Celebrate');
                break;
        }
    });
}

/* ============================================
   6. TOAST NOTIFICATIONS
   ============================================ */
function showIconToast(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #6D28D9 0%, #F59E0B 100%);
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
    
    if (!document.getElementById('icon-toast-style')) {
        const style = document.createElement('style');
        style.id = 'icon-toast-style';
        style.textContent = `
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
}