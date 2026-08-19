// ============================================
// UNIYO LMS - Lesson Reader JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    const lessonContent = document.getElementById('lessonContent');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const markCompleteBtn = document.getElementById('markCompleteBtn');
    const protectionToast = document.getElementById('protectionToast');
    
    if (!lessonContent) return;
    
    const lessonId = lessonContent.dataset.lessonId;
    
    lessonContent.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showProtectionToast();
    });
    
    lessonContent.addEventListener('selectstart', function(e) {
        e.preventDefault();
    });
    
    lessonContent.addEventListener('dragstart', function(e) {
        e.preventDefault();
    });
    
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && ['c', 'p', 's', 'u', 'a'].includes(e.key.toLowerCase())) {
            if (lessonContent) {
                e.preventDefault();
                showProtectionToast();
            }
        }
    });
    
    function showProtectionToast() {
        protectionToast.style.display = 'block';
        setTimeout(() => { protectionToast.style.display = 'none'; }, 2000);
    }
    
    let scrollProgress = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (scrollHeight > 0) {
            scrollProgress = Math.round((scrollTop / scrollHeight) * 100);
        }
    });
    
    setInterval(saveProgress, 30000);
    
    function saveProgress() {
        if (scrollProgress > 0) {
            fetch(`/api/lessons/${lessonId}/progress`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    progress_percent: scrollProgress,
                    last_position: window.scrollY,
                    is_completed: 0
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    progressFill.style.width = scrollProgress + '%';
                    progressPercent.textContent = scrollProgress + '%';
                }
            })
            .catch(() => {});
        }
    }
    
    if (markCompleteBtn) {
        markCompleteBtn.addEventListener('click', function() {
            fetch(`/api/lessons/${lessonId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    markCompleteBtn.textContent = '✓ Completed';
                    markCompleteBtn.classList.add('completed');
                    progressFill.style.width = '100%';
                    progressPercent.textContent = '100%';
                    showToast('Lesson completed! 🎉', 'success');
                }
            });
        });
    }
    
    loadSelfCheckQuestions();
    
    function loadSelfCheckQuestions() {
        const container = document.getElementById('selfCheckContainer');
        if (!container) return;
        
        const urlParts = window.location.pathname.split('/');
        const courseCode = urlParts[urlParts.indexOf('lessons') + 1];
        const chapter = urlParts[urlParts.indexOf('chapter') + 1];
        
        fetch(`/api/worksheets/${courseCode}/chapter/${chapter}/questions`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.questions.length > 0) {
                    renderSelfCheckQuestions(data.questions);
                } else {
                    container.innerHTML = '<div class="coming-soon-box"><h4>📝 Practice Questions Coming Soon!</h4><p>We are preparing detailed practice questions with explanations for this lesson. Check back soon!</p></div>';
                }
            })
            .catch(() => {
                container.innerHTML = '<div class="coming-soon-box"><h4>📝 Practice Questions Coming Soon!</h4><p>We are preparing detailed practice questions with explanations for this lesson. Check back soon!</p></div>';
            });
    }
    
    function renderSelfCheckQuestions(questions) {
        const container = document.getElementById('selfCheckContainer');
        container.innerHTML = '';
        
        questions.slice(0, 3).forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-card';
            questionDiv.style.cssText = 'background:#1A2332;border-radius:8px;padding:16px;margin-bottom:12px;';
            questionDiv.innerHTML = `
                <div style="color:#E2E8F0;margin-bottom:12px;"><strong>Q${index + 1}:</strong> ${question.text}</div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    ${question.options.map(option => `
                        <button class="option-btn" style="padding:10px;background:#0B0F19;border:1px solid rgba(255,255,255,0.08);border-radius:6px;color:#E2E8F0;cursor:pointer;text-align:left;" onclick="checkSelfAnswer(this, '${option}', '${question.correct_answer}', ${index})">${option}</button>
                    `).join('')}
                </div>
                <div class="explanation hidden" id="explanation-${index}" style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.05);border-radius:6px;color:#94A3B8;font-size:13px;">
                    <strong>Explanation:</strong> ${question.explanation}
                </div>
            `;
            container.appendChild(questionDiv);
        });
        if (typeof renderMath === 'function') {
            renderMath();
        }
    }
});

function checkSelfAnswer(button, selected, correct, questionIndex) {
    const options = button.parentElement.querySelectorAll('.option-btn');
    options.forEach(opt => opt.disabled = true);
    
    if (selected === correct) {
        button.style.background = 'rgba(20, 184, 166, 0.3)';
        button.style.borderColor = '#14B8A6';
    } else {
        button.style.background = 'rgba(236, 72, 153, 0.3)';
        button.style.borderColor = '#EC4899';
        options.forEach(opt => {
            if (opt.textContent.trim() === correct) {
                opt.style.background = 'rgba(20, 184, 166, 0.3)';
                opt.style.borderColor = '#14B8A6';
            }
        });
    }
    
    const explanation = document.getElementById(`explanation-${questionIndex}`);
    if (explanation) explanation.classList.remove('hidden');
}
