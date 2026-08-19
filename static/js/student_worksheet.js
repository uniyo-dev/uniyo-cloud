// ============================================
// UNIYO LMS - Worksheet Engine JavaScript
// ============================================

let selectedAnswers = {};
let answeredCount = 0;
let totalQuestions = document.querySelectorAll('.question-card').length;

function selectOption(button, questionId, option) {
    const options = document.querySelectorAll(`[data-question-id="${questionId}"]`);
    options.forEach(opt => {
        opt.classList.remove('selected');
        opt.classList.remove('correct');
        opt.classList.remove('wrong');
    });
    
    button.classList.add('selected');
    selectedAnswers[questionId] = option;
    updateAnsweredCount();
    showFeedback(questionId, option);
}

function showFeedback(questionId, selectedOption) {
    const questionCard = document.getElementById(`question-${questionId}`);
    const options = questionCard.querySelectorAll('.option-btn');
    
    let correctAnswer = '';
    options.forEach(opt => {
        if (opt.dataset.correct === 'true') {
            correctAnswer = opt.dataset.option;
        }
    });
    
    if (!correctAnswer) return;
    
    const feedbackArea = document.getElementById(`feedback-${questionId}`);
    const feedbackResult = document.getElementById(`feedbackResult-${questionId}`);
    
    feedbackArea.classList.remove('hidden');
    
    options.forEach(opt => {
        opt.disabled = true;
        if (opt.dataset.option === correctAnswer) {
            opt.classList.add('correct');
            opt.dataset.correct = 'true';
        }
        if (opt.dataset.option === selectedOption && selectedOption !== correctAnswer) {
            opt.classList.add('wrong');
        }
    });
    
    if (selectedOption === correctAnswer) {
        feedbackResult.textContent = '✓ Correct!';
        feedbackResult.className = 'feedback-result correct';
    } else {
        feedbackResult.textContent = '✗ Incorrect';
        feedbackResult.className = 'feedback-result wrong';
    }
    
    const savedAnswers = JSON.parse(localStorage.getItem('worksheetAnswers') || '{}');
    savedAnswers[questionId] = selectedOption;
    localStorage.setItem('worksheetAnswers', JSON.stringify(savedAnswers));
}

function toggleExplanation(questionId) {
    const explanation = document.getElementById(`explanation-${questionId}`);
    explanation.classList.toggle('hidden');
}

function updateAnsweredCount() {
    answeredCount = Object.keys(selectedAnswers).length;
    document.getElementById('answeredCount').textContent = answeredCount;
}

function submitWorksheet() {
    if (answeredCount < totalQuestions) {
        const confirmSubmit = confirm(`You have answered ${answeredCount}/${totalQuestions} questions. Submit anyway?`);
        if (!confirmSubmit) return;
    }
    
    const answers = {};
    document.querySelectorAll('.question-card').forEach(card => {
        const questionId = card.dataset.questionId;
        answers[questionId] = selectedAnswers[questionId] || '';
    });
    
    fetch(`/api/worksheet/${worksheetId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResults(data);
        }
    })
    .catch(() => {
        showToast('Error submitting worksheet', 'danger');
    });
}

function showResults(data) {
    const resultsModal = document.getElementById('resultsModal');
    const resultsContent = document.getElementById('resultsContent');
    
    resultsContent.innerHTML = `
        <div style="margin-bottom:20px;">
            <h3 style="font-size:48px;color:#F59E0B;">${data.score} / ${data.total}</h3>
            <p style="color:#94A3B8;">${data.percentage}%</p>
            <p style="color:#94A3B8;">Attempt: #${data.attempt_number}</p>
        </div>
    `;
    
    resultsModal.classList.remove('hidden');
    localStorage.removeItem('worksheetAnswers');
}

function closeResults() {
    document.getElementById('resultsModal').classList.add('hidden');
    location.reload();
}

document.addEventListener('DOMContentLoaded', function() {
    const savedAnswers = JSON.parse(localStorage.getItem('worksheetAnswers') || '{}');
    Object.keys(savedAnswers).forEach(questionId => {
        const answer = savedAnswers[questionId];
        const optionBtn = document.querySelector(`[data-question-id="${questionId}"][data-option="${answer}"]`);
        if (optionBtn) {
            optionBtn.classList.add('selected');
            selectedAnswers[questionId] = answer;
        }
    });
    updateAnsweredCount();
});
