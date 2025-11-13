"""
Contributor Statistics Update Script
Purpose: Track and gamify community contributions with a points system
"""

import os
import json
import sys
from pathlib import Path
from github import Github


# Points configuration
POINTS_MAP = {
    "PR_MERGED_LARGE": 50,      # >500 lines changed
    "PR_MERGED_MEDIUM": 25,     # 100-500 lines changed
    "PR_MERGED_SMALL": 10,      # <100 lines changed
    "REVIEW_APPROVED": 5,       # Approved a PR
    "REVIEW_CHANGES_REQUESTED": 3,  # Requested changes (helpful)
    "ISSUE_CLOSED": 3,          # Closed an issue
    "DISCUSSION_COMMENT": 1,    # Participated in discussion
}

CONTRIBUTORS_FILE = "community/contributors.json"


def ensure_contributors_file():
    """Ensure the contributors.json file and directory exist."""
    contributors_path = Path(CONTRIBUTORS_FILE)
    contributors_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not contributors_path.exists():
        with open(contributors_path, "w") as f:
            json.dump([], f, indent=2)
        print(f"✅ Created {CONTRIBUTORS_FILE}")


def load_contributors():
    """
    Load the contributors data from JSON file.
    
    Returns:
        list: List of contributor dictionaries
    """
    ensure_contributors_file()
    
    with open(CONTRIBUTORS_FILE, "r") as f:
        return json.load(f)


def save_contributors(contributors):
    """
    Save the contributors data to JSON file.
    
    Args:
        contributors: List of contributor dictionaries
    """
    # Sort by points descending
    contributors.sort(key=lambda x: x.get("points", 0), reverse=True)
    
    with open(CONTRIBUTORS_FILE, "w") as f:
        json.dump(contributors, f, indent=2)
    
    print(f"✅ Saved contributor statistics to {CONTRIBUTORS_FILE}")


def find_contributor(contributors, username):
    """
    Find a contributor by username.
    
    Args:
        contributors: List of contributor dictionaries
        username: GitHub username
        
    Returns:
        dict or None: Contributor dictionary if found
    """
    for contributor in contributors:
        if contributor["username"] == username:
            return contributor
    return None


def parse_github_event(event_name, event_payload):
    """
    Parse GitHub event payload to extract contribution information.
    
    Args:
        event_name: Name of the GitHub event
        event_payload: Event payload as string
        
    Returns:
        tuple: (username, contribution_type, metadata)
    """
    try:
        event_data = json.loads(event_payload)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse event payload")
        return None, None, {}
    
    username = None
    contribution_type = None
    metadata = {}
    
    if event_name == "pull_request":
        pr = event_data.get("pull_request", {})
        username = pr.get("user", {}).get("login")
        
        if pr.get("merged", False):
            # Determine PR size based on changes
            additions = pr.get("additions", 0)
            deletions = pr.get("deletions", 0)
            total_changes = additions + deletions
            
            if total_changes > 500:
                contribution_type = "PR_MERGED_LARGE"
            elif total_changes > 100:
                contribution_type = "PR_MERGED_MEDIUM"
            else:
                contribution_type = "PR_MERGED_SMALL"
            
            metadata = {
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title"),
                "additions": additions,
                "deletions": deletions,
            }
    
    elif event_name == "pull_request_review":
        review = event_data.get("review", {})
        username = review.get("user", {}).get("login")
        state = review.get("state", "").lower()
        
        if state == "approved":
            contribution_type = "REVIEW_APPROVED"
        elif state == "changes_requested":
            contribution_type = "REVIEW_CHANGES_REQUESTED"
        
        metadata = {
            "pr_number": event_data.get("pull_request", {}).get("number"),
            "review_state": state,
        }
    
    elif event_name == "issues":
        issue = event_data.get("issue", {})
        username = issue.get("user", {}).get("login")
        
        if event_data.get("action") == "closed":
            contribution_type = "ISSUE_CLOSED"
            metadata = {
                "issue_number": issue.get("number"),
                "issue_title": issue.get("title"),
            }
    
    elif event_name == "discussion_comment":
        comment = event_data.get("comment", {})
        username = comment.get("user", {}).get("login")
        contribution_type = "DISCUSSION_COMMENT"
        metadata = {
            "comment_id": comment.get("id"),
        }
    
    return username, contribution_type, metadata


