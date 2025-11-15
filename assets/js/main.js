// Main JavaScript for Delta Lake & Apache Iceberg Knowledge Hub

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSyntaxHighlighting();
    initializeSmoothScrolling();
    initializeCopyToClipboard();
    initializeTableOfContents();
    initializeMobileNavigation();
    initializeScrollAnimations();
    initializeStickyHeader();
    initializeSearch();
    initializeAccessibility();
    initializeThemeToggle();
});

// Initialize syntax highlighting for dynamically loaded content
function initializeSyntaxHighlighting() {
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

// Add smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Add copy-to-clipboard functionality for code blocks
function initializeCopyToClipboard() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const pre = block.parentNode;

        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');

        // Add button to pre element
        pre.style.position = 'relative';
        pre.appendChild(copyButton);

        // Add click handler
        copyButton.addEventListener('click', function() {
            const text = block.textContent;
            navigator.clipboard.writeText(text).then(function() {
                // Show success feedback
                copyButton.innerHTML = '<i class="fas fa-check"></i>';
                copyButton.classList.add('copied');
                copyButton.setAttribute('aria-label', 'Code copied to clipboard');

                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                    copyButton.classList.remove('copied');
                    copyButton.setAttribute('aria-label', 'Copy code to clipboard');
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                copyButton.innerHTML = '<i class="fas fa-times"></i>';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            });
        });
    });
}

// Generate table of contents for documentation pages
function initializeTableOfContents() {
    if (document.querySelector('.content')) {
        generateTableOfContents();
    }
}

// Mobile navigation toggle functionality
function initializeMobileNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            const isHidden = navLinks.classList.contains('mobile-hidden');
            navLinks.classList.toggle('mobile-hidden');

            // Update aria-expanded
            navToggle.setAttribute('aria-expanded', !isHidden);

            // Update button text for screen readers
            navToggle.setAttribute('aria-label', isHidden ? 'Close navigation menu' : 'Open navigation menu');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.add('mobile-hidden');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.setAttribute('aria-label', 'Open navigation menu');
            }
        });

        // Close mobile menu on window resize
        window.addEventListener('resize', debounce(function() {
            if (window.innerWidth > 768) {
                navLinks.classList.remove('mobile-hidden');
            } else {
                navLinks.classList.add('mobile-hidden');
            }
        }, 250));
    }
}

// Scroll animations using Intersection Observer
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements that should animate in
    const animateElements = document.querySelectorAll('.feature-card, .content-card, .stat-item');
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// Sticky header behavior
function initializeStickyHeader() {
    const header = document.querySelector('.site-header');
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', debounce(function() {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScrollY = currentScrollY;
    }, 10));
}

// Enhanced accessibility features
function initializeAccessibility() {
    // Add skip link for keyboard navigation
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link sr-only';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Add main content landmark
    const mainContent = document.querySelector('main') || document.querySelector('.main-content');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }

    // Enhance focus management
    const focusableElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        element.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });

    // Add keyboard navigation for cards
    const cards = document.querySelectorAll('.feature-card, .content-card');
    cards.forEach(card => {
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const link = card.querySelector('a');
                if (link) link.click();
            }
        });
    });
}

// Initialize theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;

    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Add click handler
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        themeToggle.classList.toggle('dark', theme === 'dark');
        themeToggle.setAttribute('aria-label', `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`);
    }
}

// Generate table of contents for documentation pages
function generateTableOfContents() {
    const content = document.querySelector('.content');
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');

    if (headings.length < 3) return; // Don't generate TOC for short content

    const toc = document.createElement('nav');
    toc.className = 'table-of-contents';
    toc.setAttribute('aria-label', 'Table of contents');
    toc.innerHTML = '<h4>Table of Contents</h4><ul></ul>';

    const tocList = toc.querySelector('ul');

    headings.forEach((heading, index) => {
        if (heading.tagName === 'H1' && index === 0) return; // Skip main title

        const level = parseInt(heading.tagName.charAt(1));
        const text = heading.textContent;
        const id = heading.id || generateHeadingId(text);

        heading.id = id;

        const li = document.createElement('li');
        li.className = `toc-level-${level}`;
        li.innerHTML = `<a href="#${id}">${text}</a>`;

        tocList.appendChild(li);
    });

    // Insert TOC after the main content title
    const firstHeading = content.querySelector('h1, h2');
    if (firstHeading) {
        firstHeading.insertAdjacentElement('afterend', toc);
    }
}

// Generate unique IDs for headings
function generateHeadingId(text) {
    return text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single
        .trim();
}

// Initialize search functionality (placeholder)
function initializeSearch() {
    // This would be expanded with a proper search implementation
    // For now, it's a placeholder for future enhancement
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.toLowerCase();
            // Implement search logic here
            console.log('Search query:', query);
        }, 300));
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add loading states for async operations
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// Error handling utility
function handleError(error, context = 'An error occurred') {
    console.error(context, error);
    // Could show user-friendly error messages here
}

// Performance monitoring (enhanced)
if ('performance' in window && 'mark' in window.performance) {
    performance.mark('page-load-start');
    window.addEventListener('load', () => {
        performance.mark('page-load-end');
        performance.measure('page-load', 'page-load-start', 'page-load-end');
        const measure = performance.getEntriesByName('page-load')[0];
        console.log(`Page load time: ${measure.duration}ms`);

        // Monitor Core Web Vitals
        if ('web-vitals' in window) {
            webVitals.getCLS(console.log);
            webVitals.getFID(console.log);
            webVitals.getFCP(console.log);
            webVitals.getLCP(console.log);
            webVitals.getTTFB(console.log);
        }
    });
}

// Add CSS for enhanced accessibility
const style = document.createElement('style');
style.textContent = `
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--color-primary);
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: var(--radius-md);
        z-index: 1000;
        transition: top 0.3s;
    }

    .skip-link:focus {
        top: 6px;
    }

    .focused {
        outline: 3px solid var(--color-primary);
        outline-offset: 2px;
    }

    .copy-button {
        position: absolute;
        top: 8px;
        right: 8px;
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-bg-tertiary);
        border-radius: var(--radius-md);
        padding: 6px;
        cursor: pointer;
        opacity: 0;
        transition: all var(--transition-fast);
        color: var(--color-text-secondary);
    }

    pre:hover .copy-button {
        opacity: 1;
    }

    .copy-button:hover {
        background: var(--color-primary);
        color: white;
    }

    .copy-button.copied {
        background: var(--color-success);
        color: white;
    }

    .table-of-contents {
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-bg-tertiary);
        border-radius: var(--radius-lg);
        padding: var(--space-6);
        margin: var(--space-6) 0;
    }

    .table-of-contents h4 {
        margin-bottom: var(--space-4);
        color: var(--color-text-primary);
        font-size: var(--text-lg);
    }

    .table-of-contents ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .table-of-contents li {
        margin-bottom: var(--space-2);
    }

    .table-of-contents a {
        color: var(--color-text-secondary);
        text-decoration: none;
        padding: var(--space-1) 0;
        display: block;
        border-left: 3px solid transparent;
        padding-left: var(--space-3);
        transition: all var(--transition-fast);
    }

    .table-of-contents a:hover {
        color: var(--color-primary);
        border-left-color: var(--color-primary);
        background: var(--color-bg-primary);
    }

    .toc-level-2 { margin-left: var(--space-4); }
    .toc-level-3 { margin-left: var(--space-8); }
    .toc-level-4 { margin-left: var(--space-12); }
    .toc-level-5 { margin-left: var(--space-16); }
    .toc-level-6 { margin-left: var(--space-20); }
`;
document.head.appendChild(style);