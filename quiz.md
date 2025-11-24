---
layout: default
title: Knowledge Quiz - Delta Lake & Apache Iceberg
description: Test your knowledge of Delta Lake and Apache Iceberg with our interactive quiz
---

<div class="quiz-container">
    <div class="quiz-header">
        <h1>🧠 Knowledge Quiz</h1>
        <p>Test your understanding of Delta Lake and Apache Iceberg technologies</p>
        <div class="quiz-progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
            <span class="progress-text" id="progress-text">Question 1 of 10</span>
        </div>
    </div>

    <div class="quiz-content">
        <div class="question-card" id="question-card">
            <h2 id="question-text">Loading question...</h2>
            <div class="options" id="options">
                <!-- Options will be populated by JavaScript -->
            </div>
        </div>

        <div class="quiz-controls">
            <button class="btn btn-secondary" id="prev-btn" disabled>Previous</button>
            <button class="btn btn-primary" id="next-btn" disabled>Next</button>
            <button class="btn btn-success" id="submit-btn" style="display: none;">Submit Quiz</button>
        </div>
    </div>

    <div class="quiz-results" id="quiz-results" style="display: none;">
        <div class="results-header">
            <h2>Quiz Complete!</h2>
            <div class="score-display">
                <div class="score-circle">
                    <span id="final-score">0</span>
                    <span class="score-total">/10</span>
                </div>
                <p id="score-message"></p>
            </div>
        </div>

        <div class="results-details">
            <h3>Detailed Results</h3>
            <div id="results-breakdown">
                <!-- Results will be populated by JavaScript -->
            </div>
        </div>

        <div class="leaderboard-section">
            <h3>🏆 Leaderboard</h3>
            <div id="leaderboard">
                <!-- Leaderboard will be populated by JavaScript -->
            </div>
            <button class="btn btn-primary" id="submit-score-btn">Submit Your Score</button>
        </div>

        <div class="quiz-actions">
            <button class="btn btn-secondary" id="retake-btn">Retake Quiz</button>
            <button class="btn btn-primary" id="share-btn">Share Results</button>
        </div>
    </div>
</div>

<script src="{{ '/assets/js/github-leaderboard.js' | absolute_url }}"></script>
<script src="{{ '/assets/js/quiz-engine.js' | absolute_url }}"></script>