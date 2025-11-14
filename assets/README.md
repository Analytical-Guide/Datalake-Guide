# Assets Directory

This directory contains static assets for the Jekyll site.

## Structure

```
assets/
├── css/
│   └── main.css          # Main stylesheet
├── js/
│   └── main.js           # Main JavaScript file
└── images/               # Static images (logos, diagrams, etc.)
```

## CSS

The `main.css` file contains all the styling for the site, including:
- Responsive design
- Dark mode support
- Print styles
- Component styles for navigation, content, footer, etc.

## JavaScript

The `main.js` file provides interactive functionality:
- Syntax highlighting initialization
- Copy-to-clipboard for code blocks
- Table of contents generation
- Smooth scrolling
- Search functionality (placeholder)

## Images

Place static images here:
- Site logos and favicons
- Architecture diagrams
- Screenshots
- Social media preview images

## Usage

Assets are automatically included in Jekyll builds and can be referenced using:
- CSS: `{{ '/assets/css/main.css' | absolute_url }}`
- JS: `{{ '/assets/js/main.js' | absolute_url }}`
- Images: `{{ '/assets/images/filename.png' | absolute_url }}`