import datetime
import os
import subprocess
import time
from typing import List, Optional, Tuple

import pandas as pd
import psutil
import requests
import streamlit as st

# Streamlit page setup
st.set_page_config(
    page_title="Memory Cleanup Utility",
    page_icon="🔧",)

# Constants
DATA_DIR = "data"
MEMORY_FILE_PATH = os.path.join(DATA_DIR, "memory_usage.csv")
EXE_PATH = os.path.join(os.getcwd(), "EmptyStandbyList.exe")
GITHUB_RELEASE_URL = "https://api.github.com/repos/PatrickJnr/StreamLitMemCleaner/releases/latest"
DOWNLOAD_URL = "https://github.com/stefanpejcic/EmptyStandbyList/raw/master/EmptyStandbyList.exe"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize app
st.title("Memory Cleanup Utility")

# Utility functions
def run_command(command: List[str]) -> Tuple[str, int]:
    """Run a system command and return its output and return code."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout, result.returncode
    except Exception as e:
        st.error(f"Command execution error: {e}")
        return str(e), 1

def format_memory_value(memory_mb: float) -> str:
    """Format memory value in MB or GB."""
    if memory_mb < 1024:
        return f"{memory_mb:.2f} MB"
    else:
        return f"{memory_mb / 1024:.2f} GB"

def get_system_info() -> Tuple[float, float, float, float]:
    """Get the system's memory information."""
    try:
        mem = psutil.virtual_memory()
        total_memory = mem.total / (1024**3)
        free_memory_gb = mem.available / (1024**3)
        used_memory = mem.used / (1024**3)
        return total_memory, free_memory_gb, 0.0, used_memory  # Set cached to 0.0
    except Exception as e:
        st.error(f"Error fetching system info: {e}")
        return 0.0, 0.0, 0.0, 0.0

def read_local_version() -> Optional[str]:
    """Read the local version from a file."""
    version_file_path = os.path.join(DATA_DIR, "version.txt")
    try:
        with open(version_file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None
    except IOError as e:
        st.error(f"Error reading version file: {e}")
        return None

def get_latest_release(timeout: float = 10) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Fetch the latest release information from GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "StreamLitMemCleanerApp"}
    try:
        response = requests.get(GITHUB_RELEASE_URL, headers=headers, timeout=timeout)
        response.raise_for_status()
        release_data = response.json()

        tag_name = release_data.get("tag_name")
        html_url = release_data.get("html_url")
        body = release_data.get("body", "No changelog available.")

        if not tag_name:
            st.warning("Unable to retrieve the latest version information!")
            return None, None, None

        return tag_name, html_url, body
    except requests.RequestException as e:
        st.error(f"Failed to fetch the latest release: {e}")
        return None, None, None

def plot_memory_history(data: pd.DataFrame):
    """Plot the memory and CPU usage history using a line chart."""
    try:
        data["Timestamp"] = pd.to_datetime(data["Timestamp"])
        data.set_index("Timestamp", inplace=True)
        st.line_chart(data[['Free Memory Before', 'Free Memory After', 'Freed Memory']])
    except Exception as e:
        st.error(f"Error plotting memory history: {e}")

