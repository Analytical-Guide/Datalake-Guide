"""
Stale Content Detection Script
Purpose: Automatically detect documentation that hasn't been updated recently
and create GitHub issues for review
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
from github import Github
from dateutil import parser as date_parser


# Configuration
STALE_THRESHOLD_MONTHS = 12
DIRECTORIES_TO_CHECK = ["docs/", "docs/tutorials/"]
STALE_LABEL = "stale-content"
ISSUE_TITLE_PREFIX = "[Stale Content] Review:"


def get_file_last_modified(filepath):
    """
    Get the last modification date of a file using Git history.
    
    Args:
        filepath: Path to the file
        
    Returns:
        datetime: Last modification date or None if error
    """
    try:
        # Get the last commit date for this file
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        
        date_str = result.stdout.strip()
        if date_str:
            return date_parser.parse(date_str)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting last modified date for {filepath}: {e}")
        return None


def find_stale_files(stale_threshold_date):
    """
    Find all markdown files that haven't been updated since the threshold date.
    
    Args:
        stale_threshold_date: datetime object representing the cutoff date
        
    Returns:
        list: List of tuples (filepath, last_modified_date)
    """
    stale_files = []
    
    for directory in DIRECTORIES_TO_CHECK:
        dir_path = Path(directory)
        
        # Skip if directory doesn't exist
        if not dir_path.exists():
            print(f"Directory {directory} does not exist, skipping...")
            continue
        
        # Find all markdown files
        for md_file in dir_path.rglob("*.md"):
            filepath = str(md_file)
            last_modified = get_file_last_modified(filepath)
            
            if last_modified is None:
                print(f"⚠️  Could not determine last modified date for {filepath}")
                continue
            
            if last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)
            else:
                last_modified = last_modified.astimezone(timezone.utc)
            
            if last_modified < stale_threshold_date:
                stale_files.append((filepath, last_modified))
                print(f"📅 Found stale file: {filepath} (last updated: {last_modified.date()})")
    
    return stale_files


def issue_exists(gh_repo, filepath):
    """
    Check if an issue already exists for this stale file.
    
    Args:
        gh_repo: GitHub repository object
        filepath: Path to the file
        
    Returns:
        bool: True if issue exists, False otherwise
    """
    issue_title = f"{ISSUE_TITLE_PREFIX} {filepath}"
    
    # Search for existing open issues with this title
    issues = gh_repo.get_issues(state="open", labels=[STALE_LABEL])
    
    for issue in issues:
        if issue.title == issue_title:
            print(f"  Issue already exists for {filepath} (#{issue.number})")
            return True
    
    return False


def get_last_committer(filepath):
    """
    Get the username of the last person who committed to this file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        str: GitHub username or None
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ae", "--", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        
        email = result.stdout.strip()
        if email:
            # Try to get GitHub username from email
            # This is a simplified approach - in production, you might want to maintain a mapping
            username = email.split("@")[0]
            return username
        return None
    except subprocess.CalledProcessError:
        return None


def create_stale_issue(gh_repo, filepath, last_modified):
    """
    Create a GitHub issue for stale content.
    
    Args:
        gh_repo: GitHub repository object
        filepath: Path to the stale file
        last_modified: datetime of last modification
    """
    issue_title = f"{ISSUE_TITLE_PREFIX} {filepath}"
    
    last_committer = get_last_committer(filepath)
    assignee_mention = f"@{last_committer}" if last_committer else "the maintainers"
    
    issue_body = f"""## 📅 Stale Content Detected

**File:** `{filepath}`  
**Last Updated:** {last_modified.strftime('%Y-%m-%d')} ({age_days} days ago)

### 🔍 What to Do

This file hasn't been updated in over {STALE_THRESHOLD_MONTHS} months. Please review and:

- [ ] **Update** the content if information is outdated
- [ ] **Verify** that all links and code examples still work
- [ ] **Add** any new best practices or features
- [ ] **Close** this issue if content is still accurate

### 📝 Notes

- If the content is still accurate, simply close this issue with a comment
- If major updates are needed, consider creating a separate PR
- Last contributor: {assignee_mention}

### 🤖 Automated Check

This issue was automatically created by the Stale Content Bot. Our knowledge base should stay current and relevant!

---

**Related:** #{filepath}
"""
    
    try:
        # Create the issue
        issue = gh_repo.create_issue(
            title=issue_title,
            body=issue_body,
            labels=[STALE_LABEL, "documentation"],
        )
        
        print(f"✅ Created issue #{issue.number} for {filepath}")
        
    except Exception as e:
        print(f"❌ Error creating issue for {filepath}: {e}")


def ensure_label_exists(gh_repo):
    """
    Ensure the stale-content label exists in the repository.
    
    Args:
        gh_repo: GitHub repository object
    """
    try:
        gh_repo.get_label(STALE_LABEL)
        print(f"✅ Label '{STALE_LABEL}' exists")
    except:
        # Create the label if it doesn't exist
        try:
            gh_repo.create_label(
                name=STALE_LABEL,
                color="FFA500",  # Orange color
                description="Content that hasn't been updated recently and needs review",
            )
            print(f"✅ Created label '{STALE_LABEL}'")
        except Exception as e:
            print(f"⚠️  Could not create label '{STALE_LABEL}': {e}")


def main():
    """
    Main function to find stale documentation and create issues.
    """
    print("=" * 60)
    print("🤖 Stale Content Bot")
    print("=" * 60)
    
    # Get GitHub token and repository from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("REPOSITORY")
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    if not repository:
        print("❌ REPOSITORY environment variable not set")
        sys.exit(1)
    
    # Initialize GitHub API
    gh = Github(github_token)
    gh_repo = gh.get_repo(repository)
    
    print(f"📦 Repository: {repository}")
    
    # Ensure label exists
    ensure_label_exists(gh_repo)
    
    # Calculate stale threshold date
    stale_threshold_date = datetime.now(timezone.utc) - timedelta(days=STALE_THRESHOLD_MONTHS * 30)
    print(f"📅 Stale threshold: {stale_threshold_date.date()} ({STALE_THRESHOLD_MONTHS} months)")
    
    # Find stale files
    print(f"\n🔍 Checking directories: {', '.join(DIRECTORIES_TO_CHECK)}")
    stale_files = find_stale_files(stale_threshold_date)
    
    if not stale_files:
        print("\n✅ No stale content found!")
        return
    
    print(f"\n📊 Found {len(stale_files)} stale file(s)")
    
    # Create issues for stale files
    print("\n📝 Creating issues...")
    created_count = 0
    skipped_count = 0
    
    for filepath, last_modified in stale_files:
        if issue_exists(gh_repo, filepath):
            skipped_count += 1
            continue
        
        create_stale_issue(gh_repo, filepath, last_modified)
        created_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Total stale files found: {len(stale_files)}")
    print(f"New issues created: {created_count}")
    print(f"Existing issues skipped: {skipped_count}")
    print("\n✅ Stale content check completed!")


if __name__ == "__main__":
    main()
    if last_modified.tzinfo is None:
        last_modified = last_modified.replace(tzinfo=timezone.utc)
    else:
        last_modified = last_modified.astimezone(timezone.utc)
    age_days = (datetime.now(timezone.utc) - last_modified).days
    
