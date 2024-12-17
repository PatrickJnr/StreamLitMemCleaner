# Memory Cleanup Utility

The **Memory Cleanup Utility** is a Streamlit-based application designed to monitor, analyze, and clean up system memory. This tool helps identify memory bottlenecks, perform cleanup tasks, and maintain historical data on memory usage.

---

## Demo

Watch the demo of the Memory Cleanup Utility:

[Demo Video](https://github.com/user-attachments/assets/aa79d784-5d22-470e-a597-fe407e9e069d)

---

## Features

- **Memory Monitoring**: Displays your system's total, free, cached, and used memory.
- **Cleanup Commands**: Executes memory cleanup tasks, including clearing:
  - Modified page list
  - Standby list
  - Priority 0 standby list
  - Working sets
- **Historical Data Visualization**:
  - Tracks memory usage over time.
  - Visualizes data in easy-to-read charts.
- **Integration with EmptyStandbyList.exe**: Uses the executable to perform memory cleanup tasks.
- **Custom CSS Styling**: Personalize the application UI with external CSS files.
- **Version Checking**: Manually check for application updates.
- **Git Commit Hash Display**: Shows the current Git commit hash in the app footer.

---

## Installation

### Prerequisites

1. Install [Python 3.9+](https://www.python.org/downloads/).
2. Install the required Python libraries:
   ```bash
   pip install streamlit pandas matplotlib requests
   ```
3. Download the `EmptyStandbyList.exe` file. If not already present, the app will prompt you to download it during runtime.

### Method 1: Clone the Repository

1. Clone this repository:
   ```bash
   git clone https://github.com/PatrickJnr/StreamLitMemCleaner.git
   ```
2. Navigate to the project directory:
   ```bash
   cd StreamLitMemCleaner
   ```
3. Start the application:
   ```bash
   streamlit run memcleaner.py
   ```
4. The app should automatically open in your browser at `http://localhost:8501`.

### Method 2: Download the Latest Release

1. Download the latest release from the [releases tab](https://github.com/PatrickJnr/StreamLitMemCleaner/releases).
2. Extract the downloaded archive.
3. Navigate to the extracted directory.
4. Ensure you have Python 3.9+ and the required libraries installed (see prerequisites above).
5. Start the application using the command:
   ```bash
   streamlit run memcleaner.py
   ```
6. The app should automatically open in your browser at `http://localhost:8501`.

### Method 3: Run the Application Using `run.bat` (Windows Only)

For ease of use, a `run.bat` file is included in the repository. This script will:

- Install the required Python dependencies.
- Run the application automatically.

To use the `run.bat` file:

1. Download or clone the repository.
2. Navigate to the project directory.
3. Double-click the `run.bat` file to start the application.

---

## Usage

### Memory Monitoring
- View system memory statistics, including:
  - Total memory
  - Free memory
  - Cached memory

### Cleanup Tasks
- Select from various cleanup options to free up system memory.
- Track the amount of memory freed after executing commands.
- Warnings are displayed if all cleanup options are selected simultaneously.

### Historical Data
- Analyze historical memory usage with detailed tables and charts.
- Manage memory history by deleting data that exceeds a specified maximum row count.

---

## Development

To contribute or debug:

1. Use Git for version control.
2. Run the app in a local development environment.
3. Ensure changes pass tests before submitting a pull request.

The **Latest Commit Hash** is automatically displayed in the app footer for reference.

---

## Help

For troubleshooting and support:

- Check the **Help** section in the app footer.
- Report issues or ask questions on the [GitHub Issues page](link_to_github_issues).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Credits

This application utilizes the following libraries and tools:

- [Streamlit](https://streamlit.io/) - For building the app interface and functionality.
- [Matplotlib](https://matplotlib.org/) - For visualizing memory usage data in charts.
- [Pandas](https://pandas.pydata.org/) - For handling and processing memory usage data.
- [Requests](https://requests.readthedocs.io/en/master/) - For making HTTP requests to retrieve updates and other data.
- [Python](https://www.python.org/) - The underlying programming language.

Special thanks to contributors and the open-source community for their support.