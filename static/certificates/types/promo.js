function renderPromoCertificate(cert) {
    document.getElementById('promoStudentName').textContent = cert.full_name || '';
    document.getElementById('promoStudentDetails').textContent = (cert.university || '') + ' • ' + (cert.stream || '');
    document.getElementById('promoCertNumber').textContent = cert.certificate_number || '';
    document.getElementById('promoToken').textContent = cert.verification_token || '';
    document.getElementById('promoIssueDate').textContent = cert.issue_date || '';
    if (cert.qr_data_uri) {
        document.getElementById('promoQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:60px;height:60px;">';
    }
}
