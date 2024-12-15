# Memory Cleanup Utility

The **Memory Cleanup Utility** is a Streamlit-based application designed to monitor, analyze, and clean up system memory. This tool can help identify memory bottlenecks, perform cleanup tasks, and maintain historical data on memory usage.

---

## Demo

Watch the demo of the Memory Cleanup Utility:

https://github.com/user-attachments/assets/aa79d784-5d22-470e-a597-fe407e9e069d

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
  - Visualizes data in an easy-to-read chart.
- **Integration with EmptyStandbyList.exe**: Uses the executable to perform memory cleanup tasks.
- **Custom CSS Styling**: Personalize the application UI with external CSS files.

---

## Installation

### Prerequisites
1. Install [Python 3.9+](https://www.python.org/downloads/).
2. Install required Python libraries:
   ```bash
   pip install streamlit pandas matplotlib requests
   ```

3. Download the `EmptyStandbyList.exe` file:
   - If not already present, the app will prompt you to download it during runtime.

### Running the Application

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

4. The app should automatically open the app in your browser at `http://localhost:8501`.

---

## Usage

### Memory Monitoring
- View your system's memory statistics, including:
  - Total memory
  - Free memory
  - Cached memory

### Cleanup Tasks
- Select from the provided cleanup options to free up system memory.
- Track the amount of memory freed after executing commands.

### Historical Data
- View and analyze historical memory usage through tables and charts.
- Delete memory history when it reaches a specified maximum row count.


---

## Development

To contribute or debug:
1. Use `git` to manage version control.
2. Run the app in a local development environment.
3. Ensure changes pass tests before submitting a pull request.

**Latest Commit Hash**: Automatically displayed in the app footer.

---

## Help

If you encounter issues or have questions, check the **Help** section in the app's sidebar. You can also contact support via the GitHub Issues page.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Credits

- [Streamlit](https://streamlit.io/) - For building the app interface and functionality.
- [Matplotlib](https://matplotlib.org/) - For visualizing memory usage data in charts.
- [Pandas](https://pandas.pydata.org/) - For handling and processing memory usage data.
- [Requests](https://requests.readthedocs.io/en/master/) - For making HTTP requests to retrieve updates and other data.
- [Python](https://www.python.org/) - For the underlying programming language.

Special thanks to the contributors and open-source communities for their ongoing work and support.

