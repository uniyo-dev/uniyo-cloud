// ============================================
// UNIYO CERTIFICATE LOADER
// Loads the correct certificate type design
// ============================================

function loadCertificatePopup(certId, popupContentId, isAdmin) {
    var content = document.getElementById(popupContentId);
    if (!content) return;
    
    content.innerHTML = '<p style="color: #94A3B8;">Loading...</p>';
    
    // Determine which API to use
    var apiUrl = isAdmin 
        ? '/admin/api/certificates/' + certId 
        : '/student/api/certificate/' + certId;
    
    fetch(apiUrl)
        .then(function(response) { return response.text(); })
        .then(function(data) {
            // Check if response is JSON or HTML
            try {
                var jsonData = JSON.parse(data);
                renderCertificateByType(jsonData.certificate, content);
            } catch(e) {
                // It's HTML - extract the certificate
                var parser = new DOMParser();
                var doc = parser.parseFromString(data, 'text/html');
                var certDiv = doc.querySelector('.certificate-full-a4') || doc.querySelector('.certificate-display');
                if (certDiv) {
                    content.innerHTML = certDiv.outerHTML;
                } else {
                    content.innerHTML = '<p>Certificate not found</p>';
                }
            }
        })
        .catch(function() {
            content.innerHTML = '<p>Error loading certificate</p>';
        });
}

function renderCertificateByType(cert, content) {
    if (!cert) {
        content.innerHTML = '<p>Certificate not found</p>';
        return;
    }
    
    var certType = cert.certificate_type || 'other';
    var rank = cert.rank || 0;
    var fullName = cert.full_name || '';
    var university = cert.university || '';
    var stream = cert.stream || '';
    var title = cert.title || 'Certificate';
    var certNumber = cert.certificate_number || '';
    var issueDate = cert.issue_date || '';
    
    var html = '';
    
    // Determine primary stamp
    var primaryStamp = '/static/Authenticity/super_admin_stamp.png';
    if (certType == 'vip_leaderboard') {
        if (rank == 1) primaryStamp = '/static/Authenticity/vip1.png';
        else if (rank == 2) primaryStamp = '/static/Authenticity/vip2.png';
        else if (rank == 3) primaryStamp = '/static/Authenticity/vip3.png';
        else if (rank == 4) primaryStamp = '/static/Authenticity/vip4.png';
        else if (rank == 5) primaryStamp = '/static/Authenticity/vip5.png';
    } else if (certType == 'completion') {
        primaryStamp = '/static/Authenticity/general.png';
    } else if (certType == 'payment') {
        primaryStamp = '/static/Authenticity/paid.png';
    } else if (certType == 'promotion') {
        primaryStamp = '/static/Authenticity/promotion.png';
    }
    
    // Build the full certificate HTML
    html += '<div class="certificate-full-a4" style="background:#fffdf9; padding:25px; border:5px double #6D28D9; border-radius:12px; position:relative;">';
    html += '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);font-size:60pt;font-weight:bold;color:rgba(109,40,217,0.05);">UNIYO</div>';
    
    // Header
    html += '<div style="text-align:center;">';
    html += '<img src="/static/Authenticity/default_stamp.png" style="height:45px;object-fit:contain;">';
    html += '<p style="color:#64748b;font-size:9px;letter-spacing:2px;">ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB</p>';
    html += '<h3 style="color:#6D28D9;margin:8px 0;">' + title + '</h3>';
    html += '</div>';
    
    // Medal (for VIP)
    if (certType == 'vip_leaderboard') {
        var medal = '🏆';
        if (rank == 1) medal = '🥇';
        else if (rank == 2) medal = '🥈';
        else if (rank == 3) medal = '🥉';
        html += '<div style="text-align:center;font-size:35px;">' + medal + '</div>';
    }
    
    // Student info
    html += '<div style="text-align:center;margin:15px 0;">';
    html += '<p style="font-size:10px;">This certificate is proudly presented to</p>';
    html += '<div style="font-size:22px;font-weight:700;color:#1e1b4b;border-bottom:2px solid #6D28D9;display:inline-block;padding:0 25px 6px;">' + fullName + '</div>';
    html += '<p style="color:#64748b;font-size:11px;">' + university + ' • ' + stream + '</p>';
    html += '</div>';
    
    // Stamps
    html += '<div style="display:flex;justify-content:space-around;align-items:center;margin:20px 0;">';
    html += '<img src="' + primaryStamp + '" style="width:75px;height:75px;object-fit:contain;border-radius:50%;">';
    
    // Secondary stamp for VIP and Payment
    if (certType == 'vip_leaderboard' || certType == 'payment') {
        html += '<img src="/static/Authenticity/super_admin_stamp.png" style="width:60px;height:60px;object-fit:contain;border-radius:50%;">';
    }
    html += '</div>';
    
    // Signatures
    html += '<div style="display:flex;justify-content:space-around;margin:15px 0;">';
    html += '<div style="text-align:center;">';
    html += '<img src="/static/Authenticity/super_admin_signature.png" style="height:30px;">';
    html += '<p style="font-size:9px;font-weight:600;">Chalachew Agegn</p><small>Super Admin</small>';
    html += '</div>';
    html += '<div style="text-align:center;">';
    html += '<img src="/static/Authenticity/signature_(content_manager).png" style="height:30px;">';
    html += '<p style="font-size:9px;font-weight:600;">Banch Destaw</p><small>Content Manager</small>';
    html += '</div>';
    html += '</div>';
    
    // Certificate details
    html += '<div style="max-width:350px;margin:10px auto;padding:8px;background:rgba(109,40,217,0.05);border-radius:8px;font-size:10px;">';
    html += '<div style="display:flex;justify-content:space-between;"><span>Number:</span><strong>' + certNumber + '</strong></div>';
    html += '<div style="display:flex;justify-content:space-between;"><span>Date:</span><strong>' + issueDate + '</strong></div>';
    html += '</div>';
    
    // QR placeholder
    html += '<div style="text-align:center;margin-top:10px;">';
    html += '<div style="width:60px;height:60px;background:#0B0F19;margin:0 auto;border-radius:4px;"></div>';
    html += '<small>Scan to Verify</small>';
    html += '</div>';
    
    html += '</div>';
    
    content.innerHTML = html;
}
