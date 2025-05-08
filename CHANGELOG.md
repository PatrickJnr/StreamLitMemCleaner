## [v1.0.4] - 08 May 2025

### Added
- Logging system with file and console handlers
- Type safety with enums and type definitions
- Path handling with pathlib
- Session state management
- Memory history pagination and sorting
- Color-coded success messages
- Help documentation with tabs
- Version display in footer
- Critical error handling

### Changed
- Changelog date format to Day Month Year
- Enhanced error messages and feedback
- Memory usage display with percentage formatting
- Improved cleanup command handling
- Enhanced update checking interface
- Enhanced changelog page with better error handling
- Simplified Page enum values

### Refactor
- Restructured app with OOP principles
  - Class-based architecture for separation of concerns
  - Dedicated UI components
  - Centralized configuration
  - Enhanced error handling
  - Improved memory information display
- Split large functions into smaller methods
- Added type hints and documentation
- Improved code organization with mixins
- Centralized string formatting
- Added error handling

## [v1.0.4] - 08 May 2025

### Refactor
  - Restructure app with OOP principles and improve code organization
  - Implement class-based architecture for better separation of concerns
  - Create dedicated UI components for each page
  - Centralize configuration with structured dictionaries
  - Enhance error handling throughout the application
  - Improve memory information display with additional metrics

### Changed
- Updated changelog date format to Day Month Year for better readability

## [v1.0.3] - 21 December 2024

### Added
- Added a confirmation dialog before deleting memory usage history.
- Improved error handling for file operations.
- Added a refresh button for system information.
- Improved layout using columns.

## [v1.0.2] - 16 December 2024

### Added
- Centralized constants for paths and URLs to simplify maintenance.
- `download_exe()` function to handle the download and verification of `EmptyStandbyList.exe` if missing.
- Enhanced error handling for memory info retrieval and plotting operations.
- Additional docstrings for utility functions to improve code clarity.
- Modularized RAM data collection through a reusable `collect_ram_data()` function.
- `run.bat` script to automate the setup and running of the application, including dependency installation and Streamlit execution.

### Changed
- Refactored the `main()` function to streamline logic and reduce inline redundancy.
- Simplified tab layouts with consistent descriptions for each section.
- Optimized memory cleanup warnings and progress feedback during operations.
- Consolidated similar logic in memory management and plotting history for maintainability.
- Changed the chart visualization from a graph to a line chart for better clarity.

### Fixed
- Ensured proper handling of missing or corrupted version files in `read_local_version()`.
- Fixed issues with missing memory history files to prevent crashes.
- Improved handling of command execution errors with more robust and informative error messages.

## [v1.0.1] - 2024-12-15

### Changed
- Minor improvements to the user interface.
- Enhanced performance of memory cleanup operations.

## [v1.0.0] - 2024-12-15

### Added
- Initial release of the Memory Cleanup Utility.
- Core functionality for monitoring and cleaning system memory.
- Basic user interface with tabs for different functionalities.
- Memory usage history tracking and visualization.