import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GitAnalysisConfig:
    """Configuration class for Git Analysis project"""

    def __init__(self):
        # API Keys
        self.api_key = os.getenv("API_KEY")

        # Base directories
        self.base_dir = Path(__file__).resolve().parent.parent
        self.repos_dir = self.base_dir / "cloned_repos"
        self.summaries_dir = self.base_dir / "summaries"
        self.git_history_dir = self.base_dir / "git_file_history_output"
        self.vector_db_dir = self.base_dir / "faiss_repo_knowledge"

        # Create directories if they don't exist
        self._create_directories()

        # Model configurations
        self.llm_model = "models/gemini-1.5-flash"
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        self.repos_dir.mkdir(exist_ok=True)
        self.summaries_dir.mkdir(exist_ok=True)
        self.git_history_dir.mkdir(exist_ok=True)
        self.vector_db_dir.mkdir(exist_ok=True)

    def get_repo_path(self, repo_name):
        """Get the full path to a repository"""
        return self.repos_dir / repo_name


class GitProjectState:
    """Class to manage the state of the current git project analysis"""

    def __init__(self):
        self.current_repo_name = None
        self.current_repo_path = None
        self.analysis_complete = False
        self.vector_db_loaded = False
        self.state_file = Path(__file__).resolve().parent.parent / "project_state.json"

        # Load state if exists
        self.load_state()

    def update_repo(self, repo_name, repo_path):
        """Update the current repository information"""
        self.current_repo_name = repo_name
        self.current_repo_path = repo_path
        self.analysis_complete = False
        self.vector_db_loaded = False
        self.save_state()

    def mark_analysis_complete(self):
        """Mark that the repository analysis is complete"""
        self.analysis_complete = True
        self.save_state()

    def mark_vector_db_loaded(self):
        """Mark that the vector database is loaded"""
        self.vector_db_loaded = True
        self.save_state()

    def save_state(self):
        """Save the current state to disk"""
        state_data = {
            "current_repo_name": self.current_repo_name,
            "current_repo_path": self.current_repo_path,
            "analysis_complete": self.analysis_complete,
            "vector_db_loaded": self.vector_db_loaded,
        }

        with open(self.state_file, "w") as f:
            json.dump(state_data, f)

    def load_state(self):
        """Load state from disk if it exists"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state_data = json.load(f)

                self.current_repo_name = state_data.get("current_repo_name")
                self.current_repo_path = state_data.get("current_repo_path")
                self.analysis_complete = state_data.get("analysis_complete", False)
                self.vector_db_loaded = state_data.get("vector_db_loaded", False)

                logger.info(f"Loaded project state: {self.current_repo_name}")
            except Exception as e:
                logger.error(f"Error loading project state: {e}")


def extract_github_url(text):
    """Extract GitHub URL from text"""
    import re

    url_match = re.search(r"https?://github\.com/[^\s]+", text)
    if url_match:
        # Clean up the URL in case it has trailing characters
        url = url_match.group(0)
        # Remove any trailing punctuation
        url = url.rstrip(",.;:!?\"'\\/)")
        return url
    return None


def is_binary_file(file_path):
    """Check if a file is binary by extension"""
    binary_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".exe",
        ".dll",
        ".bin",
        ".zip",
        ".tar",
        ".gz",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    ]
    return Path(file_path).suffix.lower() in binary_extensions


def count_files_in_directory(directory, skip_binary=True):
    """Count the number of files in a directory recursively"""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not skip_binary or not is_binary_file(file_path):
                count += 1
    return count
