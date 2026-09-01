// BRAVE — Certificate Controller
// Adds print functionality and interactive elements

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c BRAVE CERTIFICATE ', 'background: #1a5f7a; color: #ffffff; font-size: 20px; font-weight: bold; padding: 10px 20px; border-radius: 5px;');
    
    const certificate = document.querySelector('.certificate');
    const stamp = document.querySelector('.stamp-container');
    
    // Add print button
    const printButton = document.createElement('button');
    printButton.textContent = '🖨️ Print Certificate';
    printButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 24px;
        background: #0b3b5c;
        color: white;
        border: 2px solid #e6b422;
        border-radius: 30px;
        font-size: 1rem;
        cursor: pointer;
        font-family: 'Georgia', serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    `;
    
    printButton.addEventListener('mouseenter', () => {
        printButton.style.transform = 'translateY(-2px)';
        printButton.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.3)';
    });
    
    printButton.addEventListener('mouseleave', () => {
        printButton.style.transform = 'translateY(0)';
        printButton.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
    });
    
    printButton.addEventListener('click', () => {
        window.print();
    });
    
    document.body.appendChild(printButton);
    
    // Stamp hover effect
    if (stamp) {
        stamp.addEventListener('mouseenter', () => {
            stamp.style.opacity = '1';
            stamp.style.transform = 'scale(1.05)';
            stamp.style.transition = 'all 0.3s ease';
        });
        
        stamp.addEventListener('mouseleave', () => {
            stamp.style.opacity = '0.85';
            stamp.style.transform = 'scale(1)';
        });
        
        // Click to "stamp" effect
        stamp.addEventListener('click', () => {
            stamp.style.transform = 'scale(0.95) rotate(-5deg)';
            stamp.style.opacity = '1';
            
            setTimeout(() => {
                stamp.style.transform = 'scale(1) rotate(0deg)';
                stamp.style.opacity = '0.85';
            }, 300);
        });
    }
    
    // Add keyboard shortcut for printing
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
            e.preventDefault();
            window.print();
        }
    });
    
    // Print styles
    const printStyles = document.createElement('style');
    printStyles.textContent = `
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .certificate {
                box-shadow: none;
                max-width: 100%;
                padding: 0;
            }
            button {
                display: none !important;
            }
            .stamp-container {
                opacity: 1 !important;
            }
        }
    `;
    document.head.appendChild(printStyles);
});
