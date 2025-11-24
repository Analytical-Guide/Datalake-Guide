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

START_MARKER = "<!-- QUIZ_LEADERBOARD_START -->"
END_MARKER = "<!-- QUIZ_LEADERBOARD_END -->"

def parse_score_from_comment(comment):
    """Parse quiz score from a comment object."""
    body = comment.body or ""
    score_match = re.search(r'QUIZ_SCORE:\s*(\d+)/10', body)
    name_match = re.search(r'NAME:\s*(.+)', body)
    time_match = re.search(r'TIME:\s*(.+)', body)

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
        score_data = parse_score_from_comment(comment)
        if score_data:
            score_data['comment_id'] = comment.id
            scores.append(score_data)

    # Sort by score (descending), then by time (ascending for same scores)
    scores.sort(key=lambda x: (-x['score'], x['time'] if x['time'] != 'N/A' else float('inf')))

    return scores[:50]  # Top 50 scores

def generate_leaderboard_markdown(scores):
    """Generate marked markdown section for the leaderboard."""
    if not scores:
        table = (
            "| Rank | Name | Score | Time | Date | User |\n"
            "|------|------|-------|------|------|------|\n"
            "| - | No scores yet | - | - | - | - |\n"
        )
    else:
        header = (
            "| Rank | Name | Score | Time | Date | User |\n"
            "|------|------|-------|------|------|------|\n"
        )
        rows = []
        for i, score in enumerate(scores, 1):
            date_str = datetime.fromisoformat(score['date']).strftime('%Y-%m-%d')
            row = f"| {i} | {score['name']} | {score['score']}/10 | {score['time']} | {date_str} | @{score['user']} |"
            rows.append(row)
        table = header + "\n".join(rows) + "\n"

    section = (
        f"{START_MARKER}\n"
        f"## Current Leaderboard\n\n"
        f"{table}"
        f"{END_MARKER}"
    )
    return section

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

        # Generate new leaderboard markdown section (with markers)
        leaderboard_section = generate_leaderboard_markdown(scores)

        # Update issue body using markers
        current_body = issue.body or ""
        if START_MARKER in current_body and END_MARKER in current_body:
            start_idx = current_body.index(START_MARKER)
            end_idx = current_body.index(END_MARKER) + len(END_MARKER)
            updated_body = current_body[:start_idx] + leaderboard_section + current_body[end_idx:]
        else:
            # Append section at the end if markers missing
            sep = "\n\n" if not current_body.endswith("\n") else "\n"
            updated_body = current_body + sep + leaderboard_section + "\n"

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