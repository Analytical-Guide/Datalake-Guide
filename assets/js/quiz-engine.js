// Quiz Engine for Delta Lake & Apache Iceberg Knowledge Hub

class QuizEngine {
    constructor() {
        this.quizData = null;
        this.currentQuestionIndex = 0;
        this.userAnswers = [];
        this.score = 0;
        this.startTime = null;
        this.endTime = null;
        this.githubLeaderboard = null;

        this.elements = {
            questionCard: document.getElementById('question-card'),
            questionText: document.getElementById('question-text'),
            options: document.getElementById('options'),
            progressFill: document.getElementById('progress-fill'),
            progressText: document.getElementById('progress-text'),
            prevBtn: document.getElementById('prev-btn'),
            nextBtn: document.getElementById('next-btn'),
            submitBtn: document.getElementById('submit-btn'),
            quizResults: document.getElementById('quiz-results'),
            finalScore: document.getElementById('final-score'),
            scoreMessage: document.getElementById('score-message'),
            resultsBreakdown: document.getElementById('results-breakdown'),
            leaderboard: document.getElementById('leaderboard'),
            submitScoreBtn: document.getElementById('submit-score-btn'),
            retakeBtn: document.getElementById('retake-btn'),
            shareBtn: document.getElementById('share-btn'),
            liveRegion: document.getElementById('live-region'),
            liveAssertive: document.getElementById('live-assertive')
        };

        this.init();
    }

    async init() {
        try {
            // Load quiz data
            const response = await fetch('/assets/js/quiz-data.json');
            this.quizData = await response.json();

            // Initialize GitHub leaderboard
            this.githubLeaderboard = new GitHubLeaderboard();
            await this.githubLeaderboard.initialize();

            this.setupEventListeners();
            this.loadSavedProgress();
            this.showQuestion();
        } catch (error) {
            console.error('Failed to initialize quiz:', error);
            this.showError('Failed to load quiz. Please refresh the page.');
        }
    }

    setupEventListeners() {
        this.elements.prevBtn.addEventListener('click', () => this.previousQuestion());
        this.elements.nextBtn.addEventListener('click', () => this.nextQuestion());
        this.elements.submitBtn.addEventListener('click', () => this.submitQuiz());
        this.elements.submitScoreBtn.addEventListener('click', () => this.submitScore());
        this.elements.retakeBtn.addEventListener('click', () => this.retakeQuiz());
        this.elements.shareBtn.addEventListener('click', () => this.shareResults());
    }

    loadSavedProgress() {
        const saved = localStorage.getItem('quiz-progress');
        if (saved) {
            const progress = JSON.parse(saved);
            this.currentQuestionIndex = progress.currentQuestionIndex || 0;
            this.userAnswers = progress.userAnswers || [];
            this.startTime = progress.startTime ? new Date(progress.startTime) : new Date();
        } else {
            this.startTime = new Date();
        }
    }

    saveProgress() {
        const progress = {
            currentQuestionIndex: this.currentQuestionIndex,
            userAnswers: this.userAnswers,
            startTime: this.startTime.toISOString()
        };
        localStorage.setItem('quiz-progress', JSON.stringify(progress));
    }

