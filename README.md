# 🌊 Delta Lake & Apache Iceberg Knowledge Hub

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor%20Covenant-purple.svg)](CODE_OF_CONDUCT.md)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.x-00ADD8?logo=databricks)](https://delta.io/)
[![Apache Iceberg](https://img.shields.io/badge/Apache%20Iceberg-1.5+-306998?logo=apache)](https://iceberg.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/features/actions)
[![GitHub Pages](https://img.shields.io/badge/Site-GitHub%20Pages-222222?logo=github)](https://analytical-guide.github.io/Datalake-Guide/)

> **The definitive, community-driven reference for modern data lakehouse engineering** — comparing Delta Lake and Apache Iceberg with production-tested recipes, automated freshness tracking, and weekly AI-powered content discovery.

---

## 🌐 Live Knowledge Hub

Explore the full site at **[analytical-guide.github.io/Datalake-Guide](https://analytical-guide.github.io/Datalake-Guide/)** — searchable documentation, tutorials, and curated resources, automatically kept up to date.

---

## 🎯 What Is This?

Choosing between Delta Lake and Apache Iceberg—or deciding how to deploy either in production—is non-trivial. This hub solves that by providing:

| Need | What You'll Find |
|------|-----------------|
| **Understand the differences** | [Feature comparison matrix](docs/comparisons/feature-matrix.md) with 60+ criteria across 10 dimensions |
| **Get hands-on quickly** | [CI/CD-validated code recipes](code-recipes/) for common workloads |
| **Move to production** | [Production readiness guide](docs/best-practices/production-readiness.md) with advanced compaction, monitoring, and DR patterns |
| **Migrate existing systems** | [Step-by-step migration guide](docs/tutorials/migration-guide.md) covering Parquet, Hive, and cross-cloud scenarios |
| **Stay current** | Weekly automated discovery of new articles and blog posts from trusted sources |

---

## 📁 Repository Structure

```
Datalake-Guide/
├── docs/
│   ├── comparisons/feature-matrix.md   ← Delta vs Iceberg (60+ features)
│   ├── tutorials/getting-started.md    ← Quickstart for both formats
│   ├── tutorials/migration-guide.md    ← Parquet → Delta/Iceberg migration
│   ├── best-practices/production-readiness.md ← Production checklist
│   ├── architecture/system-overview.md ← Hub automation architecture
│   └── awesome-list.md                 ← Curated resources (auto-updated)
├── code-recipes/examples/              ← Runnable, validated code recipes
├── community/                          ← Contributor stats & processed URLs
├── scripts/                            ← Automation scripts
└── .github/workflows/                  ← 8 automated GitHub Actions
```

### Core Content

| Section | Location | Description |
|---------|----------|-------------|
| **Feature Matrix** | [`docs/comparisons/feature-matrix.md`](docs/comparisons/feature-matrix.md) | 60+ feature comparison across 10 dimensions |
| **Code Recipes** | [`code-recipes/`](code-recipes/) | CI-validated, production-ready examples |
| **Getting Started** | [`docs/tutorials/getting-started.md`](docs/tutorials/getting-started.md) | Hands-on quickstart for both technologies |
| **Migration Guide** | [`docs/tutorials/migration-guide.md`](docs/tutorials/migration-guide.md) | Parquet, Hive → Delta/Iceberg with validation scripts |
| **Production Readiness** | [`docs/best-practices/production-readiness.md`](docs/best-practices/production-readiness.md) | Advanced patterns for production deployments |
| **Architecture** | [`docs/architecture/system-overview.md`](docs/architecture/system-overview.md) | Hub automation and workflow architecture |
| **Awesome List** | [`docs/awesome-list.md`](docs/awesome-list.md) | Curated resources, updated weekly by AI aggregator |
| **Knowledge Quiz** | [`quiz.md`](quiz.md) | Test and track your knowledge |

## 📚 Quick Links

- [🔍 **Feature Comparison Matrix**](docs/comparisons/feature-matrix.md) — 60+ criteria, benchmarks, and decision framework
- [👨‍💻 **Code Recipes**](code-recipes/) — Production-ready examples with CI validation
- [📖 **Getting Started**](docs/tutorials/getting-started.md) — First Delta/Iceberg table in minutes
- [🚀 **Migration Guide**](docs/tutorials/migration-guide.md) — Parquet/Hive → modern format
- [🏗️ **Production Readiness**](docs/best-practices/production-readiness.md) — Best practices for production
- [🤝 **Contributing Guide**](CONTRIBUTING.md) — Earn points, join the community
- [📜 **Code of Conduct**](CODE_OF_CONDUCT.md) — Community standards
- [🏆 **Community Leaderboard**](#-community-leaderboard) — Top contributors

## 💡 The "Living Whitepaper" Philosophy

Unlike traditional static documentation, this repository is designed as a **living knowledge base** that continuously evolves through automation:

| Automation | Trigger | What It Does |
|-----------|---------|-------------|
| **Code Recipe CI** | Every PR | Lints Python, runs `validate.sh` per recipe |
| **Documentation CI** | Every PR | Markdownlint, link checker, Mermaid diagram validation |
| **Stale Content Bot** | Weekly (Mon) | Opens issues for docs untouched > 12 months |
| **Resource Aggregator** | Weekly (Sun) | Discovers new articles from RSS feeds, commits to awesome list |
| **Leaderboard Update** | Daily | Regenerates top-10 contributor table in README |
| **Gamification Engine** | PR/Review/Issue | Awards points and updates contributor stats |
| **Quiz Leaderboard** | Issue comment | Updates quiz scores in the leaderboard issue |

All architecture diagrams use **Mermaid.js** so every diagram is version-controlled and diffable alongside the content it describes.

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Data Formats** | Delta Lake 3.x, Apache Iceberg 1.5+ |
| **Languages** | Python 3.8+, SQL, Scala |
| **Automation** | GitHub Actions (8 workflows) |
| **Documentation** | Markdown, Mermaid.js, Jekyll |
| **Code Quality** | black, flake8, markdownlint, typos |
| **Link Health** | lychee link checker |
| **Content Discovery** | feedparser, BeautifulSoup, optional LLM APIs |

## 🚀 How to Use This Material

### 👩‍🎓 For Learners

| Step | Goal | Resource |
|------|------|----------|
| 1 | Compare technologies | [Feature Matrix](docs/comparisons/feature-matrix.md) |
| 2 | Set up your environment | [Getting Started Tutorial](docs/tutorials/getting-started.md) |
| 3 | Try runnable examples | [Code Recipes](code-recipes/examples/) |
| 4 | Move to production | [Production Readiness Guide](docs/best-practices/production-readiness.md) |
| 5 | Migrate existing systems | [Migration Guide](docs/tutorials/migration-guide.md) |
| 6 | Test your knowledge | [Knowledge Quiz](quiz.md) |

### 👩‍💻 For Contributors

1. Read our [Contributing Guide](CONTRIBUTING.md) — contributions earn points on the leaderboard
2. Check [open issues](https://github.com/Analytical-Guide/Datalake-Guide/issues) for areas needing help
3. Review the [Code of Conduct](CODE_OF_CONDUCT.md)
4. Submit your first pull request — the gamification engine awards points automatically!

## 🛠️ Development & Deployment

### Prerequisites

- **Ruby**: 2.7+ (for Jekyll)
- **Python**: 3.8+ (for scripts and validation)
- **Node.js**: 16+ (optional, for additional tooling)
- **Git**: Latest version

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Analytical-Guide/Datalake-Guide.git
   cd Datalake-Guide
   ```

2. **Install Jekyll and dependencies**
   ```bash
   # Install Bundler if not already installed
   gem install bundler

   # Install project dependencies
   bundle install
   ```

3. **Install Python dependencies** (for validation scripts)
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Start local development server**
   ```bash
   # Serve with live reload
   bundle exec jekyll serve --livereload

   # Or build and serve
   bundle exec jekyll build && bundle exec jekyll serve
   ```

5. **Open your browser**
   - Navigate to `http://localhost:4000/Datalake-Guide/`
   - The site will automatically reload when you make changes

### Development Workflow

#### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Edit Markdown files in `docs/`, `code-recipes/`, etc.
   - Update styles in `assets/css/main.css`
   - Modify scripts in `scripts/`

3. **Test your changes**
   ```bash
   # Run validation tests
   python scripts/validate_site.py

   # Check for broken links
   python scripts/check_internal_links.py

   # Build the site
   bundle exec jekyll build
   ```

4. **Preview changes locally**
   ```bash
   bundle exec jekyll serve
   ```

#### Code Quality

- **Markdown**: Follow the style guide in `CONTRIBUTING.md`
- **CSS**: Use the established design system (see [Design System Documentation](docs/design-system.md))
- **JavaScript**: Follow modern ES6+ standards with accessibility in mind
- **Python**: Use Black for formatting, follow PEP 8

### Automated Testing

Run the comprehensive test suite:

```bash
# Run all validation tests
python scripts/validate_site.py

# Check internal links
python scripts/check_internal_links.py

# Validate code recipes
find code-recipes -name "validate.sh" -exec bash {} \;
```

### Deployment

#### GitHub Pages (Automatic)

The site is automatically deployed to GitHub Pages via GitHub Actions:

1. **Push to main branch**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **GitHub Actions will:**
   - Build the Jekyll site
   - Run validation tests
   - Deploy to GitHub Pages
   - Report any failures

#### Manual Deployment

For manual deployment or custom environments:

```bash
# Build for production
JEKYLL_ENV=production bundle exec jekyll build

# Deploy to custom server
rsync -avz _site/ user@server:/path/to/site/
```

### Environment Configuration

#### Jekyll Configuration

Key settings in `_config.yml`:
- `url`: Site URL for absolute links
- `baseurl`: Subpath for GitHub Pages
- `repository`: GitHub repository for links
- `plugins`: Enabled Jekyll plugins

#### Custom Variables

Available in `_config.yml`:
- `github_url`: Full GitHub repository URL
- `issues_url`: Issues page URL
- `discussions_url`: Discussions page URL

### Troubleshooting

#### Common Issues

1. **Jekyll build fails**
   ```bash
   # Clear Jekyll cache
   rm -rf .jekyll-cache _site

   # Reinstall dependencies
   bundle install

   # Try building again
   bundle exec jekyll build
   ```

2. **Python scripts fail**
   ```bash
   # Ensure Python 3.8+
   python --version

   # Install/update dependencies
   pip install -r requirements-dev.txt
   ```

3. **Links are broken**
   ```bash
   # Run link checker
   python scripts/check_internal_links.py

   # Fix any reported issues
   ```

4. **Styling issues**
   - Check browser developer tools for CSS errors
   - Ensure design system variables are used correctly
   - Test responsive design across breakpoints

#### Getting Help

- **Issues**: [Report bugs](https://github.com/Analytical-Guide/Datalake-Guide/issues)
- **Discussions**: [Ask questions](https://github.com/Analytical-Guide/Datalake-Guide/discussions)
- **Documentation**: Check [local development docs](docs/local-development.md)

### Performance Monitoring

The site includes performance optimizations:

- **Font loading**: Optimized with `font-display: swap`
- **CSS**: Minified and optimized
- **Images**: Lazy loading support
- **JavaScript**: Progressive enhancement

Monitor performance using:
- **Lighthouse**: Browser dev tools
- **WebPageTest**: External performance testing
- **GitHub Actions**: Automated performance checks

## 🏆 Community Leaderboard

<!-- LEADERBOARD_START -->
### 🏆 Top Contributors

Thank you to our amazing community members who make this knowledge hub possible!

| Rank | Contributor | Points | PRs | Reviews | Issues |
|------|-------------|--------|-----|---------|--------|
| 🥇 #1 | [@Copilot](https://github.com/Copilot) | **75** | 2 | 0 | 0 |
| 🥈 #2 | [@moshesham](https://github.com/moshesham) | **13** | 1 | 0 | 1 |

*Last updated: 2026-04-30 13:26 UTC*

**Want to see your name here?** Check out our [Contributing Guide](CONTRIBUTING.md) to get started!
<!-- LEADERBOARD_END -->

## 📈 Repository Stats

![GitHub stars](https://img.shields.io/github/stars/Analytical-Guide/Datalake-Guide?style=social)
![GitHub forks](https://img.shields.io/github/forks/Analytical-Guide/Datalake-Guide?style=social)
![GitHub contributors](https://img.shields.io/github/contributors/Analytical-Guide/Datalake-Guide)
![GitHub last commit](https://img.shields.io/github/last-commit/Analytical-Guide/Datalake-Guide)

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Community & Support

- **Issues**: [Report bugs or request features](https://github.com/Analytical-Guide/Datalake-Guide/issues)
- **Discussions**: [Join community discussions](https://github.com/Analytical-Guide/Datalake-Guide/discussions)
- **Pull Requests**: [Contribute code or documentation](https://github.com/Analytical-Guide/Datalake-Guide/pulls)

## 🙏 Acknowledgments

This knowledge hub is made possible by our amazing community of contributors. Thank you to everyone who has helped make this resource valuable for data engineers worldwide!

---

**Built with ❤️ by the data engineering community**
