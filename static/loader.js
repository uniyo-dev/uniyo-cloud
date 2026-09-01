/* ============================================
   UNIYO LOADER — Complete Loading Logic
   With Letters N, I, Y, O Animation
   ============================================ */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c UNIYO LOADER ', 'background: #6D28D9; color: #FCD34D; font-size: 22px; font-weight: bold; padding: 12px 25px; border-radius: 8px;');
    console.log('%c U • N • I • Y • O — All Letters Active ', 'color: #14B8A6; font-size: 13px;');
    
    startLoading();
    initLetterInteractions();
});

/* ============================================
   1. START LOADING
   ============================================ */
function startLoading() {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const statusText = document.getElementById('statusText');
    
    if (!progressFill || !progressPercentage) return;
    
    let progress = 0;
    const targetProgress = 100;
    const duration = 3000;
    const interval = 30;
    const increment = (targetProgress / duration) * interval;
    
    const progressInterval = setInterval(() => {
        progress += increment;
        
        if (progress >= targetProgress) {
            progress = targetProgress;
            clearInterval(progressInterval);
            setTimeout(() => showSuccess(), 500);
        }
        
        progressFill.style.width = progress + '%';
        progressPercentage.textContent = Math.floor(progress) + '%';
        
        // Status updates with letter references
        if (progress < 20) statusText.textContent = 'Loading U...';
        else if (progress < 40) statusText.textContent = 'Loading N...';
        else if (progress < 60) statusText.textContent = 'Loading I...';
        else if (progress < 80) statusText.textContent = 'Loading Y...';
        else statusText.textContent = 'Loading O...';
        
        // Activate letters based on progress
        activateLetters(progress);
        
        // Milestone effects
        if (Math.floor(progress) % 20 === 0 && progress > 0 && progress < 100) {
            triggerMilestone(progress);
        }
        
    }, interval);
}

/* ============================================
   2. ACTIVATE LETTERS BASED ON PROGRESS
   ============================================ */
function activateLetters(progress) {
    const letterN = document.querySelector('.letter-n');
    const letterI = document.querySelector('.letter-i');
    const letterY = document.querySelector('.letter-y');
    const letterO = document.querySelector('.letter-o-text');
    
    // Letter N activates at 20%
    if (letterN) {
        letterN.style.opacity = progress >= 20 ? '1' : '0.3';
        letterN.style.transform = progress >= 20 ? 'translateX(-50%) scale(1.3)' : 'translateX(-50%) scale(1)';
    }
    
    // Letter I activates at 40%
    if (letterI) {
        letterI.style.opacity = progress >= 40 ? '1' : '0.3';
        letterI.style.transform = progress >= 40 ? 'translateX(-50%) scale(1.3)' : 'translateX(-50%) scale(1)';
    }
    
    // Letter Y activates at 60%
    if (letterY) {
        letterY.style.opacity = progress >= 60 ? '1' : '0.3';
        letterY.style.transform = progress >= 60 ? 'translateY(-50%) scale(1.3)' : 'translateY(-50%) scale(1)';
    }
    
    // Letter O activates at 80%
    if (letterO) {
        letterO.style.opacity = progress >= 80 ? '1' : '0.3';
    }
}

/* ============================================
   3. LETTER INTERACTIONS
   ============================================ */
function initLetterInteractions() {
    const letters = document.querySelectorAll('.ring-letter, .letter-o-text');
    
    letters.forEach(letter => {
        letter.addEventListener('click', () => {
            const text = letter.textContent;
            console.log(`%c Letter ${text} clicked! `, 'background: #6D28D9; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;');
            
            // Pulse the letter
            letter.style.transform = 'scale(1.5)';
            letter.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                letter.style.transform = '';
                letter.style.transition = 'transform 0.5s ease';
            }, 300);
            
            showLoaderToast(`Letter ${text} activated!`);
        });
    });
}

/* ============================================
   4. MILESTONE EFFECTS
   ============================================ */
