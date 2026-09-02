function renderOtherCertificate(cert) {
    document.getElementById('otherStudentName').textContent = cert.full_name || '';
    document.getElementById('otherStudentDetails').textContent = (cert.university || '') + ' • ' + (cert.stream || '');
    document.getElementById('otherCertNumber').textContent = cert.certificate_number || '';
    document.getElementById('otherToken').textContent = cert.verification_token || '';
    document.getElementById('otherIssueDate').textContent = cert.issue_date || '';
    
    // Set unique title and icon if available
    if (cert._icon) {
        document.getElementById('otherIcon').textContent = cert._icon;
    }
    if (cert._color) {
        document.getElementById('otherTitle').style.color = cert._color;
        document.getElementById('otherTitle').style.borderColor = cert._color;
    }
    
    if (cert.qr_data_uri) {
        document.getElementById('otherQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:60px;height:60px;">';
    }
}