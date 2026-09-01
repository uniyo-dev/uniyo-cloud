// ============================================
// UNIYO STUDENT CERTIFICATE VIEW - JS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Apply saved theme
    const savedDarkMode = localStorage.getItem('uniyo_dark_mode');
    if (savedDarkMode === 'light') {
        document.body.classList.add('light-mode');
    }
    
    // Initialize print button
    const printBtn = document.getElementById('printCertBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Initialize download button
    const downloadBtn = document.getElementById('downloadCertBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            downloadCertificate();
        });
    }
    
    // Add entrance animation
    const certDisplay = document.getElementById('certificateDisplay');
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

// Download certificate as image
function downloadCertificate() {
    const certElement = document.getElementById('certificateDisplay');
    if (!certElement) return;
    
    // Show loading toast
    if (typeof showToast === 'function') {
        showToast('Generating download...', 'info');
    }
    
    // Check if html2canvas is loaded
    if (typeof html2canvas === 'undefined') {
        // Load html2canvas dynamically
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        script.onload = () => captureCertificate(certElement);
        document.head.appendChild(script);
    } else {
        captureCertificate(certElement);
    }
}

function captureCertificate(element) {
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
        
        if (typeof showToast === 'function') {
            showToast('Certificate downloaded!', 'success');
        }
    }).catch(err => {
        console.error('Download error:', err);
        if (typeof showToast === 'function') {
            showToast('Download failed. Try Print instead.', 'danger');
        }
    });
}