def load_changelog() -> str:
    """Load the changelog from the CHANGELOG.md file."""
    changelog_path = "CHANGELOG.md"
    try:
        with open(changelog_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Changelog not found."
    except IOError as e:
        return f"Error reading changelog: {e}"

def download_exe():
    """Download the EmptyStandbyList.exe file if not present."""
    if not os.path.exists(EXE_PATH):
        st.error("Error: EmptyStandbyList.exe not found.")
        if st.button("Download EmptyStandbyList.exe"):
            try:
                response = requests.get(DOWNLOAD_URL, timeout=30)
                response.raise_for_status()
                with open(EXE_PATH, "wb") as file:
                    file.write(response.content)
                st.success("EmptyStandbyList.exe downloaded successfully! Refresh the page to use the program.")
            except requests.RequestException as e:
                st.error(f"Failed to download EmptyStandbyList.exe: {e}")
            return False
    return True

# Main function
def main():
    """Main function to run the memory cleanup utility."""
    local_version = read_local_version()

    # Ensure the required executable exists
    if not download_exe():
        return

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Updates", "Help", "Changelog"])

    if page == "Home":
        # Display system information
        st.subheader("System Information")
        system_info_placeholder = st.empty()

        def display_system_info():
            total_memory, free_memory_before, _, used_memory = get_system_info()
            system_info_placeholder.markdown(f"""
                **Total Memory:** {format_memory_value(total_memory * 1024)}
                **Free Memory:** {format_memory_value(free_memory_before)}
                **Used Memory:** {format_memory_value(used_memory * 1024)}
            """)

        display_system_info()

        if st.button("Refresh System Information"):
            display_system_info()

        # Define cleanup commands
        commands = {
            "modifiedpagelist": "Clear modified page list",
            "standbylist": "Clear standby list",
            "priority0standbylist": "Clear priority 0 standby list",
            "workingsets": "Clear working sets",
        }

        # Select cleanup commands
        selected_commands = st.multiselect("Select Cleanup Commands", list(commands.keys()), default=list(commands.keys()))

        if st.button("Start Cleanup"):
            if len(selected_commands) == len(commands):
                st.warning("You have selected all cleanup options. Your system may lock up briefly during the cleanup process.")

            with st.spinner('Cleaning up memory...'):
                total_memory, free_memory_before, _, _ = get_system_info()
                st.write(f"Total Memory: {format_memory_value(total_memory * 1024)}")
                st.write(f"Free Memory before cleanup: {format_memory_value(free_memory_before)}")

                progress_bar = st.progress(0)
                for i, cmd in enumerate(selected_commands):
                    st.write(f"Executing EmptyStandbyList for {commands[cmd]}...")
                    output, returncode = run_command([EXE_PATH, cmd])
                    if returncode == 0:
                        progress_bar.progress((i + 1) / len(selected_commands))
                    else:
                        st.error(f"Error occurred while executing {cmd}. Output: {output}")
                        break

                _, free_memory_after, _, _ = get_system_info()
                st.write(f"Free Memory after cleanup: {format_memory_value(free_memory_after)}")

                freed_memory = free_memory_after - free_memory_before
                st.write(f"Freed memory: {format_memory_value(abs(freed_memory))}")

                new_data = pd.DataFrame({
                    "Timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Free Memory Before": [f"{free_memory_before:.2f}"],
                    "Free Memory After": [f"{free_memory_after:.2f}"],
                    "Freed Memory": [f"{abs(freed_memory):.2f}"]
                })

                try:
                    if os.path.exists(MEMORY_FILE_PATH):
                        memory_df = pd.read_csv(MEMORY_FILE_PATH)
                        memory_df = pd.concat([memory_df, new_data], ignore_index=True)
                    else:
                        memory_df = new_data

                    memory_df.to_csv(MEMORY_FILE_PATH, index=False)
                except Exception as e:
                    st.error(f"Error saving memory usage history: {e}")

        # Memory usage history
        st.subheader("Memory Usage History")
        if os.path.exists(MEMORY_FILE_PATH):
            try:
                memory_df = pd.read_csv(MEMORY_FILE_PATH)
                st.dataframe(memory_df)

                if st.button("Plot Memory Usage"):
                    if not memory_df.empty:
                        plot_memory_history(memory_df)
                    else:
                        st.warning("No data available to plot.")

                if st.button("Delete Memory Usage History"):
                    st.session_state.confirm_delete = True

                if st.session_state.get("confirm_delete"):
                    if st.button("Confirm Delete"):
                        try:
                            os.remove(MEMORY_FILE_PATH)
                            st.success("Memory usage history deleted successfully.")
                            del st.session_state.confirm_delete
                        except Exception as e:
                            st.error(f"Error deleting memory usage history: {e}")
                    if st.button("Cancel"):
                        del st.session_state.confirm_delete
            except Exception as e:
                st.error(f"Error reading memory history: {e}")
        else:
            st.write("No memory usage history available.")

    elif page == "Updates":
        st.write("**Version Check**")
        st.markdown(f"**Local Version:** {local_version}")

        if st.button("Check for Updates"):
            tag_name, html_url, body = get_latest_release()
            if tag_name:
                if local_version != tag_name:
                    st.warning(f"A new version is available: {tag_name}!")
                    st.markdown(f"[Go to the release page]({html_url})")
                else:
                    st.success("You are using the latest version.")
            else:
                st.error("Failed to check for updates.")

    elif page == "Help":
        st.write("**Help Section**")
        st.write(
            """
            - **Memory Monitoring**: Displays your system's memory usage.
            - **Cleanup Commands**:
              - Clear modified page list: Removes modified pages not written to disk.
              - Clear standby list: Clears unused memory pages held in RAM.
              - Clear priority 0 standby list: Targets low-priority memory pages.
              - Clear working sets: Frees memory from inactive applications.
            - **Updating the Application**: Manually check for updates.
            - **Viewing Memory History**: Plot or delete memory usage history.
            """
        )

    elif page == "Changelog":
        st.markdown(load_changelog())

    # Footer
    st.write("---")
    st.write("© GrimTech 2007-2024 | PatrickJr. ❤️ Made with love")

if __name__ == "__main__":
    main()