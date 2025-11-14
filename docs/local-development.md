# Local Development

This guide explains how to set up and run the Jekyll site locally for development and testing.

## Prerequisites

### Option 1: Install Jekyll (Recommended)

1. **Install Ruby** (version 2.5.0 or higher):
   - Windows: Download from [rubyinstaller.org](https://rubyinstaller.org/)
   - macOS: `brew install ruby`
   - Linux: `sudo apt-get install ruby-full`

2. **Install Jekyll and Bundler**:
   ```bash
   gem install jekyll bundler
   ```

3. **Install dependencies** (if Gemfile exists):
   ```bash
   bundle install
   ```

### Option 2: Use GitHub Codespaces

If you have access to GitHub Codespaces, the environment comes pre-configured with Jekyll.

## Running the Site

### Method 1: Jekyll Serve (Recommended)

```bash
# Navigate to the repository root
cd /path/to/Datalake-Guide

# Serve the site locally
jekyll serve

# Or with live reload
jekyll serve --livereload
```

The site will be available at `http://localhost:4000/Datalake-Guide/`

### Method 2: Simple HTTP Server (Fallback)

If Jekyll is not available, you can serve the static files directly:

**Windows PowerShell:**
```powershell
# Navigate to the repository root
cd "C:\path\to\Datalake-Guide"

# Start a simple HTTP server (Python 3)
python -m http.server 8000

# Or if Python is not available, use Node.js
npx http-server -p 8000
```

**macOS/Linux:**
```bash
# Navigate to the repository root
cd /path/to/Datalake-Guide

# Start a simple HTTP server (Python 3)
python3 -m http.server 8000

# Or if Python is not available, use Node.js
npx http-server -p 8000
```

The site will be available at `http://localhost:8000`

## Development Workflow

1. **Make changes** to Markdown files, layouts, or assets
2. **Test locally** using one of the methods above
3. **Commit and push** changes to trigger GitHub Pages deployment
4. **Verify deployment** at the GitHub Pages URL

## File Structure

```
Datalake-Guide/
├── _config.yml          # Jekyll configuration
├── _layouts/            # HTML layouts
│   └── default.html     # Main layout template
├── assets/              # Static assets (CSS, JS, images)
├── docs/                # Documentation pages
├── code-recipes/        # Code examples
├── index.md             # Homepage
└── _site/               # Generated site (created by Jekyll)
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Find process using port 4000
   lsof -ti:4000 | xargs kill -9
   ```

2. **Permission errors**:
   ```bash
   # On macOS/Linux, you might need to use sudo for gem install
   sudo gem install jekyll bundler
   ```

3. **Ruby version issues**:
   ```bash
   # Check Ruby version
   ruby --version
   # Should be 2.5.0 or higher
   ```

### Build Issues

If the site fails to build:

1. Check `_config.yml` for syntax errors
2. Ensure all referenced files exist
3. Check for invalid Liquid syntax in templates
4. Verify front matter in Markdown files

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the `main` branch via the `.github/workflows/jekyll-gh-pages.yml` workflow.

To manually trigger a deployment:
1. Go to the repository on GitHub
2. Navigate to Actions tab
3. Select "Deploy Jekyll with GitHub Pages dependencies preinstalled"
4. Click "Run workflow"