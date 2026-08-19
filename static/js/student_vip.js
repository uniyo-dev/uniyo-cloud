// ============================================
// UNIYO LMS - VIP Competition JavaScript
// ============================================

let vipAnswers = {};
let startTime = Date.now();

function startTimer(endTimeElement, displayElement) {
    const endTime = new Date(endTimeElement.dataset.endTime).getTime();
    
    function updateTimer() {
        const now = Date.now();
        const timeLeft = endTime - now;
        
        if (timeLeft <= 0) {
            displayElement.textContent = '00:00:00';
            if (document.querySelector('.vip-take-header')) {
                submitVip();
            }
            return;
        }
        
        const hours = Math.floor(timeLeft / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
        
        displayElement.textContent = 
            String(hours).padStart(2, '0') + ':' +
            String(minutes).padStart(2, '0') + ':' +
            String(seconds).padStart(2, '0');
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

function selectVipOption(button, questionId, option) {
    const options = document.querySelectorAll(`[data-question-id="${questionId}"]`);
    options.forEach(opt => opt.classList.remove('selected'));
    button.classList.add('selected');
    vipAnswers[questionId] = option;
    
    // Update progress
    updateVipProgress();
}

function updateVipProgress() {
    const answered = Object.keys(vipAnswers).length;
    const total = document.querySelectorAll('.vip-question-card').length;
    
    const answeredCount = document.getElementById('answeredCount');
    const progressPercent = document.getElementById('progressPercent');
    const progressFill = document.getElementById('vipProgressFill');
    
    if (answeredCount) answeredCount.textContent = answered;
    if (progressPercent) progressPercent.textContent = Math.round((answered / total) * 100) + '%';
    if (progressFill) progressFill.style.width = Math.round((answered / total) * 100) + '%';
}

function submitVip() {
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
    
    const totalQuestions = document.querySelectorAll('.question-card').length;
    const answeredCount = Object.keys(vipAnswers).length;
    
    if (answeredCount < totalQuestions) {
        // Show custom modal
        document.getElementById('confirmTitle').textContent = 'Submit Incomplete Answers?';
        document.getElementById('confirmMessage').textContent = `You have answered ${answeredCount}/${totalQuestions} questions. Submit anyway?`;
        document.getElementById('confirmSubmitBtn').onclick = function() {
            closeConfirmModal();
            doSubmitVip(timeSpent);
        };
        document.getElementById('customConfirmModal').classList.remove('hidden');
        return;
    }
    
    doSubmitVip(timeSpent);
}

function doSubmitVip(timeSpent) {
    const answers = {};
    document.querySelectorAll('.question-card').forEach(card => {
        const questionId = card.dataset.questionId;
        answers[questionId] = vipAnswers[questionId] || '';
    });
    
    fetch(`/api/vip/${vipId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answers, time_spent_seconds: timeSpent })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showVipResults(data);
        } else {
            showToast(data.error || 'Error submitting', 'danger');
        }
    })
    .catch(() => {
        showToast('Error submitting VIP', 'danger');
    });
}

function closeConfirmModal() {
    document.getElementById('customConfirmModal').classList.add('hidden');
}

function showVipResults(data) {
    const modal = document.getElementById('vipResultsModal');
    const content = document.getElementById('vipResultsContent');
    
    content.innerHTML = `
        <div style="margin-bottom:20px;">
            <h3 style="font-size:48px;color:#F59E0B;">${data.score} / ${data.total}</h3>
            <p style="color:#94A3B8;">${data.percentage}%</p>
            <p style="color:#94A3B8;">Time: ${data.time_spent} seconds</p>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.querySelector('[data-end-time]');
    const displayElement = document.querySelector('.timer-display-large') || document.querySelector('.timer-display');
    
    if (timerElement && displayElement) {
        startTimer(timerElement, displayElement);
    }
});