    showQuestion() {
        if (!this.quizData) return;

        const question = this.quizData.questions[this.currentQuestionIndex];
        this.elements.questionText.textContent = question.question;

        this.elements.options.innerHTML = '';
        question.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'option';
            optionElement.innerHTML = `
                <input type="radio" id="option-${index}" name="quiz-option" value="${index}">
                <label for="option-${index}">${option}</label>
            `;
            optionElement.addEventListener('click', () => this.selectOption(index));
            this.elements.options.appendChild(optionElement);
        });

        // Restore previous answer if exists
        if (this.userAnswers[this.currentQuestionIndex] !== undefined) {
            const selectedOption = document.getElementById(`option-${this.userAnswers[this.currentQuestionIndex]}`);
            if (selectedOption) {
                selectedOption.checked = true;
                this.elements.nextBtn.disabled = false;
            }
        }

        this.updateProgress();
        this.announce(`Question ${this.currentQuestionIndex + 1} of ${this.quizData.questions.length}`);
        this.updateNavigationButtons();
    }

    selectOption(optionIndex) {
        this.userAnswers[this.currentQuestionIndex] = optionIndex;
        this.elements.nextBtn.disabled = false;
        this.saveProgress();
        this.announce('Option selected');
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.quizData.questions.length - 1) {
            this.currentQuestionIndex++;
            this.showQuestion();
        } else {
            this.elements.submitBtn.style.display = 'inline-block';
            this.elements.nextBtn.style.display = 'none';
        }
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.showQuestion();
        }
    }

    updateProgress() {
        const progress = ((this.currentQuestionIndex + 1) / this.quizData.questions.length) * 100;
        this.elements.progressFill.style.width = `${progress}%`;
        this.elements.progressText.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.quizData.questions.length}`;
    }

    updateNavigationButtons() {
        this.elements.prevBtn.disabled = this.currentQuestionIndex === 0;
        this.elements.nextBtn.disabled = this.userAnswers[this.currentQuestionIndex] === undefined;

        if (this.currentQuestionIndex === this.quizData.questions.length - 1) {
            this.elements.nextBtn.style.display = 'none';
            this.elements.submitBtn.style.display = 'inline-block';
        } else {
            this.elements.nextBtn.style.display = 'inline-block';
            this.elements.submitBtn.style.display = 'none';
        }
    }

    submitQuiz() {
        this.endTime = new Date();
        this.calculateScore();
        this.showResults();
        localStorage.removeItem('quiz-progress');
        this.announceAssertive(`Quiz complete. Your score is ${this.score} out of ${this.quizData.questions.length}.`);
    }

    calculateScore() {
        this.score = 0;
        this.quizData.questions.forEach((question, index) => {
            if (this.userAnswers[index] === question.correctAnswer) {
                this.score++;
            }
        });
    }

    showResults() {
        this.elements.questionCard.style.display = 'none';
        this.elements.quizResults.style.display = 'block';

        this.elements.finalScore.textContent = this.score;
        this.elements.scoreMessage.textContent = this.getScoreMessage();

        this.showResultsBreakdown();
        this.loadLeaderboard();
    }

    announce(message) {
        if (this.elements.liveRegion) {
            this.elements.liveRegion.textContent = '';
            // Force DOM update for screen readers
            setTimeout(() => {
                this.elements.liveRegion.textContent = message;
            }, 50);
        }
    }

    announceAssertive(message) {
        if (this.elements.liveAssertive) {
            this.elements.liveAssertive.textContent = '';
            setTimeout(() => {
                this.elements.liveAssertive.textContent = message;
            }, 50);
        }
    }

    getScoreMessage() {
        const scoring = this.quizData.scoring;
        for (const [level, config] of Object.entries(scoring)) {
            if (this.score >= config.min) {
                return config.message;
            }
        }
        return scoring.needs_improvement.message;
    }

    showResultsBreakdown() {
        this.elements.resultsBreakdown.innerHTML = '';

        this.quizData.questions.forEach((question, index) => {
            const isCorrect = this.userAnswers[index] === question.correctAnswer;
            const userAnswer = question.options[this.userAnswers[index]] || 'Not answered';
            const correctAnswer = question.options[question.correctAnswer];

            const resultElement = document.createElement('div');
            resultElement.className = `result-item ${isCorrect ? 'correct' : 'incorrect'}`;
            resultElement.innerHTML = `
                <h4>Question ${index + 1}</h4>
                <p><strong>Your answer:</strong> ${userAnswer}</p>
                <p><strong>Correct answer:</strong> ${correctAnswer}</p>
                <p><em>${question.explanation}</em></p>
            `;
            this.elements.resultsBreakdown.appendChild(resultElement);
        });
    }

    async loadLeaderboard() {
        try {
            const leaderboard = await this.githubLeaderboard.getLeaderboard();
            this.displayLeaderboard(leaderboard);
        } catch (error) {
            console.error('Failed to load leaderboard:', error);
            this.elements.leaderboard.innerHTML = '<p>Unable to load leaderboard at this time.</p>';
        }
    }

    displayLeaderboard(leaderboard) {
        if (leaderboard.length === 0) {
            this.elements.leaderboard.innerHTML = '<p>No scores submitted yet. Be the first!</p>';
            return;
        }

        const leaderboardHtml = leaderboard
            .slice(0, 10)
            .map((entry, index) => {
                const timeDisplay = entry.timeTaken ? `${Math.round(entry.timeTaken / 1000)}s` : 'N/A';
                const dateDisplay = new Date(entry.date).toLocaleDateString();
                return `
                    <div class="leaderboard-entry">
                        <span class="rank">#${index + 1}</span>
                        <span class="name">${entry.name}</span>
                        <span class="score">${entry.score}/10</span>
                        <span class="time">${timeDisplay}</span>
                        <span class="date">${dateDisplay}</span>
                    </div>
                `;
            })
            .join('');

        this.elements.leaderboard.innerHTML = leaderboardHtml;
    }

    async submitScore() {
        const name = prompt('Enter your name for the leaderboard:');
        if (!name || name.trim() === '') return;

        try {
            const timeTaken = this.endTime - this.startTime;
            const success = await this.githubLeaderboard.submitScore(name.trim(), this.score, timeTaken);

            if (success) {
                // Reload leaderboard to show new score
                await this.loadLeaderboard();
                alert('Score submitted successfully! It may take a moment to appear on the leaderboard.');
            } else {
                alert('Failed to submit score. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting score:', error);
            alert('Failed to submit score. Please try again.');
        }
    }

    retakeQuiz() {
        this.currentQuestionIndex = 0;
        this.userAnswers = [];
        this.score = 0;
        this.startTime = new Date();
        this.endTime = null;

        this.elements.quizResults.style.display = 'none';
        this.elements.questionCard.style.display = 'block';

        this.showQuestion();
    }

    shareResults() {
        const text = `I scored ${this.score}/10 on the Delta Lake & Apache Iceberg Knowledge Quiz! 🧠 Test your knowledge: ${window.location.href}`;
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;

        window.open(url, '_blank', 'width=600,height=400');
    }

    showError(message) {
        this.elements.questionCard.innerHTML = `
            <div class="error-message">
                <h2>⚠️ Error</h2>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
            </div>
        `;
    }
}

// Initialize quiz when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuizEngine();
});