def calculate_points(contribution_type):
    """
    Calculate points for a contribution type.
    
    Args:
        contribution_type: Type of contribution
        
    Returns:
        int: Points awarded
    """
    return POINTS_MAP.get(contribution_type, 0)


def update_stats(contributors, username, points, contribution_type, metadata):
    """
    Update statistics for a contributor.
    
    Args:
        contributors: List of contributor dictionaries
        username: GitHub username
        points: Points to award
        contribution_type: Type of contribution
        metadata: Additional metadata about the contribution
    """
    contributor = find_contributor(contributors, username)
    
    if contributor is None:
        # New contributor
        contributor = {
            "username": username,
            "points": 0,
            "contributions": {
                "prs_merged": 0,
                "reviews": 0,
                "issues_closed": 0,
                "discussions": 0,
            },
            "recent_activity": [],
        }
        contributors.append(contributor)
    
    # Update points
    contributor["points"] += points
    
    # Update contribution counts
    if contribution_type.startswith("PR_MERGED"):
        contributor["contributions"]["prs_merged"] += 1
    elif contribution_type.startswith("REVIEW"):
        contributor["contributions"]["reviews"] += 1
    elif contribution_type == "ISSUE_CLOSED":
        contributor["contributions"]["issues_closed"] += 1
    elif contribution_type == "DISCUSSION_COMMENT":
        contributor["contributions"]["discussions"] += 1
    
    # Add to recent activity (keep last 10)
    activity = {
        "type": contribution_type,
        "points": points,
        "timestamp": metadata.get("timestamp", ""),
    }
    
    if "pr_number" in metadata:
        activity["pr_number"] = metadata["pr_number"]
    if "issue_number" in metadata:
        activity["issue_number"] = metadata["issue_number"]
    
    contributor["recent_activity"].insert(0, activity)
    contributor["recent_activity"] = contributor["recent_activity"][:10]
    
    print(f"✅ Updated stats for @{username}: +{points} points ({contribution_type})")


def main():
    """
    Main function to update contributor statistics.
    """
    print("=" * 60)
    print("🎮 Gamification Engine")
    print("=" * 60)
    
    # Get environment variables
    github_token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("REPOSITORY")
    event_name = os.environ.get("EVENT_NAME")
    event_payload = os.environ.get("EVENT_PAYLOAD")
    
    if not all([github_token, repository, event_name, event_payload]):
        print("❌ Required environment variables not set")
        sys.exit(1)
    
    print(f"📦 Repository: {repository}")
    print(f"🎯 Event: {event_name}")
    
    # Parse the event
    username, contribution_type, metadata = parse_github_event(event_name, event_payload)
    
    if not username or not contribution_type:
        print("⚠️  No actionable contribution detected")
        return
    
    print(f"👤 Contributor: @{username}")
    print(f"📝 Contribution Type: {contribution_type}")
    
    # Calculate points
    points = calculate_points(contribution_type)
    print(f"🏆 Points Awarded: {points}")
    
    # Load current contributors
    contributors = load_contributors()
    print(f"📊 Current contributors: {len(contributors)}")
    
    # Update statistics
    update_stats(contributors, username, points, contribution_type, metadata)
    
    # Save updated statistics
    save_contributors(contributors)
    
    # Display top contributors
    print("\n🏆 Top 5 Contributors:")
    for i, contributor in enumerate(contributors[:5], 1):
        print(f"  {i}. @{contributor['username']}: {contributor['points']} points")
    
    print("\n✅ Contributor statistics updated successfully!")


if __name__ == "__main__":
    main()
