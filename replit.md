# Overview

This is a romantic declaration system built with Flask that allows users to create personalized romantic declarations with photos for their loved ones. Users can register, login, create custom declarations with recipient names and photos, and share them via unique URLs. The system includes user authentication, file upload handling, and a dashboard for managing declarations.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Static Assets**: CSS and JavaScript files for styling and client-side functionality
- **UI Framework**: Bootstrap 5 with custom CSS for romantic theming
- **Icons**: Font Awesome 6.4.0 for consistent iconography

## Backend Architecture
- **Web Framework**: Flask 3.1.2 with modular route handling
- **Authentication**: Flask-Login for session management and user authentication
- **Security**: Flask-WTF for CSRF protection and secure form handling
- **Password Security**: Werkzeug for password hashing and verification
- **File Handling**: Pillow for image processing and Werkzeug for secure filename handling

## Data Storage
- **Database**: SQLite for local development with simple schema
- **File Storage**: Local filesystem for uploaded images in static/uploads directory
- **Session Management**: Flask sessions with configurable security settings for production

## Security Architecture
- **CSRF Protection**: Token-based CSRF protection on all forms
- **Session Security**: Secure cookies with HttpOnly and SameSite settings in production
- **File Upload Security**: Filename sanitization, file type validation, and size limits (16MB)
- **Password Security**: Hashed passwords with Werkzeug's security utilities
- **Environment-based Configuration**: Different security settings for development vs production

## Application Structure
- **User Management**: Registration, login, logout with Flask-Login UserMixin
- **Declaration System**: Create, view, and manage romantic declarations
- **File Upload System**: Image upload with preview and validation
- **Dashboard**: User statistics and declaration management
- **Error Handling**: Custom 404 page with themed design

# External Dependencies

## Python Packages
- **Flask 3.1.2**: Core web framework
- **flask-login 0.6.3**: User session management
- **flask-wtf 1.2.2**: Form handling and CSRF protection
- **Pillow 11.3.0**: Image processing and manipulation
- **werkzeug 3.1.3**: WSGI utilities and security functions
- **gunicorn 22.0.0**: Production WSGI server

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework via CDN
- **Font Awesome 6.4.0**: Icon library via CDN

## Infrastructure
- **Render Platform**: Configured for production deployment with environment variables
- **SQLite**: Embedded database for data persistence
- **Static File Serving**: Flask's built-in static file handling for uploads and assets