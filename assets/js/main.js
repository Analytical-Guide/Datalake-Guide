// Main JavaScript for Delta Lake & Apache Iceberg Knowledge Hub

document.addEventListener('DOMContentLoaded', function() {
    // Initialize syntax highlighting for dynamically loaded content
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }

    // Add smooth scrolling for anchor links
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

    // Add copy-to-clipboard functionality for code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const pre = block.parentNode;

        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';

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

                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                    copyButton.classList.remove('copied');
                }, 2000);
            });
        });
    });

    // Add table of contents generation for docs pages
    if (document.querySelector('.content')) {
        generateTableOfContents();
    }

    // Add search functionality (placeholder for future implementation)
    initializeSearch();
});

// Generate table of contents for documentation pages
function generateTableOfContents() {
    const content = document.querySelector('.content');
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');

    if (headings.length < 3) return; // Don't generate TOC for short content

    const toc = document.createElement('nav');
    toc.className = 'table-of-contents';
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
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            // Implement search logic here
            console.log('Search query:', query);
        });
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

// Performance monitoring (basic)
if ('performance' in window && 'mark' in window.performance) {
    performance.mark('page-load-start');
    window.addEventListener('load', () => {
        performance.mark('page-load-end');
        performance.measure('page-load', 'page-load-start', 'page-load-end');
        const measure = performance.getEntriesByName('page-load')[0];
        console.log(`Page load time: ${measure.duration}ms`);
    });
}