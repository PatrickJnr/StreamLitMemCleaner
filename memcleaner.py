import datetime
import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, NamedTuple

import pandas as pd
import psutil
import requests
import streamlit as st
from typing_extensions import TypedDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger("memory_cleanup")

# Type definitions
class MemoryInfo(TypedDict):
    total_gb: float
    free_gb: float
    used_gb: float
    percent: float

class CleanupResult(TypedDict):
    success: bool
    memory_before: float
    memory_after: float
    freed_memory: float
    error: Optional[str]

class ReleaseInfo(TypedDict):
    tag_name: Optional[str]
    html_url: Optional[str]
    body: Optional[str]

class CommandResult(NamedTuple):
    stdout: str
    returncode: int

# Enums for better type safety
class CleanupCommand(str, Enum):
    MODIFIED_PAGES = "modifiedpagelist"
    STANDBY_LIST = "standbylist"
    PRIORITY0_STANDBY = "priority0standbylist"
    WORKING_SETS = "workingsets"

class Page(str, Enum):
    HOME = "Home"
    UPDATES = "Updates"
    HELP = "Help"
    CHANGELOG = "Changelog"

# Configuration using dataclasses for better type safety
@dataclass(frozen=True)
class AppConfig:
    title: str = "Memory Cleanup Utility"
    icon: str = "🔧"
    version_file: str = "version.txt"
    copyright: str = "© GrimTech 2007-2024 | PatrickJr. ❤️ Made with love"
    
@dataclass(frozen=True)
class Paths:
    data_dir: Path = Path("data")
    exe: str = "EmptyStandbyList.exe"
    changelog: Path = Path("CHANGELOG.md")
    
    @property
    def exe_full(self) -> Path:
        return Path.cwd() / self.exe
    
    @property
    def memory_csv(self) -> Path:
        return self.data_dir / "memory_usage.csv"
    
    @property
    def version_file(self) -> Path:
        return self.data_dir / APP_CONFIG.version_file

@dataclass(frozen=True)
class Urls:
    github_api: str = "https://api.github.com/repos/PatrickJnr/StreamLitMemCleaner/releases/latest"
    download: str = "https://github.com/stefanpejcic/EmptyStandbyList/raw/master/EmptyStandbyList.exe"

# Create singleton instances
APP_CONFIG = AppConfig()
PATHS = Paths()
URLS = Urls()

# Create data directory if it doesn't exist
PATHS.data_dir.mkdir(exist_ok=True)

# Command descriptions
CLEANUP_DESCRIPTIONS = {
    CleanupCommand.MODIFIED_PAGES: "Clear modified page list",
    CleanupCommand.STANDBY_LIST: "Clear standby list",
    CleanupCommand.PRIORITY0_STANDBY: "Clear priority 0 standby list",
    CleanupCommand.WORKING_SETS: "Clear working sets",
}

# Streamlit page setup
st.set_page_config(
    page_title=APP_CONFIG.title,
    page_icon=APP_CONFIG.icon,
)

# ============ UTILITY CLASSES AND FUNCTIONS ============

class SystemMonitor:
    """Monitors system resources and provides formatted information."""
    
    @staticmethod
    def get_memory_info() -> MemoryInfo:
        """Get the system's memory information."""
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": mem.total / (1024**3),
                "free_gb": mem.available / (1024**3),
                "used_gb": mem.used / (1024**3),
                "percent": mem.percent
            }
        except Exception as e:
            logger.error(f"Error fetching system info: {e}")
            st.error(f"Error fetching system info: {e}")
            return {"total_gb": 0.0, "free_gb": 0.0, "used_gb": 0.0, "percent": 0.0}

    @staticmethod
    def format_memory(value_gb: float) -> str:
        """Format memory value in MB or GB with appropriate units."""
        value_mb = value_gb * 1024
        if value_mb < 1024:
            return f"{value_mb:.2f} MB"
        else:
            return f"{value_gb:.2f} GB"


