// ============================================
// UNIYO ADMIN CERTIFICATE VIEW - JS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Apply admin theme
    const savedAdminMode = localStorage.getItem('uniyo_admin_dark_mode');
    if (savedAdminMode === 'false') {
        document.body.classList.add('light-mode');
    }
    
    // Set toggle button text
    const themeBtn = document.getElementById('adminThemeBtn');
    if (themeBtn) {
        themeBtn.textContent = savedAdminMode === 'false' ? '☀️ Light' : '🌙 Dark';
    }
    
    // Print functionality
    const printBtn = document.getElementById('printAdminCertBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Download functionality
    const downloadBtn = document.getElementById('downloadAdminCertBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            downloadAdminCertificate();
        });
    }
    
    // Entrance animation
    const certDisplay = document.querySelector('.certificate-display');
    if (certDisplay) {
        certDisplay.style.opacity = '0';
        certDisplay.style.transform = 'translateY(20px)';
        setTimeout(() => {
            certDisplay.style.transition = 'all 0.5s ease';
            certDisplay.style.opacity = '1';
            certDisplay.style.transform = 'translateY(0)';
        }, 100);
    }
});

function downloadAdminCertificate() {
    const certElement = document.querySelector('.certificate-display');
    if (!certElement) return;
    
    if (typeof html2canvas === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        script.onload = () => captureAdminCert(certElement);
        document.head.appendChild(script);
    } else {
        captureAdminCert(certElement);
    }
}

function captureAdminCert(element) {
    html2canvas(element, {
        scale: 2,
        backgroundColor: '#ffffff',
        allowTaint: true,
        useCORS: true,
        logging: false
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = 'UNIYO_Certificate.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    });
}
