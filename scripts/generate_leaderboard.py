"""
Leaderboard Generator Script
Purpose: Generate and inject a contributor leaderboard into README.md
"""

import json
from pathlib import Path
from datetime import datetime


CONTRIBUTORS_FILE = "community/contributors.json"
README_FILE = "README.md"
LEADERBOARD_START_MARKER = "<!-- LEADERBOARD_START -->"
LEADERBOARD_END_MARKER = "<!-- LEADERBOARD_END -->"
TOP_N_CONTRIBUTORS = 10


def load_contributors():
    """
    Load contributors data from JSON file.
    
    Returns:
        list: List of contributor dictionaries, sorted by points
    """
    contributors_path = Path(CONTRIBUTORS_FILE)
    
    if not contributors_path.exists():
        print(f"⚠️  {CONTRIBUTORS_FILE} not found, creating empty leaderboard")
        return []
    
    with open(contributors_path, "r") as f:
        contributors = json.load(f)
    
    # Sort by points descending
    contributors.sort(key=lambda x: x.get("points", 0), reverse=True)
    
    return contributors


def get_badge_emoji(rank):
    """
    Get emoji badge for ranking.
    
    Args:
        rank: Position in leaderboard (1-indexed)
        
    Returns:
        str: Emoji badge
    """
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return "🏅"


def generate_leaderboard_markdown(contributors):
    """
    Generate markdown table for the leaderboard.
    
    Args:
        contributors: List of contributor dictionaries
        
    Returns:
        str: Markdown formatted leaderboard
    """
    if not contributors:
        return "*No contributors yet. Be the first to contribute!*\n"
    
    # Take top N contributors
    top_contributors = contributors[:TOP_N_CONTRIBUTORS]
    
    lines = [
        "### 🏆 Top Contributors",
        "",
        "Thank you to our amazing community members who make this knowledge hub possible!",
        "",
        "| Rank | Contributor | Points | PRs | Reviews | Issues |",
        "|------|-------------|--------|-----|---------|--------|",
    ]
    
    for i, contributor in enumerate(top_contributors, 1):
        username = contributor.get("username", "Unknown")
        points = contributor.get("points", 0)
        contributions = contributor.get("contributions", {})
        
        prs = contributions.get("prs_merged", 0)
        reviews = contributions.get("reviews", 0)
        issues = contributions.get("issues_closed", 0)
        
        badge = get_badge_emoji(i)
        
        line = f"| {badge} #{i} | [@{username}](https://github.com/{username}) | **{points}** | {prs} | {reviews} | {issues} |"
        lines.append(line)
    
    lines.extend([
        "",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "**Want to see your name here?** Check out our [Contributing Guide](CONTRIBUTING.md) to get started!",
        "",
    ])
    
    return "\n".join(lines)


def update_readme_leaderboard(leaderboard_markdown):
    """
    Update the README.md file with the new leaderboard.
    
    Args:
        leaderboard_markdown: Markdown content for the leaderboard
    """
    readme_path = Path(README_FILE)
    
    if not readme_path.exists():
        print(f"❌ {README_FILE} not found")
        return False
    
    with open(readme_path, "r") as f:
        content = f.read()
    
    # Check if markers exist
    if LEADERBOARD_START_MARKER not in content or LEADERBOARD_END_MARKER not in content:
        print(f"❌ Leaderboard markers not found in {README_FILE}")
        print(f"   Please add {LEADERBOARD_START_MARKER} and {LEADERBOARD_END_MARKER}")
        return False
    
    # Find marker positions
    start_pos = content.find(LEADERBOARD_START_MARKER)
    end_pos = content.find(LEADERBOARD_END_MARKER)
    
    if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
        print(f"❌ Invalid marker positions in {README_FILE}")
        return False
    
    # Construct new content
    start_pos += len(LEADERBOARD_START_MARKER)
    new_content = (
        content[:start_pos] + "\n" + leaderboard_markdown + content[end_pos:]
    )
    
    # Write updated content
    with open(readme_path, "w") as f:
        f.write(new_content)
    
    print(f"✅ Updated leaderboard in {README_FILE}")
    return True


def generate_contributor_badges(contributors):
    """
    Generate achievement badges for contributors.
    
    Args:
        contributors: List of contributor dictionaries
        
    Returns:
        dict: Mapping of username to list of badges
    """
    badges = {}
    
    for contributor in contributors:
        username = contributor.get("username")
        points = contributor.get("points", 0)
        contributions = contributor.get("contributions", {})
        prs = contributions.get("prs_merged", 0)
        
        user_badges = []
        
        # Points-based badges
        if points >= 1000:
            user_badges.append("🌟 Legend")
        elif points >= 500:
            user_badges.append("💎 Diamond")
        elif points >= 250:
            user_badges.append("🏆 Champion")
        elif points >= 100:
            user_badges.append("⭐ Expert")
        elif points >= 50:
            user_badges.append("🔰 Contributor")
        
        # Activity-based badges
        if prs >= 50:
            user_badges.append("📝 Prolific Author")
        elif prs >= 10:
            user_badges.append("✍️ Active Writer")
        
        if contributions.get("reviews", 0) >= 25:
            user_badges.append("👀 Code Guardian")
        
        badges[username] = user_badges
    
    return badges


def main():
    """
    Main function to generate and update the leaderboard.
    """
    print("=" * 60)
    print("🏆 Leaderboard Generator")
    print("=" * 60)
    
    # Load contributors
    print(f"📊 Loading contributors from {CONTRIBUTORS_FILE}...")
    contributors = load_contributors()
    
    if not contributors:
        print("⚠️  No contributors found")
        leaderboard_markdown = "*No contributors yet. Be the first to contribute!*\n"
    else:
        print(f"✅ Found {len(contributors)} contributor(s)")
        
        # Display top 5 in console
        print("\n🏆 Top 5 Contributors:")
        for i, contributor in enumerate(contributors[:5], 1):
            username = contributor.get("username", "Unknown")
            points = contributor.get("points", 0)
            print(f"  {i}. @{username}: {points} points")
        
        # Generate leaderboard markdown
        print(f"\n📝 Generating leaderboard markdown...")
        leaderboard_markdown = generate_leaderboard_markdown(contributors)
    
    # Update README
    print(f"\n📄 Updating {README_FILE}...")
    success = update_readme_leaderboard(leaderboard_markdown)
    
    if success:
        print("\n✅ Leaderboard generation completed successfully!")
    else:
        print("\n❌ Leaderboard generation failed!")
        exit(1)


if __name__ == "__main__":
    main()
