@echo off
REM Build and validation script for Delta Lake ^& Apache Iceberg Knowledge Hub
REM This script performs basic validation checks for the Jekyll site

echo ========================================
echo Delta Lake ^& Apache Iceberg Knowledge Hub
echo Build and Validation Script
echo ========================================

REM Check if we're in the right directory
if not exist "_config.yml" (
    echo ERROR: _config.yml not found. Please run this script from the repository root.
    exit /b 1
)

echo [+] Checking repository structure...

REM Check for required directories
set REQUIRED_DIRS=_layouts assets\css assets\js docs code-recipes
for %%d in (%REQUIRED_DIRS%) do (
    if not exist "%%d" (
        echo ERROR: Required directory %%d is missing
        exit /b 1
    ) else (
        echo [OK] Directory %%d exists
    )
)

REM Check for required files
set REQUIRED_FILES=_config.yml index.md _layouts\default.html assets\css\main.css assets\js\main.js
for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo ERROR: Required file %%f is missing
        exit /b 1
    ) else (
        echo [OK] File %%f exists
    )
)

echo [+] Validating Jekyll configuration...

REM Check if _config.yml is valid YAML (basic check)
findstr /c:"title:" _config.yml >nul 2>&1
if errorlevel 1 (
    echo ERROR: _config.yml appears to be malformed (missing title)
    exit /b 1
) else (
    echo [OK] _config.yml contains basic configuration
)

echo [+] Checking for broken links in README.md...

REM Extract links from README.md and check if files exist
for /f "tokens=*" %%i in ('findstr "\[.*\](\S*)" README.md') do (
    REM Extract URL part from markdown link
    for /f "tokens=2 delims=()" %%j in ("%%i") do (
        set "link=%%j"
        REM Remove any leading/trailing spaces
        for /f "tokens=* delims= " %%k in ("!link!") do set "link=%%k"

        REM Skip external links (http/https)
        echo !link! | findstr "^http" >nul 2>&1
        if errorlevel 1 (
            REM Check if internal link exists
            if not exist "!link!" (
                echo WARNING: Linked file !link! does not exist
            ) else (
                echo [OK] Link !link! exists
            )
        )
    )
)

echo [+] Checking documentation files...

REM Count markdown files in docs directory
for /f %%c in ('dir /b /s docs\*.md 2^>nul ^| find /c ".md"') do set DOC_COUNT=%%c
echo [INFO] Found %DOC_COUNT% documentation files

REM Count code recipe files
for /f %%c in ('dir /b /s code-recipes\*.md 2^>nul ^| find /c ".md"') do set RECIPE_COUNT=%%c
echo [INFO] Found %RECIPE_COUNT% code recipe files

echo [+] Build validation complete!

echo ========================================
echo Summary:
echo - Repository structure: OK
echo - Required files: OK
echo - Configuration: OK
echo - Documentation files: %DOC_COUNT%
echo - Code recipes: %RECIPE_COUNT%
echo ========================================

echo.
echo To deploy to GitHub Pages, commit and push these changes.
echo The site will be automatically built and deployed via GitHub Actions.
echo.

echo Press any key to exit...
pause >nul