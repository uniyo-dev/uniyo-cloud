function renderPaymentCertificate(cert) {
    document.getElementById('paymentStudentName').textContent = cert.full_name || '';
    document.getElementById('paymentPhone').textContent = cert.phone || '';
    document.getElementById('paymentUniversity').textContent = cert.university || '';
    document.getElementById('paymentAmount').textContent = (cert.amount || 200) + ' ETB';
    document.getElementById('paymentMethod').textContent = cert.payment_method || 'Telebirr';
    document.getElementById('paymentTransaction').textContent = cert.transaction_number || '-';
    document.getElementById('paymentNumber').textContent = cert.certificate_number || '-';
    document.getElementById('paymentDate').textContent = cert.issue_date || '-';
    
    if (cert.qr_data_uri) {
        document.getElementById('paymentQR').innerHTML = '<img src="' + cert.qr_data_uri + '" style="width:45px;height:45px;">';
    }
    
    // Generate barcode
    if (typeof addBarcode === 'function' && cert.certificate_number) {
        addBarcode('paymentBarcode', cert.certificate_number);
    }
}