function triggerMilestone(progress) {
    console.log(`%c Milestone: ${progress}% `, 'background: #6D28D9; color: #FCD34D; padding: 5px 10px; border-radius: 3px;');
    
    const stage = document.getElementById('loaderStage');
    if (!stage) return;
    
    stage.style.transform = 'scale(1.03)';
    stage.style.transition = 'transform 0.3s ease';
    setTimeout(() => {
        stage.style.transform = 'scale(1)';
    }, 300);
    
    createLoaderParticles();
}

/* ============================================
   5. LOADER PARTICLES
   ============================================ */
function createLoaderParticles() {
    const stage = document.getElementById('loaderStage');
    if (!stage) return;
    
    const rect = stage.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const colors = ['#6D28D9', '#7C3AED', '#F59E0B', '#FCD34D', '#14B8A6', '#FFFFFF'];
    
    for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        const angle = (Math.PI * 2 * i) / 15;
        const velocity = Math.random() * 50 + 20;
        const size = Math.random() * 5 + 2;
        
        particle.style.cssText = `
            position: fixed;
            left: ${centerX}px;
            top: ${centerY}px;
            width: ${size}px;
            height: ${size}px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            animation: loaderBurst 0.6s ease-out;
            --vx: ${Math.cos(angle) * velocity}px;
            --vy: ${Math.sin(angle) * velocity}px;
        `;
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 600);
    }
    
    if (!document.getElementById('loader-particle-style')) {
        const style = document.createElement('style');
        style.id = 'loader-particle-style';
        style.textContent = `
            @keyframes loaderBurst {
                from { transform: translate(0, 0) scale(1); opacity: 1; }
                to { transform: translate(var(--vx), var(--vy)) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   6. SHOW SUCCESS
   ============================================ */
function showSuccess() {
    console.log('%c ✅ All Letters Loaded! U-N-I-Y-O Complete! ', 'background: #10B981; color: #FFFFFF; font-size: 18px; font-weight: bold; padding: 10px 20px; border-radius: 5px;');
    
    const stage = document.getElementById('loaderStage');
    const status = document.getElementById('loaderStatus');
    const progressContainer = document.querySelector('.loader-progress-container');
    
    if (stage) stage.style.display = 'none';
    if (status) status.style.display = 'none';
    if (progressContainer) progressContainer.style.display = 'none';
    
    const success = document.getElementById('loaderSuccess');
    if (success) success.style.display = 'block';
    
    triggerSuccessCelebration();
}

/* ============================================
   7. SUCCESS CELEBRATION
   ============================================ */
function triggerSuccessCelebration() {
    const container = document.querySelector('.uniyo-loader-container');
    if (!container) return;
    
    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const colors = ['#6D28D9', '#7C3AED', '#F59E0B', '#FCD34D', '#14B8A6', '#10B981', '#FFFFFF'];
    
    for (let i = 0; i < 60; i++) {
        const particle = document.createElement('div');
        const angle = (Math.PI * 2 * i) / 60;
        const velocity = Math.random() * 100 + 40;
        const size = Math.random() * 7 + 3;
        
        particle.style.cssText = `
            position: fixed;
            left: ${centerX}px;
            top: ${centerY}px;
            width: ${size}px;
            height: ${size}px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            animation: successBurst 1.2s ease-out;
            --vx: ${Math.cos(angle) * velocity}px;
            --vy: ${Math.sin(angle) * velocity}px;
            box-shadow: 0 0 15px ${colors[Math.floor(Math.random() * colors.length)]};
        `;
        
        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 1200);
    }
    
    if (!document.getElementById('success-particle-style')) {
        const style = document.createElement('style');
        style.id = 'success-particle-style';
        style.textContent = `
            @keyframes successBurst {
                from { transform: translate(0, 0) scale(1); opacity: 1; }
                to { transform: translate(var(--vx), var(--vy)) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   8. TOAST NOTIFICATIONS
   ============================================ */
function showLoaderToast(message) {
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
    
    if (!document.getElementById('loader-toast-style')) {
        const style = document.createElement('style');
        style.id = 'loader-toast-style';
        style.textContent = `
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
}