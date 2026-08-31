// ============================================
// UNIYO POPUP SYSTEM
// ============================================

const PopupSystem = {
    // Show confirmation popup
    confirm(title, message, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.className = 'popup-overlay';
        overlay.innerHTML = `
            <div class="popup-card">
                <div class="popup-header">
                    <div class="popup-icon">⚠️</div>
                    <div class="popup-title">${title}</div>
                    <div class="popup-message">${message}</div>
                </div>
                <div class="popup-actions">
                    <button class="popup-btn popup-btn-outline" id="popupCancel">Cancel</button>
                    <button class="popup-btn popup-btn-primary" id="popupConfirm">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        document.getElementById('popupCancel').onclick = () => {
            overlay.remove();
            if (onCancel) onCancel();
        };
        
        document.getElementById('popupConfirm').onclick = () => {
            overlay.remove();
            if (onConfirm) onConfirm();
        };
        
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.remove();
                if (onCancel) onCancel();
            }
        };
    },
    
    // Show success popup
    success(title, message, onClose) {
        this.show('success', '✅', title, message, onClose);
    },
    
    // Show error popup
    error(title, message, onClose) {
        this.show('error', '❌', title, message, onClose);
    },
    
    // Show warning popup
    warning(title, message, onClose) {
        this.show('warning', '⚠️', title, message, onClose);
    },
    
    // Show info popup
    info(title, message, onClose) {
        this.show('info', 'ℹ️', title, message, onClose);
    },
    
    // Generic show
    show(type, icon, title, message, onClose) {
        const overlay = document.createElement('div');
        overlay.className = `popup-overlay popup-${type}`;
        overlay.innerHTML = `
            <div class="popup-card">
                <div class="popup-header">
                    <div class="popup-icon">${icon}</div>
                    <div class="popup-title">${title}</div>
                    <div class="popup-message">${message}</div>
                </div>
                <div class="popup-actions">
                    <button class="popup-btn popup-btn-primary" id="popupClose">OK</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        const close = () => {
            overlay.remove();
            if (onClose) onClose();
        };
        
        document.getElementById('popupClose').onclick = close;
        overlay.onclick = (e) => {
            if (e.target === overlay) close();
        };
    },
    
    // Show dropdown popup
    dropdown(title, options, onSelect) {
        const overlay = document.createElement('div');
        overlay.className = 'popup-overlay';
        overlay.innerHTML = `
            <div class="popup-card">
                <div class="popup-header">
                    <div class="popup-title">${title}</div>
                </div>
                <div class="popup-dropdown">
                    ${options.map(opt => `<div class="popup-option" data-value="${opt.value}">${opt.label}</div>`).join('')}
                </div>
                <div class="popup-actions">
                    <button class="popup-btn popup-btn-outline" id="popupDropdownCancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        overlay.querySelectorAll('.popup-option').forEach(option => {
            option.onclick = () => {
                overlay.remove();
                if (onSelect) onSelect(option.dataset.value);
            };
        });
        
        document.getElementById('popupDropdownCancel').onclick = () => overlay.remove();
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.remove();
        };
    }
};

// Global access
window.PopupSystem = PopupSystem;
