// ============================================
// UNIYO BARCODE + QR GENERATOR
// ============================================

function generateBarcode(text) {
    // Simple Code 128-like barcode representation
    var bars = '';
    var pattern = '1010101010'; // Start pattern
    
    for (var i = 0; i < text.length; i++) {
        var code = text.charCodeAt(i);
        var binary = code.toString(2).padStart(8, '0');
        pattern += binary;
    }
    
    pattern += '1010101010'; // End pattern
    
    // Render as HTML div bars
    var html = '<div style="display:flex;align-items:center;height:40px;">';
    for (var j = 0; j < pattern.length; j++) {
        if (pattern[j] === '1') {
            html += '<div style="width:2px;height:40px;background:#000;"></div>';
        } else {
            html += '<div style="width:1px;height:40px;background:#fff;"></div>';
        }
    }
    html += '</div>';
    html += '<small style="font-size:7px;font-family:monospace;">' + text + '</small>';
    
    return html;
}

function addBarcode(elementId, text) {
    var el = document.getElementById(elementId);
    if (el && text) {
        el.innerHTML = generateBarcode(text);
    }
}

function addQRCode(elementId, dataUri) {
    var el = document.getElementById(elementId);
    if (el && dataUri) {
        el.innerHTML = '<img src="' + dataUri + '" style="width:60px;height:60px;">';
    }
}
