function renderPaymentCertificate(cert) {
    document.getElementById('paymentStudentName').textContent = cert.full_name || '';
    document.getElementById('paymentStudentDetails').textContent = (cert.university || '') + ' • ' + (cert.stream || '');
    document.getElementById('paymentNumber').textContent = cert.certificate_number || '';
    document.getElementById('paymentDate').textContent = cert.issue_date || '';
    if (cert.qr_data_uri) {
        document.getElementById('paymentQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:45px;height:45px;">';
    }
}
