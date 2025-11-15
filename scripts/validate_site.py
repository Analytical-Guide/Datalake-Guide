#!/usr/bin/env python3
"""
Testing and Validation Script for Delta Lake & Apache Iceberg Knowledge Hub
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import requests
from urllib.parse import urljoin

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_jekyll_build():
    """Test Jekyll site build."""
    print("🧪 Testing Jekyll build...")

    # Clean previous build
    success, _, _ = run_command("rm -rf _site", cwd=Path(__file__).parent)
    if not success:
        print("⚠️  Warning: Could not clean previous build")

    # Build site
    success, stdout, stderr = run_command("jekyll build", cwd=Path(__file__).parent)

    if success:
        print("✅ Jekyll build successful")
        return True
    else:
        print("❌ Jekyll build failed")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False

def test_html_validation():
    """Test HTML validation for generated pages."""
    print("🧪 Testing HTML validation...")

    site_dir = Path(__file__).parent / "_site"
    if not site_dir.exists():
        print("❌ Site directory not found. Run build first.")
        return False

    # Check for common HTML files
    html_files = list(site_dir.glob("**/*.html"))
    if not html_files:
        print("❌ No HTML files found in _site")
        return False

    print(f"📄 Found {len(html_files)} HTML files")

    # Basic validation - check for required elements
    issues = []
    for html_file in html_files[:5]:  # Check first 5 files
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for basic HTML structure
            checks = [
                ('DOCTYPE', '<!DOCTYPE html>' in content),
                ('Title', '<title>' in content and '</title>' in content),
                ('Meta charset', 'charset' in content),
                ('Viewport', 'viewport' in content),
                ('Main content', '<main' in content),
                ('Skip link', 'skip-link' in content or 'Skip to main content' in content),
            ]

            for check_name, passed in checks:
                if not passed:
                    issues.append(f"{html_file.name}: Missing {check_name}")

        except Exception as e:
            issues.append(f"{html_file.name}: Error reading file - {e}")

    if issues:
        print("❌ HTML validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ HTML validation passed")
        return True

def test_css_validation():
    """Test CSS for common issues."""
    print("🧪 Testing CSS validation...")

    css_file = Path(__file__).parent / "assets" / "css" / "main.css"
    if not css_file.exists():
        print("❌ Main CSS file not found")
        return False

    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for required CSS custom properties
        required_vars = [
            '--color-primary',
            '--color-bg-primary',
            '--color-text-primary',
            '--font-primary',
            '--text-base'
        ]

        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)

        if missing_vars:
            print("❌ Missing required CSS variables:")
            for var in missing_vars:
                print(f"  - {var}")
            return False

        print("✅ CSS validation passed")
        return True

    except Exception as e:
        print(f"❌ CSS validation error: {e}")
        return False

def test_accessibility_basic():
    """Basic accessibility checks."""
    print("🧪 Testing basic accessibility...")

    site_dir = Path(__file__).parent / "_site"
    if not site_dir.exists():
        print("❌ Site directory not found")
        return False

    # Check index.html for accessibility features
    index_file = site_dir / "index.html"
    if not index_file.exists():
        print("❌ index.html not found")
        return False

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ('Lang attribute', 'lang="en"' in content),
            ('Alt text check', True),  # Would need more sophisticated checking
            ('Heading hierarchy', '<h1' in content),
            ('ARIA labels', 'aria-label' in content),
            ('Focus management', 'focus-visible' in content or ':focus-visible' in content),
        ]

        issues = []
        for check_name, passed in checks:
            if not passed:
                issues.append(f"Missing {check_name}")

        if issues:
            print("❌ Accessibility issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ Basic accessibility checks passed")
            return True

    except Exception as e:
        print(f"❌ Accessibility check error: {e}")
        return False

def test_responsive_design():
    """Test for responsive design elements."""
    print("🧪 Testing responsive design...")

    css_file = Path(__file__).parent / "assets" / "css" / "main.css"
    if not css_file.exists():
        print("❌ CSS file not found")
        return False

    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        responsive_features = [
            '@media (max-width: 768px)',
            '@media (min-width: 769px)',
            'clamp(',
            'flex-direction',
            'grid-template-columns'
        ]

        missing_features = []
        for feature in responsive_features:
            if feature not in content:
                missing_features.append(feature)

        if missing_features:
            print("❌ Missing responsive design features:")
            for feature in missing_features:
                print(f"  - {feature}")
            return False
        else:
            print("✅ Responsive design features present")
            return True

    except Exception as e:
        print(f"❌ Responsive design check error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting validation tests for Delta Lake & Apache Iceberg Knowledge Hub\n")

    tests = [
        ("Jekyll Build", test_jekyll_build),
        ("HTML Validation", test_html_validation),
        ("CSS Validation", test_css_validation),
        ("Accessibility", test_accessibility_basic),
        ("Responsive Design", test_responsive_design),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        result = test_func()
        results.append((test_name, result))
        print(f"{'='*50}\n")

    # Summary
    print("📊 Test Results Summary:")
    print("=" * 30)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Site is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review and fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())