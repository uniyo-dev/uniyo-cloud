// ============================================
// UNIYO LMS - Student Dashboard JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    fetch('/api/vip/status')
        .then(response => response.json())
        .then(data => {
            if (data.active_vip && data.active_vip.length > 0) {
                showToast('🔴 VIP question is LIVE now!', 'warning');
            } else if (data.upcoming_vip && data.upcoming_vip.length > 0) {
                showToast('📅 Upcoming VIP question scheduled', 'info');
            }
        })
        .catch(() => {});
});

function scrollToPayment() {
    const paymentSection = document.getElementById('paymentSection');
    if (paymentSection) {
        paymentSection.scrollIntoView({ behavior: 'smooth' });
    }
}
