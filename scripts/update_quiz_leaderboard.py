#!/usr/bin/env python3
"""
Quiz Leaderboard Update Script
Updates the GitHub issue with the latest quiz scores from comments
"""

import os
import sys
import re
from datetime import datetime
from github import Github
from collections import defaultdict

def parse_score_from_comment(comment_body):
    """Parse quiz score from a comment body."""
    score_match = re.search(r'QUIZ_SCORE:\s*(\d+)/10', comment_body)
    name_match = re.search(r'NAME:\s*(.+)', comment_body)
    time_match = re.search(r'TIME:\s*(.+)', comment_body)

    if not score_match or not name_match:
        return None

    return {
        'name': name_match.group(1).strip(),
        'score': int(score_match.group(1)),
        'time': time_match.group(1).strip() if time_match else 'N/A',
        'date': comment.created_at.isoformat(),
        'user': comment.user.login
    }

def get_leaderboard_data(issue):
    """Extract all quiz scores from issue comments."""
    scores = []

    for comment in issue.get_comments():
        score_data = parse_score_from_comment(comment.body)
        if score_data:
            score_data['comment_id'] = comment.id
            scores.append(score_data)

    # Sort by score (descending), then by time (ascending for same scores)
    scores.sort(key=lambda x: (-x['score'], x['time'] if x['time'] != 'N/A' else float('inf')))

    return scores[:50]  # Top 50 scores

def generate_leaderboard_markdown(scores):
    """Generate markdown table for the leaderboard."""
    if not scores:
        return """
## Current Leaderboard

| Rank | Name | Score | Time | Date | User |
|------|------|-------|------|------|------|
| - | No scores yet | - | - | - | - |
"""

    header = """
## Current Leaderboard

| Rank | Name | Score | Time | Date | User |
|------|------|-------|------|------|------|
"""

    rows = []
    for i, score in enumerate(scores, 1):
        date_str = datetime.fromisoformat(score['date']).strftime('%Y-%m-%d')
        row = f"| {i} | {score['name']} | {score['score']}/10 | {score['time']} | {date_str} | @{score['user']} |"
        rows.append(row)

    return header + '\n'.join(rows) + '\n'

def update_leaderboard_issue():
    """Main function to update the leaderboard issue."""
    # Get environment variables
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('REPOSITORY', 'Analytical-Guide/Datalake-Guide')
    issue_number = os.getenv('ISSUE_NUMBER')

    if not token:
        print("❌ GITHUB_TOKEN not found")
        sys.exit(1)

    if not issue_number:
        print("❌ ISSUE_NUMBER not found")
        sys.exit(1)

    try:
        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(int(issue_number))

        print(f"📊 Updating leaderboard for issue #{issue_number}")

        # Get leaderboard data
        scores = get_leaderboard_data(issue)
        print(f"📈 Found {len(scores)} quiz scores")

        # Generate new leaderboard markdown
        leaderboard_md = generate_leaderboard_markdown(scores)

        # Update issue body
        current_body = issue.body
        # Replace the leaderboard section
        updated_body = re.sub(
            r'## Current Leaderboard.*?(?=\n##|\n###|\Z)',
            leaderboard_md.strip(),
            current_body,
            flags=re.DOTALL
        )

        if updated_body != current_body:
            issue.edit(body=updated_body)
            print("✅ Leaderboard updated successfully")
        else:
            print("ℹ️  No changes needed")

    except Exception as e:
        print(f"❌ Error updating leaderboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    update_leaderboard_issue()