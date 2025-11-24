// GitHub API Integration for Quiz Leaderboard

class GitHubLeaderboard {
    constructor() {
        this.repoOwner = 'Analytical-Guide';
        this.repoName = 'Datalake-Guide';
        this.leaderboardIssueNumber = null; // Will be set after finding/creating the issue
        this.apiBase = 'https://api.github.com';
    }

    async initialize() {
        try {
            await this.findOrCreateLeaderboardIssue();
        } catch (error) {
            console.error('Failed to initialize GitHub leaderboard:', error);
        }
    }

    async findOrCreateLeaderboardIssue() {
        try {
            // Search for existing leaderboard issue
            const searchResponse = await fetch(
                `${this.apiBase}/search/issues?q=repo:${this.repoOwner}/${this.repoName}+label:quiz-leaderboard+state:open`,
                {
                    headers: {
                        'Accept': 'application/vnd.github.v3+json'
                    }
                }
            );

            const searchData = await searchResponse.json();

            if (searchData.items && searchData.items.length > 0) {
                this.leaderboardIssueNumber = searchData.items[0].number;
                return;
            }

            // Create new leaderboard issue if none exists
            await this.createLeaderboardIssue();

        } catch (error) {
            console.error('Error finding/creating leaderboard issue:', error);
            throw error;
        }
    }

    async createLeaderboardIssue() {
        const issueData = {
            title: '🧠 Quiz Leaderboard - Delta Lake & Apache Iceberg Knowledge Hub',
            body: this.getInitialLeaderboardBody(),
            labels: ['quiz-leaderboard', 'enhancement']
        };

        try {
            const response = await fetch(
                `${this.apiBase}/repos/${this.repoOwner}/${this.repoName}/issues`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/vnd.github.v3+json'
                        // Note: In production, you'd need authentication for creating issues
                        // For now, this is for demonstration - users would submit scores via comments
                    },
                    body: JSON.stringify(issueData)
                }
            );

            if (response.ok) {
                const data = await response.json();
                this.leaderboardIssueNumber = data.number;
            } else {
                throw new Error(`Failed to create issue: ${response.status}`);
            }
        } catch (error) {
            console.error('Error creating leaderboard issue:', error);
            throw error;
        }
    }

    getInitialLeaderboardBody() {
        return `# 🧠 Quiz Leaderboard

This issue tracks the leaderboard for the Delta Lake & Apache Iceberg Knowledge Quiz.

## How to Submit Your Score

Comment on this issue with the following format:
\`\`\`
QUIZ_SCORE: [Your Score]/10
NAME: [Your Name]
TIME: [Time taken in seconds, optional]
\`\`\`

Example:
\`\`\`
QUIZ_SCORE: 9/10
NAME: Data Engineer
TIME: 180
\`\`\`

<!-- QUIZ_LEADERBOARD_START -->
## Current Leaderboard

| Rank | Name | Score | Date | Time |
|------|------|-------|------|------|
| - | No scores yet | - | - | - |
<!-- QUIZ_LEADERBOARD_END -->

*This leaderboard is automatically updated when new scores are submitted.*
`;
    }

    async submitScore(name, score, timeTaken = null) {
        if (!this.leaderboardIssueNumber) {
            throw new Error('Leaderboard issue not initialized');
        }

        const commentBody = `\`\`\`
QUIZ_SCORE: ${score}/10
NAME: ${name}
TIME: ${timeTaken ? Math.round(timeTaken / 1000) : 'N/A'}
\`\`\`

I scored ${score}/10 on the Delta Lake & Apache Iceberg Knowledge Quiz! 🧠`;

        try {
            const response = await fetch(
                `${this.apiBase}/repos/${this.repoOwner}/${this.repoName}/issues/${this.leaderboardIssueNumber}/comments`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/vnd.github.v3+json'
                        // Note: In a real implementation, you'd need authentication
                    },
                    body: JSON.stringify({ body: commentBody })
                }
            );

            if (response.ok) {
                return true;
            } else {
                // Fallback to local storage if API fails
                console.warn('GitHub API submission failed, using local storage');
                this.storeLocally(name, score, timeTaken);
                return true;
            }
        } catch (error) {
            console.error('Error submitting score to GitHub:', error);
            // Fallback to local storage
            this.storeLocally(name, score, timeTaken);
            return true;
        }
    }

    async getLeaderboard() {
        if (!this.leaderboardIssueNumber) {
            return this.getLocalLeaderboard();
        }

        try {
            const response = await fetch(
                `${this.apiBase}/repos/${this.repoOwner}/${this.repoName}/issues/${this.leaderboardIssueNumber}/comments`,
                {
                    headers: {
                        'Accept': 'application/vnd.github.v3+json'
                    }
                }
            );

            if (response.ok) {
                const comments = await response.json();
                return this.parseLeaderboardFromComments(comments);
            } else {
                throw new Error(`Failed to fetch comments: ${response.status}`);
            }
        } catch (error) {
            console.error('Error fetching leaderboard from GitHub:', error);
            return this.getLocalLeaderboard();
        }
    }

    parseLeaderboardFromComments(comments) {
        const scores = [];

        comments.forEach(comment => {
            const body = comment.body;
            const scoreMatch = body.match(/QUIZ_SCORE:\s*(\d+)\/10/);
            const nameMatch = body.match(/NAME:\s*(.+)/);
            const timeMatch = body.match(/TIME:\s*(.+)/);

            if (scoreMatch && nameMatch) {
                scores.push({
                    name: nameMatch[1].trim(),
                    score: parseInt(scoreMatch[1]),
                    date: comment.created_at,
                    timeTaken: timeMatch ? parseInt(timeMatch[1]) * 1000 : null,
                    source: 'github'
                });
            }
        });

        // Sort by score (descending), then by time (ascending)
        scores.sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            if (a.timeTaken && b.timeTaken) return a.timeTaken - b.timeTaken;
            return 0;
        });

        return scores.slice(0, 50); // Top 50 scores
    }

    storeLocally(name, score, timeTaken) {
        const leaderboard = this.getLocalLeaderboard();
        leaderboard.push({
            name,
            score,
            date: new Date().toISOString(),
            timeTaken,
            source: 'local'
        });

        leaderboard.sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            if (a.timeTaken && b.timeTaken) return a.timeTaken - b.timeTaken;
            return 0;
        });

        localStorage.setItem('quiz-leaderboard', JSON.stringify(leaderboard));
    }

    getLocalLeaderboard() {
        const stored = localStorage.getItem('quiz-leaderboard');
        return stored ? JSON.parse(stored) : [];
    }
}

// Export for use in quiz engine
window.GitHubLeaderboard = GitHubLeaderboard;