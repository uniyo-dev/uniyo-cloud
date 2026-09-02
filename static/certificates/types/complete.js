function renderCompleteCertificate(cert) {
    document.getElementById('completeStudentName').textContent = cert.full_name || '';
    document.getElementById('completeStudentDetails').textContent = (cert.university || '') + ' • ' + (cert.stream || '');
    document.getElementById('completeCertNumber').textContent = cert.certificate_number || '';
    document.getElementById('completeToken').textContent = cert.verification_token || '';
    document.getElementById('completeIssueDate').textContent = cert.issue_date || '';
    if (cert.qr_data_uri) {
        document.getElementById('completeQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:65px;height:65px;">';
    }
}
