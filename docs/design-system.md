---
layout: default
title: Design System
description: Comprehensive design system documentation for the Delta Lake & Apache Iceberg Knowledge Hub
---

# Design System Documentation

## Overview

This document outlines the comprehensive design system used throughout the Delta Lake & Apache Iceberg Knowledge Hub. The system is built on modern web standards with a focus on accessibility, performance, and user experience.

## Color Palette

### Primary Colors
- **Primary**: `#4F46E5` (Vibrant Indigo)
- **Primary Light**: `#818CF8` (Soft Indigo)
- **Primary Lighter**: `#C7D2FE` (Pale Indigo)
- **Primary Dark**: `#3730A3` (Deep Indigo)

### Secondary Colors
- **Secondary**: `#EC4899` (Vibrant Pink)
- **Secondary Light**: `#F9A8D4` (Soft Pink)
- **Accent**: `#F59E0B` (Warm Amber)
- **Accent Light**: `#FCD34D` (Bright Yellow)

### Neutral Colors
- **Background Primary**: `#FEFEFE` (Warm White)
- **Background Secondary**: `#F8FAFC` (Light Gray-Blue)
- **Background Tertiary**: `#F1F5F9` (Medium Gray-Blue)
- **Text Primary**: `#1E293B` (Slate Gray)
- **Text Secondary**: `#475569` (Medium Slate)
- **Text Tertiary**: `#94A3B8` (Light Slate)

### Status Colors
- **Success**: `#10B981` (Emerald Green)
- **Warning**: `#F59E0B` (Amber)
- **Error**: `#EF4444` (Red)
- **Info**: `#3B82F6` (Blue)

## Typography

### Font Families
- **Primary**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono (Google Fonts)

### Font Sizes (Fluid Typography)
- `text-xs`: `clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)`
- `text-sm`: `clamp(0.875rem, 0.8rem + 0.375vw, 1rem)`
- `text-base`: `clamp(1rem, 0.9rem + 0.5vw, 1.125rem)`
- `text-lg`: `clamp(1.125rem, 1rem + 0.625vw, 1.25rem)`
- `text-xl`: `clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)`
- `text-2xl`: `clamp(1.5rem, 1.3rem + 1vw, 2rem)`
- `text-3xl`: `clamp(1.875rem, 1.5rem + 1.5vw, 2.5rem)`
- `text-4xl`: `clamp(2.25rem, 1.8rem + 2vw, 3rem)`

### Font Weights
- Light: `300`
- Normal: `400`
- Medium: `500`
- Semibold: `600`
- Bold: `700`
- Extrabold: `800`

### Line Heights
- Tight: `1.25`
- Normal: `1.5`
- Relaxed: `1.75`

## Spacing Scale

Built on an 8px base grid:

- `space-1`: `0.25rem` (4px)
- `space-2`: `0.5rem` (8px)
- `space-3`: `0.75rem` (12px)
- `space-4`: `1rem` (16px)
- `space-5`: `1.5rem` (24px)
- `space-6`: `2rem` (32px)
- `space-8`: `3rem` (48px)
- `space-10`: `4rem` (64px)
- `space-12`: `6rem` (96px)
- `space-16`: `8rem` (128px)

## Border Radius

- `radius-sm`: `0.375rem` (6px)
- `radius-md`: `0.5rem` (8px)
- `radius-lg`: `0.75rem` (12px)
- `radius-xl`: `1rem` (16px)
- `radius-2xl`: `1.5rem` (24px)
- `radius-full`: `9999px`

## Shadows

- `shadow-sm`: Subtle shadow for cards
- `shadow-md`: Medium shadow for elevated elements
- `shadow-lg`: Large shadow for modals/popovers
- `shadow-xl`: Extra large shadow for emphasis
- `shadow-2xl`: Maximum shadow for overlays

## Gradients

- `gradient-hero`: Linear gradient for hero sections
- `gradient-card`: Subtle card background gradient
- `gradient-cta`: Call-to-action button gradient

## Transitions

- `transition-fast`: `150ms cubic-bezier(0.4, 0, 0.2, 1)`
- `transition-base`: `250ms cubic-bezier(0.4, 0, 0.2, 1)`
- `transition-slow`: `350ms cubic-bezier(0.4, 0, 0.2, 1)`

## Dark Mode

The design system includes comprehensive dark mode support:

### Dark Mode Colors
- Background Primary: `#0F172A` (Deep Slate)
- Background Secondary: `#1E293B` (Slate)
- Background Tertiary: `#334155` (Medium Slate)
- Text Primary: `#F1F5F9` (Light)
- Text Secondary: `#CBD5E1` (Medium Light)
- Text Tertiary: `#94A3B8` (Muted)

### Implementation
- Automatic detection via `prefers-color-scheme: dark`
- Manual override via theme toggle button
- Persistent user preference in localStorage

## Components

### Navigation
- Sticky header with backdrop blur
- Responsive mobile menu
- Theme toggle integration
- Smooth scroll behavior

### Buttons
- Primary CTA buttons with gradient backgrounds
- Secondary buttons with subtle styling
- Icon integration support
- Hover animations with transform effects

### Cards
- Feature cards with hover effects
- Content cards for documentation
- Consistent padding and border radius
- Shadow system integration

### Forms
- Accessible form controls
- Focus management
- Error state styling
- Responsive layouts

## Accessibility

### Focus Management
- `focus-visible` outlines for keyboard navigation
- Skip links for screen readers
- Proper ARIA labels and roles
- Semantic HTML structure

### Motion Preferences
- Respects `prefers-reduced-motion`
- Disabled animations for users who prefer reduced motion
- Essential animations only

### Color Contrast
- WCAG AA compliance
- High contrast focus indicators
- Clear text hierarchy

## Responsive Design

### Breakpoints
- Mobile: `max-width: 768px`
- Tablet: `min-width: 769px and max-width: 1024px`
- Desktop: `min-width: 1025px`

### Fluid Typography
- Clamp functions for scalable text
- Viewport-based sizing
- Minimum and maximum constraints

### Grid System
- CSS Grid for complex layouts
- Flexbox for component alignment
- Container max-widths for readability

## Performance Optimizations

### Font Loading
- `font-display: swap` for better loading
- Preload critical font weights
- Fallback font stacks

### CSS Optimizations
- CSS custom properties for theming
- Efficient selectors
- Minimal specificity conflicts

### JavaScript Enhancements
- Lazy loading for images
- Intersection Observer for animations
- Debounced event handlers

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Progressive enhancement approach
- Graceful degradation for older browsers

## Implementation Guidelines

### CSS Architecture
- CSS custom properties for design tokens
- Component-based styling
- Mobile-first responsive design
- BEM-like naming convention

### JavaScript Integration
- Vanilla JavaScript for broad compatibility
- Progressive enhancement
- Accessibility-first approach
- Performance-conscious coding

### HTML Structure
- Semantic HTML5 elements
- Proper heading hierarchy
- Accessible form markup
- Screen reader friendly content

## Maintenance

### Version Control
- Document changes in design system updates
- Maintain backward compatibility
- Deprecation notices for removed features

### Testing
- Cross-browser testing
- Accessibility audits
- Performance monitoring
- User experience validation

This design system provides a solid foundation for consistent, accessible, and performant web experiences across the Delta Lake & Apache Iceberg Knowledge Hub.