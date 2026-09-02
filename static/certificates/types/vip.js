// VIP Certificate - Populate Data
function renderVipCertificate(cert) {
    var medal = '🏆';
    var stamp = 'vip1.png';
    
    if (cert.rank == 1) { medal = '🥇'; stamp = 'vip1.png'; }
    else if (cert.rank == 2) { medal = '🥈'; stamp = 'vip2.png'; }
    else if (cert.rank == 3) { medal = '🥉'; stamp = 'vip3.png'; }
    else if (cert.rank == 4) { medal = '🏆'; stamp = 'vip4.png'; }
    else if (cert.rank == 5) { medal = '🏆'; stamp = 'vip5.png'; }
    
    document.getElementById('vipMedal').textContent = medal;
    document.getElementById('vipTitle').textContent = cert.title || 'VIP Certificate';
    document.getElementById('vipStudentName').textContent = cert.full_name || '';
    document.getElementById('vipStudentDetails').textContent = (cert.university || '') + ' • ' + (cert.stream || '');
    document.getElementById('vipPrimaryStamp').src = '/static/Authenticity/' + stamp;
    
    if (cert.qr_data_uri) {
        document.getElementById('vipQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:70px;height:70px;">';
    }
}
