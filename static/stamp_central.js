/* ============================================
   UNIYO STAMP CENTRAL — Interactive Features
   ============================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c UNIYO OFFICIAL STAMP ', 'background: #6D28D9; color: #FCD34D; font-size: 22px; font-weight: bold; padding: 12px 25px; border-radius: 8px;');
    console.log('%c Certificate Authority — Ethiopia ', 'color: #14B8A6; font-size: 13px;');
    
    initStampInteractions();
    initVerificationSystem();
    initStampAnimation();
});

/* ============================================
   1. STAMP INTERACTIONS
   ============================================ */
function initStampInteractions() {
    const stamp = document.getElementById('uniyoStamp');
    
    if (!stamp) return;
    
    // Click - Stamp Press Effect
    stamp.addEventListener('click', (event) => {
        triggerStampPress(event);
    });
    
    // Double click - Verification
    stamp.addEventListener('dblclick', () => {
        showVerificationDetails();
    });
    
    // Right click - Secret
    stamp.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        showStampSecret();
    });
    
    // Touch support
    stamp.addEventListener('touchstart', (event) => {
        event.preventDefault();
        triggerStampPress(event);
    }, { passive: false });
}

/* ============================================
   2. STAMP PRESS EFFECT
   ============================================ */
function triggerStampPress(event) {
    const stamp = document.getElementById('uniyoStamp');
    if (!stamp) return;
    
    // Press animation
    stamp.style.transform = 'scale(0.93) rotate(-2deg)';
    stamp.style.transition = 'transform 0.15s ease';
    
    setTimeout(() => {
        stamp.style.transform = 'scale(1) rotate(0deg)';
        stamp.style.transition = 'transform 0.4s ease';
    }, 150);
    
    // Ink splash
    createInkEffect(event);
    
    // Particle burst
    createStampParticles(event);
    
    showStampToast('✅ Stamp Applied!');
}

function createInkEffect(event) {
    const stamp = document.getElementById('uniyoStamp');
    if (!stamp) return;
    
    const rect = stamp.getBoundingClientRect();
    const x = (event.clientX || event.touches[0].clientX) - rect.left;
    const y = (event.clientY || event.touches[0].clientY) - rect.top;
    
    const ink = document.createElement('div');
    ink.style.cssText = `
        position: absolute;
        left: ${x}px;
        top: ${y}px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(109,40,217,0.6) 0%, rgba(109,40,217,0.2) 50%, transparent 70%);
        transform: translate(-50%, -50%) scale(0);
        animation: inkSpread 0.6s ease-out;
        pointer-events: none;
        z-index: 100;
    `;
    
    stamp.appendChild(ink);
    setTimeout(() => ink.remove(), 600);
    
    if (!document.getElementById('ink-style')) {
        const style = document.createElement('style');
        style.id = 'ink-style';
        style.textContent = `
            @keyframes inkSpread {
                to { transform: translate(-50%, -50%) scale(10); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

function createStampParticles(event) {
    const stamp = document.getElementById('uniyoStamp');
    if (!stamp) return;
    
    const rect = stamp.getBoundingClientRect();
    const x = event.clientX || rect.left + rect.width / 2;
    const y = event.clientY || rect.top + rect.height / 2;
    
    const colors = ['#6D28D9', '#7C3AED', '#F59E0B', '#FCD34D', '#FFFFFF'];
    
    for (let i = 0; i < 25; i++) {
        const particle = document.createElement('div');
        const angle = (Math.PI * 2 * i) / 25;
        const velocity = Math.random() * 60 + 20;
        const size = Math.random() * 5 + 2;
        
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
            animation: stampBurst 0.7s ease-out;
            --vx: ${Math.cos(angle) * velocity}px;
            --vy: ${Math.sin(angle) * velocity}px;
        `;
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 700);
    }
    
    if (!document.getElementById('stamp-particle-style')) {
        const style = document.createElement('style');
        style.id = 'stamp-particle-style';
        style.textContent = `
            @keyframes stampBurst {
                from { transform: translate(0, 0) scale(1); opacity: 1; }
                to { transform: translate(var(--vx), var(--vy)) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   3. VERIFICATION SYSTEM
   ============================================ */
function initVerificationSystem() {
    // Simulated verification on double-click
    console.log('%c Verification System Ready ', 'color: #14B8A6;');
}

function showVerificationDetails() {
    const details = `
╔══════════════════════════════════╗
║     UNIYO OFFICIAL STAMP         ║
╠══════════════════════════════════╣
║ Verification Code: UNY-2026-0001 ║
║ Platform: UNIYO                   ║
║ Authority: Ethiopian Higher Ed    ║
║ Status: ✅ AUTHENTIC              ║
║ Issue Date: September 2026        ║
╚══════════════════════════════════╝`;
    
    console.log(details);
    showStampToast('🔍 Verification Complete — Authentic!');
}

/* ============================================
   4. STAMP IDLE ANIMATION
   ============================================ */
function initStampAnimation() {
    const stamp = document.getElementById('uniyoStamp');
    if (!stamp) return;
    
    setInterval(() => {
        if (!stamp.matches(':hover')) {
            stamp.style.transform = 'scale(1.01)';
            stamp.style.transition = 'transform 1s ease';
            
            setTimeout(() => {
                stamp.style.transform = 'scale(1)';
                stamp.style.transition = 'transform 1s ease';
            }, 1000);
        }
    }, 6000);
}

/* ============================================
   5. TOAST NOTIFICATIONS
   ============================================ */
function showStampToast(message) {
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
    
    if (!document.getElementById('stamp-toast-style')) {
        const style = document.createElement('style');
        style.id = 'stamp-toast-style';
        style.textContent = `
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   6. SECRET MESSAGES
   ============================================ */
function showStampSecret() {
    const messages = [
        '📜 UNIYO — Certified Excellence!',
        '🔒 Trusted by Ethiopian Students!',
        '💜 University Made for YOU!',
        '✅ Authentic & Verified!',
        '🌟 The Gold Standard!'
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    showStampToast(randomMessage);
}