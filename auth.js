// ============================================
// UNIYO LMS - Authentication JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    const photoInput = document.getElementById('photoInput');
    const photoPreview = document.getElementById('photoPreview');
    
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    photoPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const passwordMatch = document.getElementById('passwordMatch');
    
    if (password && confirmPassword && passwordMatch) {
        confirmPassword.addEventListener('input', function() {
            if (this.value === password.value && this.value !== '') {
                passwordMatch.textContent = '✓ Passwords match';
                passwordMatch.className = 'validation-message success';
            } else if (this.value === '') {
                passwordMatch.textContent = '';
                passwordMatch.className = 'validation-message';
            } else {
                passwordMatch.textContent = '✗ Passwords do not match';
                passwordMatch.className = 'validation-message error';
            }
        });
        
        password.addEventListener('input', function() {
            if (this.value.length < 8) {
                this.style.borderColor = '#EC4899';
            } else if (!/[A-Za-z]/.test(this.value) || !/[0-9]/.test(this.value)) {
                this.style.borderColor = '#F59E0B';
            } else {
                this.style.borderColor = '#14B8A6';
            }
        });
    }
    
    const phoneInput = document.querySelector('input[name="phone"]');
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            const phonePattern = /^(09|07)[0-9]{8}$/;
            if (this.value.length === 10) {
                if (phonePattern.test(this.value)) {
                    this.style.borderColor = '#14B8A6';
                } else {
                    this.style.borderColor = '#EC4899';
                }
            }
        });
    }
});

function previewPhoto(input) {
    const preview = document.getElementById('photoPreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}
