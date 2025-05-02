import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool, Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Optional, Dict, Any, List
from datetime import datetime

import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage, HumanMessage

# At the top of your settings.py, before the dotenv import
import sys

print("Python path:", sys.path)

# Then try your import
try:
    from dotenv import load_dotenv

    print("Successfully imported dotenv!")
except ImportError as e:
    print(f"Failed to import dotenv: {e}")
    print("Python path:", sys.path)

api_key = os.getenv("API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
# )

from pydriller import Repository


print("Starting repository traversal...")

import os
import json
import re
from git import Repo
from collections import defaultdict

# Path to your cloned Git repository
repo_path = "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/turning-ideas"  # <<< CHANGE THIS
output_folder = "git_file_history_output"  # Where to store output
os.makedirs(output_folder, exist_ok=True)

repo = Repo(repo_path)

NULL_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

# This will store commits per file
file_commit_data = defaultdict(list)


# Safe folder name maker (remove / \ : * ? " < > |)
def safe_folder_name(name):
    return re.sub(r'[\/:*?"<>|]', "_", name)


# Loop through commits
for commit in repo.iter_commits("--all"):
    parents = commit.parents or []

    if not parents:
        files_changed = repo.git.diff(
            NULL_TREE, commit.hexsha, name_only=True
        ).splitlines()
    else:
        files_changed = repo.git.diff(
            parents[0].hexsha, commit.hexsha, name_only=True
        ).splitlines()

    for file_path in files_changed:
        # Now get the diff for this specific file
        if not parents:
            diff_text = repo.git.diff(NULL_TREE, commit.hexsha, "--", file_path)
        else:
            diff_text = repo.git.diff(parents[0].hexsha, commit.hexsha, "--", file_path)

        file_commit_data[file_path].append(
            {
                "commit_time": commit.committed_datetime.isoformat(),
                "commit_hash": commit.hexsha,
                "commit_message": commit.message.strip(),
                "diff": diff_text,
            }
        )

# Now write output
for file_path, commits in file_commit_data.items():
    # Sort by time
    commits.sort(key=lambda x: x["commit_time"])

    # Create a folder for each file
    safe_name = safe_folder_name(file_path)
    full_folder_path = os.path.join(output_folder, safe_name)
    os.makedirs(full_folder_path, exist_ok=True)

    # Save JSON file
    json_path = os.path.join(full_folder_path, "commit_history.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=2, ensure_ascii=False)

print(f"Done! Output saved to: {output_folder}")