class CommandExecutor:
    """Executes system commands with proper error handling."""
    
    @staticmethod
    def run(command: List[str]) -> CommandResult:
        """Run a system command and return its output and return code."""
        logger.info(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            return CommandResult(result.stdout, result.returncode)
        except Exception as e:
            error_msg = f"Command execution error: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return CommandResult(str(e), 1)


class MemoryCleanup:
    """Handles memory cleanup operations using external tools."""
    
    def __init__(self, exe_path: Path):
        self.exe_path = exe_path
        
    def execute_cleanup(self, commands: List[CleanupCommand]) -> CleanupResult:
        """Execute cleanup commands and return results."""
        if not self.exe_path.exists():
            error_msg = f"Executable not found at {self.exe_path}"
            logger.error(error_msg)
            st.error(error_msg)
            return {"success": False, "error": error_msg, "memory_before": 0.0, "memory_after": 0.0, "freed_memory": 0.0}
            
        memory_before = SystemMonitor.get_memory_info()["free_gb"]
        logger.info(f"Starting cleanup with free memory: {memory_before:.2f} GB")
        
        progress_bar = st.progress(0)
        for i, cmd in enumerate(commands):
            st.write(f"Executing EmptyStandbyList for {CLEANUP_DESCRIPTIONS[cmd]}...")
            output, returncode = CommandExecutor.run([str(self.exe_path), cmd.value])
            
            if returncode == 0:
                progress_bar.progress((i + 1) / len(commands))
                logger.info(f"Successfully executed {cmd.value}")
            else:
                error_msg = f"Error in {cmd.value}: {output}"
                logger.error(error_msg)
                return {
                    "success": False, 
                    "error": error_msg,
                    "memory_before": memory_before,
                    "memory_after": 0.0,
                    "freed_memory": 0.0
                }
        
        memory_after = SystemMonitor.get_memory_info()["free_gb"]
        freed_memory = memory_after - memory_before
        logger.info(f"Cleanup complete. Memory before: {memory_before:.2f} GB, after: {memory_after:.2f} GB, freed: {freed_memory:.2f} GB")
        
        return {
            "success": True,
            "memory_before": memory_before,
            "memory_after": memory_after,
            "freed_memory": freed_memory,
            "error": None
        }


class MemoryHistoryManager:
    """Manages the history of memory cleanup operations."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        
    def save_record(self, record: CleanupResult) -> bool:
        """Save memory cleanup record to CSV file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = pd.DataFrame({
                "Timestamp": [timestamp],
                "Free Memory Before": [f"{record['memory_before']:.2f}"],
                "Free Memory After": [f"{record['memory_after']:.2f}"],
                "Freed Memory": [f"{abs(record['freed_memory']):.2f}"]
            })
            
            if self.file_path.exists():
                memory_df = pd.read_csv(self.file_path)
                memory_df = pd.concat([memory_df, new_data], ignore_index=True)
            else:
                memory_df = new_data
                
            memory_df.to_csv(self.file_path, index=False)
            logger.info(f"Saved memory record for {timestamp}")
            return True
        except Exception as e:
            error_msg = f"Error saving memory usage history: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return False
            
    def load_history(self) -> Optional[pd.DataFrame]:
        """Load memory usage history from CSV file."""
        if not self.file_path.exists():
            return None
            
        try:
            df = pd.read_csv(self.file_path)
            logger.info(f"Loaded {len(df)} memory history records")
            return df
        except Exception as e:
            error_msg = f"Error reading memory history: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return None
            
    def delete_history(self) -> bool:
        """Delete memory usage history file."""
        try:
            if self.file_path.exists():
                self.file_path.unlink()
                logger.info("Memory history deleted")
                return True
            logger.info("No memory history to delete")
            return False
        except Exception as e:
            error_msg = f"Error deleting memory usage history: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return False
            
    def plot_history(self, data: pd.DataFrame) -> bool:
        """Plot memory usage history."""
        try:
            data["Timestamp"] = pd.to_datetime(data["Timestamp"])
            data.set_index("Timestamp", inplace=True)
            
            # Convert string columns to float for proper plotting
            for col in ['Free Memory Before', 'Free Memory After', 'Freed Memory']:
                data[col] = data[col].astype(float)
                
            st.line_chart(data[['Free Memory Before', 'Free Memory After', 'Freed Memory']])
            logger.info("Memory history plotted successfully")
            return True
        except Exception as e:
            error_msg = f"Error plotting memory history: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return False


class UpdateManager:
    """Manages application updates."""
    
    def __init__(self, version_file: Path, github_api_url: str):
        self.version_file = version_file
        self.github_api_url = github_api_url
        
    def get_local_version(self) -> Optional[str]:
        """Read the local version from a file."""
        try:
            if self.version_file.exists():
                version = self.version_file.read_text().strip()
                logger.info(f"Local version: {version}")
                return version
            logger.info("No local version file found")
            return None
        except Exception as e:
            error_msg = f"Error reading version file: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return None
            
    def get_latest_release(self, timeout: float = 10) -> ReleaseInfo:
        """Fetch the latest release information from GitHub."""
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "StreamLitMemCleanerApp"}
        try:
            logger.info(f"Fetching latest release from {self.github_api_url}")
            response = requests.get(self.github_api_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            release_data = response.json()
            
            tag_name = release_data.get("tag_name")
            if tag_name:
                logger.info(f"Latest version: {tag_name}")
            else:
                logger.warning("No tag name found in release data")
                
            return {
                "tag_name": tag_name,
                "html_url": release_data.get("html_url"),
                "body": release_data.get("body", "No changelog available.")
            }
        except requests.RequestException as e:
            error_msg = f"Failed to fetch the latest release: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return {"tag_name": None, "html_url": None, "body": None}


class ResourceManager:
    """Manages file and network resources."""
    
    @staticmethod
    def download_file(url: str, destination: Path, timeout: int = 30) -> bool:
        """Download a file from URL to destination."""
        try:
            logger.info(f"Downloading file from {url} to {destination}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Ensure parent directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            destination.write_bytes(response.content)
            logger.info(f"File downloaded successfully to {destination}")
            return True
        except requests.RequestException as e:
            error_msg = f"Failed to download file: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return False
    
    @staticmethod
    def load_text_file(file_path: Path, default_message: str = "") -> str:
        """Load text content from a file."""
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return default_message
                
            content = file_path.read_text()
            logger.info(f"Loaded text file: {file_path}")
            return content
        except Exception as e:
            error_msg = f"Error reading file: {e}"
            logger.error(error_msg)
            return error_msg


# ============ UI COMPONENTS ============

class BasePageUI:
    """Base class for all page UIs."""
    
    def render(self) -> None:
        """Render the page UI. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement render()")


class HomePageUI(BasePageUI):
    """UI for the home page."""
    
    def __init__(self, cleanup_manager: MemoryCleanup, history_manager: MemoryHistoryManager):
        self.cleanup_manager = cleanup_manager
        self.history_manager = history_manager
        
    def render(self) -> None:
        """Render the home page UI."""
        # System information section
        st.subheader("System Information")
        system_info_placeholder = st.empty()
        
        def display_system_info() -> None:
            mem_info = SystemMonitor.get_memory_info()
            system_info_placeholder.markdown(f"""
                **Total Memory:** {SystemMonitor.format_memory(mem_info["total_gb"])}
                **Free Memory:** {SystemMonitor.format_memory(mem_info["free_gb"])}
                **Used Memory:** {SystemMonitor.format_memory(mem_info["used_gb"])}
                **Memory Usage:** {mem_info["percent"]:.1f}%
            """)
            
        display_system_info()
        
        if st.button("Refresh System Information"):
            display_system_info()
            
        # Cleanup section
        st.subheader("Memory Cleanup")
        selected_commands = st.multiselect(
            "Select Cleanup Commands", 
            list(CleanupCommand),
            default=list(CleanupCommand),
            format_func=lambda x: CLEANUP_DESCRIPTIONS[x]
        )
        
        if st.button("Start Cleanup"):
            self._handle_cleanup(selected_commands)
                
        # Memory history section
        self._render_memory_history()

    def _handle_cleanup(self, selected_commands: List[CleanupCommand]) -> None:
        """Handle the cleanup process."""
        if not selected_commands:
            st.warning("Please select at least one cleanup command.")
            return
            
        if len(selected_commands) == len(CleanupCommand):
            st.warning("You have selected all cleanup options. Your system may lock up briefly during the cleanup process.")
            
        with st.spinner('Cleaning up memory...'):
            result = self.cleanup_manager.execute_cleanup(selected_commands)
            
            if result["success"]:
                st.write(f"Free Memory before cleanup: {SystemMonitor.format_memory(result['memory_before'])}")
                st.write(f"Free Memory after cleanup: {SystemMonitor.format_memory(result['memory_after'])}")
                freed_memory_abs = abs(result['freed_memory'])
                st.write(f"Freed memory: {SystemMonitor.format_memory(freed_memory_abs)}")
                
                # Add color-coded success message based on amount freed
                if freed_memory_abs > 0.5:  # More than 0.5 GB
                    st.success(f"Successfully freed {SystemMonitor.format_memory(freed_memory_abs)} of memory!")
                elif freed_memory_abs > 0:
                    st.info(f"Freed {SystemMonitor.format_memory(freed_memory_abs)} of memory.")
                else:
                    st.warning("No memory was freed. Your system may already be optimized.")
                
                # Save the record
                self.history_manager.save_record(result)
            else:
                st.error(result["error"])
        
    def _render_memory_history(self) -> None:
        """Render the memory history section."""
        st.subheader("Memory Usage History")
        memory_df = self.history_manager.load_history()
        
        if memory_df is not None and not memory_df.empty:
            # Add controls for sorting and filtering
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox(
                    "Sort by", 
                    ["Timestamp", "Free Memory Before", "Free Memory After", "Freed Memory"],
                    index=0
                )
            with col2:
                ascending = st.checkbox("Ascending", value=False)
            
            # Sort the dataframe
            memory_df = memory_df.sort_values(
                by=sort_by, 
                ascending=ascending,
                key=lambda x: pd.to_numeric(x) if x.name != "Timestamp" else x
            )
            
            # Display with pagination if there are many records
            if len(memory_df) > 10:
                page_size = st.slider("Records per page", min_value=5, max_value=50, value=10, step=5)
                page_number = st.number_input("Page", min_value=1, max_value=max(1, len(memory_df) // page_size + 1), value=1)
                start_idx = (page_number - 1) * page_size
                end_idx = min(start_idx + page_size, len(memory_df))
                st.dataframe(memory_df.iloc[start_idx:end_idx])
                st.write(f"Showing records {start_idx+1} to {end_idx} of {len(memory_df)}")
            else:
                st.dataframe(memory_df)
            
            # Add action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Plot Memory Usage"):
                    self.history_manager.plot_history(memory_df)
            
            with col2:
                if st.button("Delete Memory Usage History"):
                    st.session_state.confirm_delete = True
                    
            if st.session_state.get("confirm_delete"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Delete"):
                        if self.history_manager.delete_history():
                            st.success("Memory usage history deleted successfully.")
                        del st.session_state.confirm_delete
                with col2:
                    if st.button("Cancel"):
                        del st.session_state.confirm_delete
        else:
            st.info("No memory usage history available. Run a cleanup to start tracking results.")


class UpdatesPageUI(BasePageUI):
    """UI for the updates page."""
    
    def __init__(self, update_manager: UpdateManager):
        self.update_manager = update_manager
        
    def render(self) -> None:
        """Render the updates page UI."""
        st.subheader("Version Check")
        
        local_version = self.update_manager.get_local_version()
        st.markdown(f"**Local Version:** {local_version or 'Not installed'}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check for Updates"):
                self._check_for_updates(local_version)
                
        with col2:
            if st.button("Refresh Local Version"):
                st.rerun()
    
    def _check_for_updates(self, local_version: Optional[str]) -> None:
        """Check for updates and display results."""
        with st.spinner("Checking for updates..."):
            release_info = self.update_manager.get_latest_release()
            tag_name = release_info["tag_name"]
            
            if tag_name:
                if not local_version:
                    st.warning(f"No local version found. Latest version is {tag_name}.")
                    st.markdown(f"[Download the latest release]({release_info['html_url']})")
                elif local_version != tag_name:
                    st.warning(f"A new version is available: {tag_name}!")
                    st.markdown(f"[Go to the release page]({release_info['html_url']})")
                    
                    if release_info["body"]:
                        with st.expander("Release Notes"):
                            st.markdown(release_info["body"])
                else:
                    st.success(f"You are using the latest version ({tag_name}).")
            else:
                st.error("Failed to check for updates. Please try again later.")


class HelpPageUI(BasePageUI):
    """UI for the help page."""
    
    def render(self) -> None:
        """Render the help page UI."""
        st.subheader("Help Section")
        
        # Tabs for different help sections
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Cleanup Commands", "Memory History", "Updates"])
        
        with tab1:
            st.markdown("""
                ### Memory Cleanup Utility
                
                This application helps optimize your system's memory usage by clearing various
                memory lists and caches. Regular use can help keep your system responsive,
                especially during memory-intensive tasks.
                
                ### System Requirements
                
                - Windows operating system (Windows 10/11 recommended)
                - Administrative privileges (for some cleanup operations)
                - Internet connection (for updates)
            """)
        
        with tab2:
            st.markdown("""
                ### Cleanup Commands
                
                - **Clear modified page list**: Removes modified pages that have not yet been written to disk.
                  *Use when*: System feels sluggish after heavy disk operations.
                
                - **Clear standby list**: Clears memory pages that are no longer in use but kept in RAM for quick access.
                  *Use when*: You want to free up memory for new applications.
                
                - **Clear priority 0 standby list**: Targets only the lowest priority memory pages in the standby list.
                  *Use when*: You want a lighter cleanup that only removes least-needed cached data.
                
                - **Clear working sets**: Frees memory from applications that are currently inactive.
                  *Use when*: You have many open applications but only actively using a few.
                
                > **Note**: Using all options simultaneously may cause your system to briefly freeze 
                > while memory is being reorganized.
            """)
        
        with tab3:
            st.markdown("""
                ### Memory History
                
                The application keeps track of all cleanup operations, including:
                
                - When the cleanup was performed
                - How much memory was free before cleanup
                - How much memory was free after cleanup
                - Total amount of memory freed
                
                You can:
                - View and sort this history
                - Plot trends over time to analyze your system's memory behavior
                - Delete history if needed
                
                This data can help you understand your system's memory patterns and determine
                the most effective cleanup strategies for your specific usage.
            """)
            
        with tab4:
            st.markdown("""
                ### Updates
                
                The application can check for new versions that may include:
                
                - Bug fixes
                - Performance improvements
                - New features
                
                When a new version is available, you'll see a link to download it.
                
                > **Tip**: Check for updates regularly to ensure you have the latest features
                > and security improvements.
            """)


class ChangelogPageUI(BasePageUI):
    """UI for the changelog page."""
    
    def __init__(self, changelog_path: Path):
        self.changelog_path = changelog_path
        
    def render(self) -> None:
        """Render the changelog page UI."""
        st.subheader("Changelog")
        
        changelog_content = ResourceManager.load_text_file(
            self.changelog_path, 
            default_message="Changelog not found. This may be a new installation."
        )
        
        if changelog_content:
            st.markdown(changelog_content)
        else:
            st.info("No changelog available. Check the GitHub repository for release information.")


# ============ MAIN APPLICATION ============

class SessionState:
    """Manages session state variables."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize session state variables."""
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        if "page" not in st.session_state:
            st.session_state.page = Page.HOME


class MemoryCleanupApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.title = APP_CONFIG.title
        
        # Initialize managers
        self.update_manager = UpdateManager(PATHS.version_file, URLS.github_api)
        self.cleanup_manager = MemoryCleanup(PATHS.exe_full)
        self.history_manager = MemoryHistoryManager(PATHS.memory_csv)
        
        # Initialize UI components
        self.ui_components = {
            "Home": HomePageUI(self.cleanup_manager, self.history_manager),
            "Updates": UpdatesPageUI(self.update_manager),
            "Help": HelpPageUI(),
            "Changelog": ChangelogPageUI(PATHS.changelog)
        }
        
        # Initialize session state
        SessionState.initialize()
        
    def check_dependencies(self) -> bool:
        """Check if all dependencies are available."""
        if not PATHS.exe_full.exists():
            st.error(f"Error: {PATHS.exe} not found.")
            st.info(f"This application requires {PATHS.exe} to clean memory.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Download {PATHS.exe}"):
                    with st.spinner(f"Downloading {PATHS.exe}..."):
                        if ResourceManager.download_file(URLS.download, PATHS.exe_full):
                            st.success(f"{PATHS.exe} downloaded successfully!")
                            st.button("Refresh Application", on_click=st.experimental_rerun)
                        return False
            with col2:
                if st.button("Learn More"):
                    st.markdown("""
                        **EmptyStandbyList** is a command-line utility that helps free up 
                        memory on Windows systems by clearing various memory caches.
                        
                        It's created by [Wj32](https://wj32.org/wp/software/empty-standby-list/) 
                        and is commonly used for system optimization.
                    """)
            return False
        return True
        
    def run(self) -> None:
        """Run the main application."""
        st.title(self.title)
        
        # Check dependencies first
        if not self.check_dependencies():
            return
            
        # Sidebar navigation
        st.sidebar.title("Navigation")
        selected_page = st.sidebar.radio(
            "Go to", 
            ["Home", "Updates", "Help", "Changelog"],
            index=["Home", "Updates", "Help", "Changelog"].index(st.session_state.page) if "page" in st.session_state else 0
        )
        
        # Update session state
        st.session_state.page = selected_page
        
        # Render the selected page
        self.ui_components[selected_page].render()
            
        # Footer
        st.write("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(APP_CONFIG.copyright)
        with col2:
            st.write(f"{self.update_manager.get_local_version() or 'dev'}")


# Run the application
if __name__ == "__main__":
    try:
        logger.info("Starting Memory Cleanup Utility")
        app = MemoryCleanupApp()
        app.run()
        logger.info("Application closed")
    except Exception as e:
        logger.critical(f"Critical application error: {e}", exc_info=True)
        st.error(f"An unexpected error occurred: {e}")
        st.error("Please check the log file for details or report this issue.")