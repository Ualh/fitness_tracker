# Fitness Tracker

## Overview

A privacy-focused fitness tracking application built with Streamlit that allows users to log activities and track weight without requiring external services or accounts. The application stores all data locally in JSON files, emphasizing user privacy and data ownership. Key features include activity logging with duration, intensity, and targeted adaptation tracking (based on Galpin's 9 adaptations), weight monitoring with goal setting, visual dashboards with charts and metrics, and a clean, minimal user interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### August 2025 - Comprehensive Code Optimization and Clean Architecture
- **Code Structure Optimization**: Complete refactoring for improved maintainability and performance:
  - Created centralized `constants.py` module eliminating code duplication across 50+ locations
  - Implemented optimized data managers with intelligent caching and atomic file operations
  - Developed modular visualization engine with performance improvements and color management
  - Created reusable UI components for consistent interface patterns
  - Established proper error boundaries and validation throughout the application

- **Performance Enhancements**: Advanced optimization techniques implemented:
  - Intelligent file-based caching with modification time checking and TTL
  - Streamlit native caching decorators for all heavy operations
  - Database connection pooling with optimized session management
  - Efficient pandas operations with proper data typing
  - Context managers for automatic resource cleanup
  - Vectorized data filtering and aggregation operations

- **Clean Code Practices**: Industry-standard development practices:
  - Eliminated duplicate constants and magic numbers (50+ instances)
  - Separated concerns with dedicated modules for each responsibility
  - Added comprehensive type hints and documentation
  - Implemented proper error handling with user-friendly messages
  - Created backward compatibility layers for smooth transitions
  - Applied DRY principles throughout the codebase

- **Database Optimization**: Enhanced database operations:
  - Context manager pattern for automatic session cleanup
  - Optimized queries with proper filtering and pagination
  - Prepared statement patterns for SQL injection prevention
  - Connection pooling configuration centralized in constants
  - Efficient relationship loading and foreign key handling

### August 2025 - Major Performance Optimization and Database Integration
- **Performance Optimization**: Comprehensive performance improvements implemented:
  - Added intelligent caching layer for data loading operations (file modification time checking)
  - Implemented Streamlit @st.cache_data decorators for all visualization functions
  - Optimized database connection pooling with proper engine configuration
  - Created efficient data filtering algorithms to reduce computational overhead
  - Added summary statistics caching to avoid repeated calculations
  - Streamlined theme application with conditional loading
  - Enhanced DataFrame operations with pandas-native filtering
  - Database query optimization with result limiting and proper indexing

- **Database Migration**: Migrated from JSON files to PostgreSQL database with SQLAlchemy ORM
- **User Authentication**: Added complete login/register system with bcrypt password hashing
- **Friends System**: Users can add friends and view their recent fitness activities
- **Multi-language Support**: Added French translation support with dynamic language switching
- **Dark Mode**: Implemented dark theme toggle with user preference persistence
- **Improved UI**: Replaced metric tabs with compact summary box for better space utilization
- **Real-time Updates**: Fixed adaptation descriptions to update immediately on selection
- **Data Security**: All user data now stored securely in database with user isolation

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Design**: Tab-based navigation with Dashboard, Add Activity, Weight, and Settings sections
- **Styling**: Custom CSS for minimal design with light color scheme and clean metrics cards
- **State Management**: Streamlit's built-in session state and caching mechanisms

### Data Storage
- **Storage Type**: PostgreSQL database with SQLAlchemy ORM
- **Database Models**: 
  - Users: ID, username, email, password_hash, weight_goal, language preference, dark_mode setting
  - Activities: ID, user_id, type, duration, intensity, date, description, adaptation (Galpin's 9 fitness adaptations)
  - Weight Entries: ID, user_id, weight, date
  - Friendships: Many-to-many relationship table for user connections
- **Data Security**: Bcrypt password hashing, user data isolation, prepared statements for SQL injection prevention

### Data Management Layer
- **DataManager Class**: Central component handling all data operations with advanced caching
- **File Operations**: JSON serialization/deserialization with intelligent file modification tracking
- **Data Validation**: Automatic directory creation and file initialization
- **Pandas Integration**: Activities and weight data converted to DataFrames for analysis
- **Performance Caching**: Multi-layer caching system including:
  - File modification time-based cache invalidation
  - In-memory data caching with timestamps
  - Streamlit native caching for UI components
  - Database connection pooling for optimal query performance

### Visualization Layer
- **Charts Library**: Plotly Express and Graph Objects for interactive visualizations
- **Chart Types**: 
  - Activity distribution pie charts
  - Weight progression line charts with goal tracking
  - Weekly summary metrics
  - Training adaptations focus chart (based on Galpin's 9 adaptations)
- **Responsive Design**: Charts adapt to container sizing

### Utility Functions
- **Activity Support**: Extended activity types with emoji mapping (Running, Cycling, Swimming, Rock Climbing, Boxing, Basketball, Soccer, Tennis, CrossFit, Pilates, Dancing, Martial Arts, Rowing, etc.)
- **Training Science**: Integration of Galpin's 9 fitness adaptations (Maximal aerobic capacity, Long duration submaximal work, Speed, Power, Anaerobic capacity, Strength, Muscular endurance, Muscle hypertrophy)
- **Data Formatting**: Duration formatting (minutes to hours/minutes) and intensity color coding
- **Calculations**: Calorie estimation based on activity type, duration, and intensity level

### Privacy and Security
- **Local-First Architecture**: No external data transmission or cloud storage
- **No Authentication**: Simplified access model for single-user local deployment
- **Data Ownership**: Users maintain complete control over their fitness data

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework and UI components
- **pandas**: Data manipulation and analysis for activity/weight records
- **plotly**: Interactive charting and visualization library (express and graph_objects modules)
- **json**: Built-in JSON serialization for data persistence
- **os**: File system operations for data directory management
- **datetime**: Date/time handling for activity logging and filtering
- **uuid**: Unique identifier generation for activity records

### No External Services
The application is designed to operate completely offline without requiring:
- Database connections
- API integrations
- Cloud storage services
- User authentication providers
- Third-party fitness tracking services