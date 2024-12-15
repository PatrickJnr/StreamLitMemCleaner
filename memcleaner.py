import datetime
import os
import subprocess
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Memory Cleanup Utility", page_icon="🔧")


def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file {file_name} not found.")


load_css(".streamlit/styles.css")


DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


st.title("Memory Cleanup Utility")


def read_local_version() -> str:
    version_file_path = os.path.join(DATA_DIR, "version.txt")
    try:
        with open(version_file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Version file not found."
    except IOError as e:
        st.error(f"Error reading version file: {e}")
        return "Error reading version"


def get_latest_release(
    timeout: float = 10,
) -> Tuple[Optional[str], Optional[List[dict]]]:
    url = "https://api.github.com/repos/PatrickJnr/StreamLitMemCleaner/releases/latest"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "StreamLitMemCleanerApp",
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        release_data = response.json()

        # Get tag name and assets
        tag_name = release_data.get("tag_name")
        assets = release_data.get("assets", [])

        if not tag_name:
            st.warning("Unable to retrieve the latest version information!")
            return None, None

        return tag_name, assets
    except requests.RequestException as e:
        st.error(f"Failed to fetch the latest release: {e}")
        return None, None


def plot_memory_history(data: pd.DataFrame):
    try:

        data["Timestamp"] = pd.to_datetime(data["Timestamp"])

        plt.figure(figsize=(10, 6))
        plt.plot(
            data["Timestamp"],
            data["Free Memory Before"],
            marker="o",
            label="Free Memory Before",
        )
        plt.plot(
            data["Timestamp"],
            data["Free Memory After"],
            marker="o",
            label="Free Memory After",
        )
        plt.plot(
            data["Timestamp"], data["Freed Memory"], marker="o", label="Freed Memory"
        )

        plt.title("Memory Cleanup History")
        plt.xlabel("Timestamp")
        plt.ylabel("Memory (GB)")
        plt.legend()

        plt.gcf().autofmt_xdate()
        plt.tight_layout()

        st.pyplot(plt)
        plt.close()

    except Exception as e:
        st.error(f"Error plotting memory history: {e}")


def run_command(command: List[str]) -> Tuple[str, int]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout, result.returncode
    except Exception as e:
        st.error(f"Command execution error: {e}")
        return str(e), 1


def get_memory_info() -> Tuple[float, float, float, float]:
    try:
        total_memory_output, _ = run_command(
            ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory", "/Value"]
        )
        free_memory_output, _ = run_command(
            ["wmic", "OS", "get", "FreePhysicalMemory", "/Value"]
        )
        cached_memory_output, _ = run_command(
            ["wmic", "OS", "get", "TotalVisibleMemorySize", "/Value"]
        )

        total_memory = int(total_memory_output.split("=")[1]) / (1024**3)
        free_memory_mb = int(free_memory_output.split("=")[1])
        cached_memory = int(cached_memory_output.split("=")[1]) / (1024**3)

        free_memory_gb = free_memory_mb / 1024
        used_memory = max(0, total_memory - free_memory_gb)

        return total_memory, free_memory_gb, cached_memory, used_memory

    except (IndexError, ValueError, Exception) as e:
        st.error(f"Error parsing memory values: {e}")
        return 0, 0, 0, 0


def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
    except subprocess.CalledProcessError:
        return "N/A"


def main():
    local_version = read_local_version()
    latest_version, assets = get_latest_release()

    exe_path = os.path.join(os.getcwd(), "EmptyStandbyList.exe")
    if not os.path.exists(exe_path):
        st.error("Error: EmptyStandbyList.exe not found.")
        if st.button("Download EmptyStandbyList.exe"):
            download_url = "https://github.com/stefanpejcic/EmptyStandbyList/raw/master/EmptyStandbyList.exe"
            try:
                response = requests.get(download_url, timeout=30)
                response.raise_for_status()
                with open(exe_path, "wb") as file:
                    file.write(response.content)
                st.success(
                    "EmptyStandbyList.exe downloaded successfully! Refresh the page to use the program."
                )
            except requests.RequestException as e:
                st.error(f"Failed to download EmptyStandbyList.exe: {e}")
            return

    commands = {
        "modifiedpagelist": "Clear modified page list",
        "standbylist": "Clear standby list",
        "priority0standbylist": "Clear priority 0 standby list",
        "workingsets": "Clear working sets",
    }
    selected_commands = st.multiselect(
        "Select Cleanup Commands", list(commands.keys()), default=list(commands.keys())
    )

    if st.button("Start Cleanup"):
        total_memory, free_memory_before, _, _ = get_memory_info()
        st.write(f"Total Memory: {total_memory:.2f} GB")
        st.write(f"Free Memory before cleanup: {free_memory_before:.2f} GB")

        progress_bar = st.progress(0)
        for i, cmd in enumerate(selected_commands):
            st.write(f"Executing EmptyStandbyList for {commands[cmd]}...")
            output, returncode = run_command([exe_path, cmd])
            progress_bar.progress((i + 1) / len(selected_commands))

            if returncode != 0:
                st.error(f"Error occurred while executing {cmd}. Output: {output}")

        _, free_memory_after, _, _ = get_memory_info()
        st.write(f"Free Memory after cleanup: {free_memory_after:.2f} GB")

        freed_memory = free_memory_after - free_memory_before
        st.write(f"Freed memory: {abs(freed_memory):.2f} GB")

        memory_file_path = os.path.join(DATA_DIR, "memory_usage.csv")
        new_data = pd.DataFrame(
            {
                "Timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Free Memory Before": [f"{free_memory_before:.2f}"],
                "Free Memory After": [f"{free_memory_after:.2f}"],
                "Freed Memory": [f"{abs(freed_memory):.2f}"],
            }
        )

        if os.path.exists(memory_file_path):
            memory_df = pd.read_csv(memory_file_path)
            memory_df = pd.concat([memory_df, new_data], ignore_index=True)
        else:
            memory_df = new_data

        memory_df.to_csv(memory_file_path, index=False)

    st.subheader("Memory Usage History")
    memory_file_path = os.path.join(DATA_DIR, "memory_usage.csv")

    if os.path.exists(memory_file_path):
        try:
            memory_df = pd.read_csv(memory_file_path)
            st.dataframe(memory_df)

            if st.button("Plot Memory Usage"):
                plot_memory_history(memory_df)

        except Exception as e:
            st.error(f"Error reading memory history: {e}")
    else:
        st.write("No memory usage history available.")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Main", "Updates", "Help"])

    # Main tab for other content
    with tab1:
        st.write("**© GrimTech 2007-2024 | PatrickJr.** ❤️ Made with love")

    # Updates tab for version info
    with tab2:
        st.write("**© GrimTech 2007-2024 | PatrickJr.** ❤️ Made with love")
        st.markdown(f"**Commit Hash:** {get_git_commit_hash()}")
        st.markdown(f"**Local Version:** {local_version}")
        
        if latest_version:
            st.markdown(f"**Latest Version:** {latest_version}")
            if local_version != latest_version:
                st.warning("Your application is outdated!")
                release_url = "https://github.com/PatrickJnr/StreamLitMemCleaner/releases/latest"
                st.markdown(f"[Go to the release page to download the latest version]({release_url})")
            else:
                st.success("You are using the latest version.")
        else:
            st.error("Failed to check for updates. Please visit the release page manually.")
        
    # Help tab for guidance
    with tab3:
        st.write("**© GrimTech 2007-2024 | PatrickJr.** ❤️ Made with love")
        st.write(
            """
    - **Memory Monitoring**: This application displays your system's memory usage.
    - **Cleanup Commands**: You can select various cleanup commands to free up memory. These include:
      - Clear modified page list
      - Clear standby list
      - Clear priority 0 standby list
      - Clear working sets
    - **Updating the Application**: If a new version is available, Go to the release page to download the latest version".
    - **Viewing Memory History**: 
      - The memory usage history table shows previous cleanup actions.
      - You can plot this data to visually track memory usage trends.
    """)


if __name__ == "__main__":
    main()
