# 🌊 Delta Lake & Apache Iceberg Knowledge Hub

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor%20Covenant-purple.svg)](CODE_OF_CONDUCT.md)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-Latest-00ADD8?logo=databricks)](https://delta.io/)
[![Apache Iceberg](https://img.shields.io/badge/Apache%20Iceberg-Latest-306998?logo=apache)](https://iceberg.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/features/actions)

## 🌐 GitHub Pages

The GitHub Pages for this repository is available at: **[Delta Lake & Apache Iceberg Knowledge Hub](https://analytical-guide.github.io/Datalake-Guide/)**

## 🎯 Vision Statement

**Building the definitive, community-driven knowledge ecosystem for modern data lakehouse technologies.** This repository serves as a living, breathing whitepaper that evolves with the data engineering landscape, combining comprehensive technical comparisons, battle-tested code recipes, and AI-powered content curation to empower data engineers worldwide to make informed architectural decisions and implement best practices for Delta Lake and Apache Iceberg.

## 📁 Repository Content and Structure

This repository is organized into the following sections:

### Core Content

| Section | Location | Description |
|---------|----------|-------------|
| **Feature Matrix** | [`docs/comparisons/feature-matrix.md`](docs/comparisons/feature-matrix.md) | Comprehensive comparison of Delta Lake vs Apache Iceberg |
| **Code Recipes** | [`code-recipes/`](code-recipes/) | Production-ready code examples with validation |
| **Tutorials** | [`docs/tutorials/`](docs/tutorials/) | Step-by-step guides for common use cases |
| **Architecture** | [`docs/architecture/`](docs/architecture/) | Reference architectures and design patterns |
| **Best Practices** | [`docs/best-practices/`](docs/best-practices/) | Industry-tested patterns and recommendations |

### Learning Resources

| Resource | Location | Description |
|----------|----------|-------------|
| **Getting Started** | [`docs/tutorials/getting-started.md`](docs/tutorials/getting-started.md) | Quick start guide for beginners |
| **Migration Guide** | [`docs/tutorials/migration-guide.md`](docs/tutorials/migration-guide.md) | Moving from legacy systems |
| **Knowledge Quiz** | [`quiz/`](quiz/) | Test your Delta Lake & Iceberg knowledge |
| **Design System** | [`docs/design-system.md`](docs/design-system.md) | UI/UX guidelines for the project |

## 📚 Quick Links

- [🔍 **Feature Comparison Matrix**](docs/comparisons/feature-matrix.md) - Detailed side-by-side comparison of Delta Lake vs Apache Iceberg
- [👨‍💻 **Code Recipes**](code-recipes/) - Production-ready code examples with validation
- [🧠 **Knowledge Quiz**](quiz/) - Test your Delta Lake & Iceberg knowledge
- [📖 **Tutorials**](docs/tutorials/) - Step-by-step guides for common use cases
- [🏗️ **Architecture Patterns**](docs/architecture/) - Reference architectures and design patterns
- [🤝 **Contributing Guide**](CONTRIBUTING.md) - Join our community and contribute
- [📜 **Code of Conduct**](CODE_OF_CONDUCT.md) - Our community standards
- [🏆 **Community Leaderboard**](#-community-leaderboard) - Top contributors

## 💡 The "Living Whitepaper" Philosophy

Unlike traditional static documentation, this repository is designed as a **living knowledge base** that continuously evolves:

- **🤖 Automated Freshness**: GitHub Actions workflows automatically detect stale content and create issues to keep documentation current
- **✅ Validated Content**: Every code recipe is automatically tested in CI/CD to ensure it works with the latest versions
- **🔗 Link Health**: Automated link checking prevents documentation rot
- **📊 Community-Driven**: Contributions are gamified with a points system, encouraging diverse perspectives
- **🧠 AI-Enhanced**: Machine learning assists in discovering, summarizing, and curating relevant content from across the web
- **🎨 Diagrams as Code**: All architecture diagrams use Mermaid.js for version control and easy collaboration

## 🛠️ Tech Stack

This knowledge hub leverages cutting-edge technologies:

- **📊 Data Formats**: Delta Lake, Apache Iceberg
- **💻 Languages**: Python, SQL, Scala
- **🔄 Orchestration**: GitHub Actions, Python automation scripts
- **📝 Documentation**: Markdown, Mermaid.js
- **🧪 Testing**: pytest, shell scripts
- **🎨 Code Quality**: black, flake8, markdownlint
- **🔍 Content Discovery**: BeautifulSoup, feedparser, LLM APIs

## 🎯 What You'll Find Here

### 📊 Comprehensive Comparisons

Our [feature comparison matrix](docs/comparisons/feature-matrix.md) provides an unbiased, detailed analysis of:
- Time Travel and Version Control
- Schema Evolution Strategies
- Partitioning and Clustering
- Compaction and Optimization
- Concurrency Control Mechanisms
- Query Performance Characteristics
- Ecosystem Integration

### 💻 Battle-Tested Code Recipes

Every recipe in our [code-recipes](code-recipes/) directory follows a standardized structure:
- **Problem Definition**: Clear use case description
- **Solution**: Fully commented, production-ready code
- **Dependencies**: Reproducible environment specifications
- **Validation**: Automated tests to verify functionality

### 🎓 Learning Resources

- **Tutorials**: Hands-on guides for common scenarios
- **Best Practices**: Industry-tested patterns and anti-patterns
- **Architecture Guides**: Reference implementations for various scales

## 🚀 How to Use This Material

1. **Start with the Feature Comparison**: Begin by reading the [Feature Comparison Matrix](docs/comparisons/feature-matrix.md) for a comprehensive overview of Delta Lake vs Apache Iceberg.

2. **Explore the Getting Started Guide**: Use the [Getting Started Tutorial](docs/tutorials/getting-started.md) to set up your first lakehouse.

3. **Review Code Recipes**: Work through the [Code Recipes](code-recipes/) for hands-on implementation examples.

4. **Follow Best Practices**: Study the [Best Practices](docs/best-practices/) for production-ready implementations.

5. **Test Your Knowledge**: Take the [Knowledge Quiz](quiz/) to validate your understanding.

6. **Visit the Website**: Explore the full content at [GitHub Pages](https://analytical-guide.github.io/Datalake-Guide/).

## 🚀 Getting Started

### For Learners

1. Browse the [feature comparison matrix](docs/comparisons/feature-matrix.md) to understand the differences
2. Explore [code recipes](code-recipes/) for your specific use case
3. Follow [tutorials](docs/tutorials/) for step-by-step implementations

### For Contributors

1. Read our [Contributing Guide](CONTRIBUTING.md)
2. Check [open issues](https://github.com/Analytical-Guide/Datalake-Guide/issues) for areas needing help
3. Review the [Code of Conduct](CODE_OF_CONDUCT.md)
4. Submit your first pull request!

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
