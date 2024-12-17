## [v1.0.2] - 2024-12-16

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