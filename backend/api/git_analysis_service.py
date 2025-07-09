import subprocess
import logging
import time
import json
import os
from pathlib import Path
from git import Repo
from collections import defaultdict
import re

from .utils import GitAnalysisConfig, GitProjectState, is_binary_file, is_asset_file
from langchain_google_genai import ChatGoogleGenerativeAI

# Set up logging
logger = logging.getLogger(__name__)
logging.getLogger("faiss").setLevel(logging.ERROR)

# Load configuration
config = GitAnalysisConfig()


class GitAnalysisService:
    """Service for Git repository analysis"""

    def __init__(self):
        self.config = GitAnalysisConfig()
        self.state = GitProjectState()
        self._setup_intent_classifier()
        # Create a file index to help with retrieval
        self.file_index = {}

    def _setup_intent_classifier(self):
        """Setup the intent classifier to determine if a message is requesting git analysis"""
        self.intent_llm = self.get_llm(temperature=0.1)

    def _summarize_diff(self, diff_text):
        """Analyze a diff text and create a concise summary of the changes"""
        # Parse additions and deletions
        added_lines = []
        removed_lines = []

        for line in diff_text.split("\n"):
            line = line.strip()
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                removed_lines.append(line[1:])

        # Analyze the changes
        summary = {}

        # Count meaningful changes (ignore whitespace-only changes)
        meaningful_additions = [line for line in added_lines if line.strip()]
        meaningful_deletions = [line for line in removed_lines if line.strip()]

        summary["lines_added"] = len(meaningful_additions)
        summary["lines_removed"] = len(meaningful_deletions)

        # Detect the type of change
        if summary["lines_added"] > 0 and summary["lines_removed"] == 0:
            summary["change_type"] = "Addition only"
        elif summary["lines_added"] == 0 and summary["lines_removed"] > 0:
            summary["change_type"] = "Deletion only"
        elif summary["lines_added"] > 0 and summary["lines_removed"] > 0:
            summary["change_type"] = "Modification"
        else:
            summary["change_type"] = "No meaningful changes"

        # Analyze function changes for code files
        function_pattern = r"[+-][\s]*(def|function|class|method)\s+([a-zA-Z0-9_]+)"
        function_matches = re.findall(function_pattern, diff_text)

        if function_matches:
            summary["function_changes"] = []
            for match in function_matches:
                func_type, func_name = match
                summary["function_changes"].append(f"{func_type} {func_name}")

        # Look for significant additions
        significant_added = []
        for line in meaningful_additions:
            # Look for non-comment, non-whitespace code with substantial content
            if len(line.strip()) > 10 and not line.strip().startswith(
                ("//", "#", "/*", "*", "<!--")
            ):
                significant_added.append(line.strip())

        if significant_added:
            # Only keep a limited sample of significant lines
            summary["significant_additions"] = significant_added[:5]

        # Look for significant deletions
        significant_deleted = []
        for line in meaningful_deletions:
            # Look for non-comment, non-whitespace code with substantial content
            if len(line.strip()) > 10 and not line.strip().startswith(
                ("//", "#", "/*", "*", "<!--")
            ):
                significant_deleted.append(line.strip())

        if significant_deleted:
            # Only keep a limited sample of significant lines
            summary["significant_deletions"] = significant_deleted[:5]

        return summary

    def detect_analysis_intent(self, message):
        """
        Detect if the message is requesting git repository analysis
        Returns: tuple (is_analysis_intent, extracted_url)
        """
        from .utils import extract_github_url

        # First check for GitHub URL
        github_url = extract_github_url(message)
        if not github_url:
            return False, None

        # If URL exists, use LLM to determine intent
        prompt = f"""
        Determine if the following message is asking to analyze, clone, or examine a GitHub repository.
        Answer only YES or NO.
        
        Message: {message}
        
        Does this message indicate that the user wants to analyze a GitHub repository?
        """

        try:
            response = self.intent_llm.invoke(prompt)
            is_analysis_intent = "YES" in response.content.strip().upper()
            return is_analysis_intent, github_url
        except Exception as e:
            logger.error(f"Error detecting analysis intent: {e}")
            # If error in classification, default to True if URL exists
            return True, github_url

    def get_llm(self, temperature=0.0):
        """Get a new LLM instance"""
        return ChatGoogleGenerativeAI(
            model=self.config.llm_model,
            api_key=self.config.api_key,
            temperature=temperature,
        )

    def clone_repository(self, repo_url):
        """Clone a Git repository"""
        logger.info(f"Starting to clone repository: {repo_url}")
        try:
            if not repo_url.startswith("http"):
                return False, "Please provide a valid Git repository URL."

            repo_name = repo_url.strip().split("/")[-1].replace(".git", "")
            repo_path = self.config.repos_dir / repo_name

            if repo_path.exists():
                logger.info(f"Repository already exists at {repo_path}")
                self.state.update_repo(repo_name, str(repo_path))
                return True, str(repo_path)

            subprocess.run(["git", "clone", repo_url, str(repo_path)], check=True)
            logger.info(f"Successfully cloned repository to: {repo_path}")

            self.state.update_repo(repo_name, str(repo_path))
            return True, str(repo_path)

        except subprocess.CalledProcessError as e:
            logger.error(f"Error cloning repository: {e}")
            return False, f"Error cloning repository: {e}"

    def analyze_git_history(self):
        """Analyze git history of the current repository with improved metadata storage"""
        if not self.state.current_repo_path:
            return False, "No repository currently loaded"

        repo_path = self.state.current_repo_path
        logger.info(f"Starting repository history analysis for: {repo_path}")

        try:
            # Clear previous output
            for file in self.config.git_history_dir.iterdir():
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    import shutil

                    shutil.rmtree(file)

            repo = Repo(repo_path)
            try:
                NULL_TREE = repo.git.hash_object("-t", "tree", "/dev/null")
                logger.info(f"Computed NULL_TREE hash: {NULL_TREE}")
            except Exception as e:
                # Fallback to the standard empty tree hash if command fails
                NULL_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
                logger.warning(f"Using default NULL_TREE hash: {NULL_TREE}. Error: {e}")

            # Global repository commit data
            repo_commits = []
            file_commit_data = defaultdict(list)
            commit_file_map = {}  # Map of commit hash to files changed

            i = 0
            # Loop through commits in chronological order
            for commit in list(repo.iter_commits("--all", reverse=True)):
                i += 1
                parents = commit.parents or []
                commit_hash = commit.hexsha
                commit_info = {
                    "commit_hash": commit_hash,
                    "commit_time": commit.committed_datetime.isoformat(),
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "commit_message": commit.message.strip(),
                    "files_changed": [],
                    "graph_path": None,  # Will store path to generated graphs
                }

                # Track files changed in this commit
                files_changed = []

                if not parents:
                    files_changed = repo.git.diff(
                        NULL_TREE, commit_hash, name_only=True
                    ).splitlines()
                else:
                    files_changed = repo.git.diff(
                        parents[0].hexsha, commit_hash, name_only=True
                    ).splitlines()

                # Add files to the commit info
                commit_info["files_changed"] = files_changed
                commit_file_map[commit_hash] = files_changed

                # Save overall commit info
                repo_commits.append(commit_info)

                # Process each changed file
                for file_path in files_changed:
                    # Now get the diff for this specific file
                    if not parents:
                        diff_text = repo.git.diff(
                            NULL_TREE, commit_hash, "--", file_path
                        )
                    else:
                        diff_text = repo.git.diff(
                            parents[0].hexsha, commit_hash, "--", file_path
                        )

                    # Extract just what changed (without redundancy)
                    change_summary = self._analyze_diff_content(diff_text)
                    # Store file commit data with minimal redundancy
                    file_commit_record = {
                        "commit_time": commit.committed_datetime.isoformat(),
                        "commit_hash": commit_hash,
                        "commit_message": commit.message.strip(),
                        "author": f"{commit.author.name} <{commit.author.email}>",
                        "file_name_modified": file_path,
                        "commit_history_index": i,
                        "change_summary": change_summary,
                    }

                    # Store diff text only if needed for complex changes that can't be fully captured in summary
                    # if change_summary["change_type"] == "modification" and (
                    #     len(change_summary["functions_modified"]) > 0
                    #     or len(change_summary["classes_modified"]) > 0
                    # ):
                    #     file_commit_record["diff"] = diff_text

                    file_commit_data[file_path].append(file_commit_record)

                # Generate graphs for this commit
                graphs = self.config.git_history_dir / "graphs"
                graphs.mkdir(parents=True, exist_ok=True)

                graph_dir = (
                    self.config.git_history_dir
                    / "graphs"
                    / f"{i}_commit_{commit_hash[:8]}_graphs"
                )
                graph_dir.mkdir(exist_ok=True)
                self._generate_commit_graphs(commit_hash, commit_file_map, graph_dir)
                commit_info["graph_path"] = str(graph_dir)

            # Save all repository commits in chronological order
            repo_info = {
                "repo_name": os.path.basename(repo_path),
                "commit_count": len(repo_commits),
                "first_commit_date": (
                    repo_commits[0]["commit_time"] if repo_commits else None
                ),
                "last_commit_date": (
                    repo_commits[-1]["commit_time"] if repo_commits else None
                ),
                "commits": repo_commits,
                "commit_file_map": commit_file_map,
            }

            # Save repo commit history
            repo_history_path = self.config.git_history_dir / "repo_history.json"
            with open(repo_history_path, "w", encoding="utf-8") as f:
                json.dump(repo_info, f, indent=2, ensure_ascii=False)

            # Safe folder name maker
            def safe_folder_name(name):
                return re.sub(r'[\/:*?"<>|]', "_", name)

            # Now write per-file output
            for file_path, commits in file_commit_data.items():
                # Sort by time
                commits.sort(key=lambda x: x["commit_time"])

                # Create a folder for each file
                safe_name = safe_folder_name(file_path)
                full_folder_path = self.config.git_history_dir / safe_name
                full_folder_path.mkdir(exist_ok=True)

                # Add cumulative file insights by analyzing sequential changes
                self._analyze_file_evolution(commits)

                # Add file information to the JSON structure
                file_info = {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_extension": os.path.splitext(file_path)[1],
                    "commit_count": len(commits),
                    "first_commit_date": commits[0]["commit_time"] if commits else None,
                    "last_commit_date": commits[-1]["commit_time"] if commits else None,
                    "commits": commits,
                }

                # Save JSON file
                json_path = full_folder_path / "commit_history.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(file_info, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Git history analysis complete. Output saved to: {self.config.git_history_dir}"
            )
            return (
                True,
                f"Git history analysis complete. Found history for {len(file_commit_data)} files across {len(repo_commits)} commits.",
            )

        except Exception as e:
            logger.error(f"Error analyzing git history: {e}")
            return False, f"Error analyzing git history: {e}"

    def _analyze_file_evolution(self, commits):
        """Analyze the evolution of a file across multiple commits"""
        if not commits:
            return

        # Initialize tracking variables
        current_functions = set()
        current_classes = set()
        current_imports = set()

        # Process commits in chronological order to track evolution
        for i, commit in enumerate(commits):
            summary = commit["change_summary"]

            # Update tracked elements
            if "functions_added" in summary:
                current_functions.update(summary["functions_added"])
            if "functions_removed" in summary:
                current_functions.difference_update(summary["functions_removed"])

            if "classes_added" in summary:
                current_classes.update(summary["classes_added"])
            if "classes_removed" in summary:
                current_classes.difference_update(summary["classes_removed"])

            if "imports_added" in summary:
                current_imports.update(summary["imports_added"])
            if "imports_removed" in summary:
                current_imports.difference_update(summary["imports_removed"])

            # Add state after this commit
            commit["cumulative_state"] = {
                "functions": list(current_functions),
                "classes": list(current_classes),
                "imports": list(current_imports),
            }

            # For all but the first commit, compute what changed since previous
            if i > 0:
                prev = commits[i - 1].get("cumulative_state", {})
                curr = commit["cumulative_state"]

                # Check what's new compared to previous state
                commit["evolution"] = {
                    "new_functions": [
                        f
                        for f in curr["functions"]
                        if f not in prev.get("functions", [])
                    ],
                    "new_classes": [
                        c for c in curr["classes"] if c not in prev.get("classes", [])
                    ],
                    "new_imports": [
                        imp
                        for imp in curr["imports"]
                        if imp not in prev.get("imports", [])
                    ],
                }

    def _generate_commit_graphs(self, commit_hash, commit_file_map, output_dir):
        """Generate dependency graphs for a specific commit with cumulative dependencies"""
        from pathlib import Path
        import networkx as nx
        import matplotlib.pyplot as plt
        import os

        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)

        # Get the repo object
        repo = Repo(self.state.current_repo_path)

        # Get files changed in this commit
        files_in_commit = commit_file_map.get(commit_hash, [])

        # Checkout the commit to read actual file state at this commit
        current_branch = repo.active_branch.name
        try:
            # Checkout the commit
            repo.git.checkout(commit_hash)

            # Initialize dependency tracking
            file_dependencies = {}
            function_dependencies = {}

            # Process each file in the repository at this commit point
            for root, dirs, files in os.walk(self.state.current_repo_path):
                # Skip hidden directories and git directory
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != ".git"]

                for filename in files:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.state.current_repo_path)

                    # Skip binary files and non-code files
                    if is_binary_file(file_path) or is_asset_file(file_path):
                        continue

                    # Read the content of the file
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        # Skip empty files or very large files
                        if (
                            not content or len(content) > 100000
                        ):  # Skip files larger than 100KB
                            continue

                        # Extract file dependencies
                        file_deps = self._extract_file_dependencies(rel_path, content)
                        file_dependencies[rel_path] = file_deps

                        # Extract function dependencies
                        if rel_path.endswith((".py", ".js", ".jsx", ".ts", ".tsx")):
                            func_deps = self._extract_function_dependencies(
                                rel_path, content
                            )
                            function_dependencies[rel_path] = func_deps

                    except Exception as e:
                        logger.warning(
                            f"Error processing file {rel_path} at commit {commit_hash}: {e}"
                        )

            # Now generate graphs based on the complete repository state at this commit

            # 1. File dependency graph
            file_graph = self._build_file_dependency_graph(file_dependencies)
            file_graph_path = output_dir / f"file_dependency_{commit_hash[:8]}.png"
            self._save_graph(file_graph, file_graph_path, "File Dependencies")

            # 2. Function call graph
            func_graph = self._build_function_dependency_graph(function_dependencies)
            func_graph_path = output_dir / f"function_dependency_{commit_hash[:8]}.png"
            self._save_graph(func_graph, func_graph_path, "Function Call Dependencies")

            # Store the dependency data for future reference
            dependency_data = {
                "file_dependencies": file_dependencies,
                "function_dependencies": function_dependencies,
            }

            # Save dependency data as JSON
            import json

            with open(
                output_dir / f"dependencies_{commit_hash[:8]}.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(dependency_data, f, indent=2, ensure_ascii=False)

        finally:
            # Always restore the original branch
            repo.git.checkout(current_branch)

        return str(output_dir)

    def _extract_file_dependencies(self, file_path, content):
        """Extract file dependencies from file content"""
        dependencies = {"imports": [], "imported_by": [], "references": []}

        file_ext = os.path.splitext(file_path)[1].lower()

        # Python file dependencies
        if file_ext == ".py":
            # Regular imports
            import_patterns = [
                re.compile(
                    r"^import\s+([^\s,;]+)(?:\s*,\s*([^\s,;]+))*", re.MULTILINE
                ),  # import x, y
                re.compile(
                    r"^from\s+([^\s]+)\s+import\s+([^#\n]+)", re.MULTILINE
                ),  # from x import y
            ]

            for pattern in import_patterns:
                for match in pattern.finditer(content):
                    if match.group(0).startswith("from"):
                        module = match.group(1).strip()
                        # Check if it's a relative import
                        if module.startswith("."):
                            # Convert relative import to potential file path
                            relative_path = os.path.normpath(
                                os.path.join(
                                    os.path.dirname(file_path),
                                    module.strip(".").replace(".", "/"),
                                )
                            )
                            if module.strip("."):  # Not just '.'
                                dependencies["imports"].append(f"{relative_path}.py")
                        else:
                            # Handle absolute imports
                            if "." in module and not module.startswith(
                                ("os", "sys", "re", "json")
                            ):
                                # Could be a project module
                                module_path = module.replace(".", "/") + ".py"
                                dependencies["imports"].append(module_path)
                    else:
                        # Handle 'import x' or 'import x, y, z'
                        for i in range(
                            1, match.lastindex + 1 if match.lastindex else 2
                        ):
                            if match.group(i):
                                module = match.group(i).strip()
                                if "." in module and not module.startswith(
                                    ("os", "sys", "re", "json")
                                ):
                                    module_path = module.replace(".", "/") + ".py"
                                    dependencies["imports"].append(module_path)

        # JavaScript/TypeScript file dependencies
        elif file_ext in [".js", ".jsx", ".ts", ".tsx"]:
            import_patterns = [
                re.compile(
                    r'import\s+(?:{[^}]+}|[^{}\s]+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                    re.MULTILINE,
                ),  # import x from 'y'
                re.compile(r'import\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),  # import 'x'
                re.compile(
                    r'require\([\'"]([^\'"]+)[\'"]\)', re.MULTILINE
                ),  # require('x')
            ]

            for pattern in import_patterns:
                for match in pattern.finditer(content):
                    module_path = match.group(1).strip()

                    # Filter out node_modules and external packages
                    if (
                        module_path.startswith("./")
                        or module_path.startswith("../")
                        or not ("/" in module_path and not module_path.startswith("@"))
                    ):

                        # Normalize the path
                        normalized_path = os.path.normpath(
                            os.path.join(os.path.dirname(file_path), module_path)
                        )

                        # Add potential extensions if missing
                        if not os.path.splitext(normalized_path)[1]:
                            for ext in [".js", ".jsx", ".ts", ".tsx"]:
                                dependencies["imports"].append(normalized_path + ext)
                        else:
                            dependencies["imports"].append(normalized_path)

        return dependencies

    def _extract_function_dependencies(self, file_path, content):
        """Extract function dependencies from file content"""
        function_info = {
            "functions": [],
            "function_calls": {},  # function -> [called functions]
            "called_by": {},  # function -> [calling functions]
        }

        file_ext = os.path.splitext(file_path)[1].lower()

        # Python function extraction
        if file_ext == ".py":
            # Find all function definitions
            function_pattern = re.compile(
                r"^def\s+([a-zA-Z0-9_]+)\s*\([^)]*\):", re.MULTILINE
            )
            functions = [m.group(1) for m in function_pattern.finditer(content)]
            function_info["functions"] = functions

            # For each function, find calls to other functions
            for func_name in functions:
                # Find the function body
                func_pattern = re.compile(
                    r"def\s+"
                    + re.escape(func_name)
                    + r"\s*\([^)]*\):\s*(.*?)(?=\n\S|$)",
                    re.DOTALL,
                )
                func_matches = func_pattern.findall(content)

                if func_matches:
                    func_body = func_matches[0]
                    calls = []

                    # Look for calls to other functions
                    for other_func in functions:
                        if other_func != func_name and re.search(
                            r"\b" + re.escape(other_func) + r"\s*\(", func_body
                        ):
                            calls.append(other_func)

                            # Track who calls whom
                            if other_func not in function_info["called_by"]:
                                function_info["called_by"][other_func] = []
                            function_info["called_by"][other_func].append(func_name)

                    if calls:
                        function_info["function_calls"][func_name] = calls

        # JavaScript/TypeScript function extraction
        elif file_ext in [".js", ".jsx", ".ts", ".tsx"]:
            # Various patterns to catch JS function definitions
            function_patterns = [
                re.compile(
                    r"function\s+([a-zA-Z0-9_$]+)\s*\(", re.MULTILINE
                ),  # function x()
                re.compile(
                    r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
                    re.MULTILINE,
                ),  # const x = () =>
                re.compile(
                    r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*function", re.MULTILINE
                ),  # const x = function
                re.compile(
                    r"([a-zA-Z0-9_$]+)\s*:\s*function", re.MULTILINE
                ),  # x: function
                re.compile(
                    r"([a-zA-Z0-9_$]+)\([^)]*\)\s*{", re.MULTILINE
                ),  # x() { (method)
            ]

            # Collect all function definitions
            functions = []
            for pattern in function_patterns:
                funcs = [m.group(1) for m in pattern.finditer(content)]
                functions.extend(funcs)

            # Remove duplicates
            functions = list(set(functions))
            function_info["functions"] = functions

            # Simplified function call analysis (for a more accurate analysis, we'd need AST parsing)
            for func_name in functions:
                # Find potential calls to other functions
                # This is a simplified approach; real JS analysis would be more complex
                calls = []
                for other_func in functions:
                    if other_func != func_name and re.search(
                        r"\b" + re.escape(other_func) + r"\s*\(", content
                    ):
                        calls.append(other_func)

                        # Track who calls whom
                        if other_func not in function_info["called_by"]:
                            function_info["called_by"][other_func] = []
                        function_info["called_by"][other_func].append(func_name)

                if calls:
                    function_info["function_calls"][func_name] = calls

        return function_info

    def _build_file_dependency_graph(self, file_dependencies):
        """Build file dependency graph from extracted dependencies"""
        import networkx as nx

        G = nx.DiGraph()

        # Add nodes for all files
        for file_path in file_dependencies:
            # Add node with file extension as attribute
            ext = os.path.splitext(file_path)[1].lower()
            G.add_node(file_path, type="file", extension=ext)

        # Add edges based on imports
        for file_path, deps in file_dependencies.items():
            for imported_file in deps["imports"]:
                # Check if the imported file exists in our dependency map
                if imported_file in file_dependencies:
                    G.add_edge(file_path, imported_file)

                    # Also update the imported_by list for cross-reference
                    if file_path not in file_dependencies[imported_file]["imported_by"]:
                        file_dependencies[imported_file]["imported_by"].append(
                            file_path
                        )

        return G

    def _build_function_dependency_graph(self, function_dependencies):
        """Build function call graph from extracted dependencies"""
        import networkx as nx

        G = nx.DiGraph()

        # Track all functions across files
        all_functions = {}  # file_path:function_name -> node_id

        # Add nodes for all functions
        for file_path, func_info in function_dependencies.items():
            for func_name in func_info["functions"]:
                # Create unique identifier for this function
                node_id = f"{file_path}:{func_name}"
                G.add_node(node_id, function=func_name, file=file_path)
                all_functions[node_id] = func_name

        # Add edges based on function calls
        for file_path, func_info in function_dependencies.items():
            for caller, callees in func_info["function_calls"].items():
                caller_id = f"{file_path}:{caller}"

                for callee in callees:
                    callee_id = f"{file_path}:{callee}"  # Default to same file

                    # Check if the callee exists in this file
                    if callee_id in all_functions:
                        G.add_edge(caller_id, callee_id)
                    else:
                        # If not found in this file, it might be from another file
                        # This is a simplified approach; actual cross-file function resolution would be more complex
                        for other_file, other_info in function_dependencies.items():
                            if (
                                other_file != file_path
                                and callee in other_info["functions"]
                            ):
                                other_callee_id = f"{other_file}:{callee}"
                                G.add_edge(caller_id, other_callee_id)
                                break

        return G

    def _save_graph(self, G, output_path, title):
        """Save a graph visualization to file"""
        import matplotlib

        # Set non-interactive backend to avoid GUI thread issues
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx

        plt.figure(figsize=(12, 8))

        # Different layout algorithms for different graph sizes
        if len(G.nodes) < 20:
            pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.kamada_kawai_layout(G)

        # Check if graph has extension attribute
        if any("extension" in G.nodes[n] for n in G.nodes):
            # Color nodes by file extension
            extension_colors = {
                ".py": "skyblue",
                ".js": "lightgreen",
                ".jsx": "green",
                ".ts": "yellow",
                ".tsx": "orange",
                ".html": "salmon",
                ".css": "violet",
                ".json": "khaki",
            }

            node_colors = [
                extension_colors.get(G.nodes[n].get("extension", ""), "lightgray")
                for n in G.nodes
            ]

            nx.draw(
                G,
                pos,
                with_labels=True,
                labels={n: os.path.basename(n) for n in G.nodes},
                node_color=node_colors,
                node_size=800,
                edge_color="gray",
                arrows=True,
            )
        else:
            # Simple graph drawing
            nx.draw(
                G,
                pos,
                with_labels=True,
                node_color="lightblue",
                node_size=800,
                edge_color="gray",
                arrows=True,
            )

        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return str(output_path)

    def _analyze_diff_content(self, diff_text):
        """
        Analyzes diff content to extract meaningful change information
        Returns a structured summary of changes
        """
        summary = {
            "lines_added": 0,
            "lines_removed": 0,
            "additions": [],
            "deletions": [],
            "modifications": [],
            "functions_added": [],
            "functions_modified": [],
            "functions_removed": [],
            "change_type": "unknown",
        }

        # Simple pattern matching for Python functions
        function_pattern = re.compile(
            r"^[\+\-]\s*def\s+([a-zA-Z0-9_]+)\s*\(", re.MULTILINE
        )
        class_pattern = re.compile(r"^[\+\-]\s*class\s+([a-zA-Z0-9_]+)", re.MULTILINE)
        import_pattern = re.compile(
            r"^[\+\-]\s*(?:import|from)\s+([^\s]+)", re.MULTILINE
        )

        # Count added/removed lines
        for line in diff_text.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                summary["lines_added"] += 1
                summary["additions"].append(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                summary["lines_removed"] += 1
                summary["deletions"].append(line[1:].strip())

        # Extract function changes
        added_functions = [
            m.group(1)
            for m in function_pattern.finditer(diff_text)
            if m.group(0).startswith("+")
        ]
        removed_functions = [
            m.group(1)
            for m in function_pattern.finditer(diff_text)
            if m.group(0).startswith("-")
        ]

        # Functions that appear in both added and removed are likely modifications
        modified_functions = set(added_functions) & set(removed_functions)
        truly_added_functions = set(added_functions) - modified_functions
        truly_removed_functions = set(removed_functions) - modified_functions

        summary["functions_added"] = list(truly_added_functions)
        summary["functions_removed"] = list(truly_removed_functions)
        summary["functions_modified"] = list(modified_functions)

        # Similarly handle class changes
        added_classes = [
            m.group(1)
            for m in class_pattern.finditer(diff_text)
            if m.group(0).startswith("+")
        ]
        removed_classes = [
            m.group(1)
            for m in class_pattern.finditer(diff_text)
            if m.group(0).startswith("-")
        ]

        # And import changes
        added_imports = [
            m.group(1)
            for m in import_pattern.finditer(diff_text)
            if m.group(0).startswith("+")
        ]
        removed_imports = [
            m.group(1)
            for m in import_pattern.finditer(diff_text)
            if m.group(0).startswith("-")
        ]

        # Determine overall change type
        if summary["lines_added"] > 0 and summary["lines_removed"] == 0:
            summary["change_type"] = "addition"
        elif summary["lines_added"] == 0 and summary["lines_removed"] > 0:
            summary["change_type"] = "deletion"
        elif summary["lines_added"] > 0 and summary["lines_removed"] > 0:
            summary["change_type"] = "modification"

        # Additional metadata
        summary["classes_added"] = added_classes
        summary["classes_removed"] = removed_classes
        summary["imports_added"] = added_imports
        summary["imports_removed"] = removed_imports

        return summary

    def summarize_repository_files(self):
        def extract_dependencies(file_path, content):
            """
            Enhanced dependency extraction that captures all types of dependencies
            """
            file_ext = os.path.splitext(file_path)[1].lower()
            dependencies = {
                "imports": [],
                "functions": [],
                "classes": [],
                "file_dependencies": [],
                "function_calls": {},  # Map of which functions call which others
            }

            # Python-specific extraction
            if file_ext == ".py":
                # Import patterns
                import_patterns = [
                    re.compile(
                        r"^import\s+([^\s,;]+)(?:\s*,\s*([^\s,;]+))*", re.MULTILINE
                    ),  # import x, y
                    re.compile(
                        r"^from\s+([^\s]+)\s+import\s+([^#\n]+)", re.MULTILINE
                    ),  # from x import y
                ]

                # Function and class patterns
                function_pattern = re.compile(
                    r"^def\s+([a-zA-Z0-9_]+)\s*\([^)]*\):", re.MULTILINE
                )
                class_pattern = re.compile(r"^class\s+([a-zA-Z0-9_]+)", re.MULTILINE)

                # Find all imports
                for pattern in import_patterns:
                    for match in pattern.finditer(content):
                        if match.group(0).startswith("from"):
                            module = match.group(1).strip()
                            imported_items = [
                                item.strip() for item in match.group(2).split(",")
                            ]

                            # Check if it's a local import
                            if not module.startswith(".") and "." not in module:
                                dependencies["imports"].append(
                                    f"from {module} import {', '.join(imported_items)}"
                                )
                            else:
                                # Could be a local file dependency
                                if module.startswith("."):
                                    # Relative import
                                    relative_path = os.path.normpath(
                                        os.path.join(
                                            os.path.dirname(file_path),
                                            module.strip(".").replace(".", "/"),
                                        )
                                    )
                                    if module.strip("."):  # Not just '.'
                                        dependencies["file_dependencies"].append(
                                            f"{relative_path}.py"
                                        )
                                else:
                                    # Absolute import within project
                                    dependencies["file_dependencies"].append(
                                        f"{module.replace('.', '/')}.py"
                                    )
                        else:
                            # Handle 'import x' or 'import x, y, z'
                            for i in range(
                                1, match.lastindex + 1 if match.lastindex else 2
                            ):
                                if match.group(i):
                                    module = match.group(i).strip()
                                    dependencies["imports"].append(f"import {module}")

                # Extract all functions and classes first
                functions = [m.group(1) for m in function_pattern.finditer(content)]
                dependencies["functions"] = functions
                dependencies["classes"] = [
                    m.group(1) for m in class_pattern.finditer(content)
                ]

                # Now analyze each function to find its calls
                for func_name in functions:
                    # Find the function body
                    func_pattern = re.compile(
                        r"def\s+"
                        + re.escape(func_name)
                        + r"\s*\([^)]*\):\s*(.*?)(?=\n\S|$)",
                        re.DOTALL,
                    )
                    func_matches = func_pattern.findall(content)

                    if func_matches:
                        func_body = func_matches[0]
                        calls = []

                        # Look for calls to other functions in this file
                        for other_func in functions:
                            if other_func != func_name and re.search(
                                r"\b" + re.escape(other_func) + r"\s*\(", func_body
                            ):
                                calls.append(other_func)

                        if calls:
                            dependencies["function_calls"][func_name] = calls

            # JavaScript/TypeScript-specific extraction
            elif file_ext in [".js", ".ts", ".jsx", ".tsx"]:
                # Import patterns for JS/TS
                js_import_patterns = [
                    re.compile(
                        r'import\s+(?:{[^}]+}|[^{}\s]+)\s+from\s+[\'"]([^\'"]+)[\'"]',
                        re.MULTILINE,
                    ),  # import x from 'y'
                    re.compile(
                        r'import\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE
                    ),  # import 'x'
                    re.compile(
                        r'require\([\'"]([^\'"]+)[\'"]\)', re.MULTILINE
                    ),  # require('x')
                ]

                # Function patterns for JS/TS (expanded to catch more patterns)
                js_function_patterns = [
                    re.compile(
                        r"function\s+([a-zA-Z0-9_$]+)\s*\(", re.MULTILINE
                    ),  # function x()
                    re.compile(
                        r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
                        re.MULTILINE,
                    ),  # const x = () =>
                    re.compile(
                        r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*function",
                        re.MULTILINE,
                    ),  # const x = function()
                    re.compile(
                        r"([a-zA-Z0-9_$]+)\s*:\s*function", re.MULTILINE
                    ),  # x: function
                    re.compile(
                        r"([a-zA-Z0-9_$]+)\([^)]*\)\s*{", re.MULTILINE
                    ),  # x() { (method in class/object)
                ]

                # Class pattern for JS/TS
                js_class_pattern = re.compile(r"class\s+([a-zA-Z0-9_$]+)", re.MULTILINE)

                # Find all imports
                for pattern in js_import_patterns:
                    for match in pattern.finditer(content):
                        module_path = match.group(1).strip()
                        dependencies["imports"].append(module_path)

                        # Check if it's a local import
                        if (
                            module_path.startswith("./")
                            or module_path.startswith("../")
                            or not (
                                module_path.startswith("@") or "/" not in module_path
                            )
                        ):
                            # Normalize and add extension if missing
                            local_path = os.path.normpath(
                                os.path.join(os.path.dirname(file_path), module_path)
                            )
                            if not os.path.splitext(local_path)[1]:
                                # Try common extensions
                                for ext in [".js", ".jsx", ".ts", ".tsx"]:
                                    possible_path = local_path + ext
                                    dependencies["file_dependencies"].append(
                                        possible_path
                                    )
                            else:
                                dependencies["file_dependencies"].append(local_path)

                # Find all functions
                functions = []
                for pattern in js_function_patterns:
                    for match in pattern.finditer(content):
                        functions.append(match.group(1))

                dependencies["functions"] = functions
                dependencies["classes"] = [
                    m.group(1) for m in js_class_pattern.finditer(content)
                ]

                # Simplified function call analysis for JS (more complex in reality)
                for func_name in functions:
                    # This is a simplified approximation; real JS analysis would require an AST
                    calls = []
                    for other_func in functions:
                        if other_func != func_name and re.search(
                            r"\b" + re.escape(other_func) + r"\s*\(", content
                        ):
                            calls.append(other_func)

                    if calls:
                        dependencies["function_calls"][func_name] = calls

            return dependencies

        def summarize_file(file_path, file_content, dependencies):
            """
            Enhanced file summarization that emphasizes dependencies for graph generation
            """
            prompt = f"""
            You are a code analysis assistant. Provide a detailed summary of the following file.
            
            IMPORTANT REQUIREMENTS:
            1. Start with an overview of the file's main purpose in 1-2 sentences
            2. List ALL import statements EXACTLY as they appear in the code (preserve them precisely)
            3. List ALL functions with their signatures and a brief description
            4. List ALL classes with their inheritance structure and a brief description
            5. Explicitly identify ALL function calls between functions in this file
            6. Clearly identify ALL dependencies on other local files (not standard libraries)
            7. Format your response with clear headings for each section
            
            This information will be used for:
            - Understanding code dependencies
            - Generating accurate dependency graphs
            - Retrieving relevant information based on queries
            
            EXTERNAL ANALYSIS RESULTS:
            Identified imports: {dependencies['imports']}
            Identified functions: {dependencies['functions']}
            Identified classes: {dependencies['classes']}
            Identified file dependencies: {dependencies['file_dependencies']}
            Identified function calls: {dependencies['function_calls']}
            
            File path: {file_path}
            File content:
            
            {file_content}
            """

            retries = 3
            for attempt in range(retries):
                try:
                    response = llm.invoke(prompt)
                    return response.content
                except Exception as e:
                    if "429" in str(e):
                        logger.warning("Quota exceeded. Retrying after delay...")
                        time.sleep(35)
                    else:
                        raise e
            return "Error: Failed after multiple retries."

        """Summarize all files in the current repository with enhanced dependency tracking"""
        if not self.state.current_repo_path:
            return False, "No repository currently loaded"

        repo_path = self.state.current_repo_path
        logger.info(f"Starting enhanced file summarization for repository: {repo_path}")

        # Clear previous summaries
        summaries_dir = self.config.summaries_dir
        if not summaries_dir.exists():
            summaries_dir.mkdir(parents=True)

        summary_file = summaries_dir / "summaries.txt"
        dependency_file = summaries_dir / "dependencies.json"
        function_call_file = summaries_dir / "function_calls.json"

        if summary_file.exists():
            summary_file.unlink()
        if dependency_file.exists():
            dependency_file.unlink()
        if function_call_file.exists():
            function_call_file.unlink()

        try:
            llm = self.get_llm()
            summaries = {}
            file_dependencies = {}  # Track dependencies between files
            all_function_calls = {}  # Track function calls across the project

            def get_file_content(file_path):
                """Reads the content of a file."""
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    return file.read()

            # Walk through the repo directory
            repo_path_obj = Path(repo_path)
            for root, dirs, files in os.walk(repo_path_obj):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for filename in files:
                    file_path = Path(root) / filename
                    relative_path = str(file_path.relative_to(repo_path_obj))

                    # Skip binary files and other non-text files
                    if is_binary_file(file_path):
                        continue
                    if file_path == "__pycache__":
                        continue
                    # Handle asset files differently - just record them without summarizing
                    if is_asset_file(file_path):
                        # Store a simple record of the asset file
                        summaries[relative_path] = (
                            f"[ASSET FILE] {filename} - Type: {file_path.suffix}"
                        )
                        logger.info(f"Recorded asset file: {relative_path}")
                        continue

                    try:
                        # Read the file content
                        file_content = get_file_content(file_path)

                        # Skip empty files or very large files
                        if (
                            not file_content or len(file_content) > 100000
                        ):  # Skip files larger than 100KB
                            continue

                        # Extract dependencies
                        dependencies = extract_dependencies(relative_path, file_content)
                        file_dependencies[relative_path] = dependencies

                        # Get the summary of the content
                        summary = summarize_file(
                            relative_path, file_content, dependencies
                        )
                        time.sleep(
                            1.5
                        )  # Add delay between API calls to avoid rate limiting

                        # Store the summary in the dictionary with relative file path
                        summaries[relative_path] = summary
                        logger.info(f"Summarized: {relative_path}")

                    except Exception as e:
                        logger.error(f"Error summarizing {file_path}: {e}")

            # Write all summaries to a single file
            with open(summary_file, "w", encoding="utf-8") as file:
                for file_path, summary in summaries.items():
                    file.write(f"Summary of {file_path}:\n")
                    file.write(f"{summary}\n")
                    file.write("\n" + "=" * 50 + "\n")

            # Write dependencies to a JSON file
            with open(dependency_file, "w", encoding="utf-8") as file:
                json.dump(file_dependencies, file, indent=2)

            logger.info(
                f"Summarization complete. Created summaries for {len(summaries)} files."
            )
            return (
                True,
                f"Summarization complete. Created summaries for {len(summaries)} files with dependency tracking.",
            )

        except Exception as e:
            logger.error(f"Error summarizing repository files: {e}")
            return False, f"Error summarizing repository files: {e}"

    def create_vector_database(self):
        """Create an enhanced vector database from repository files, summaries, and git history"""
        if not self.state.current_repo_path:
            return False, "No repository currently loaded"

        repo_path = self.state.current_repo_path
        logger.info("Starting enhanced vector database creation")

        try:
            from langchain.docstore.document import Document
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface.embeddings import HuggingFaceEmbeddings

            # Load documents from folders with metadata enrichment
            def load_folder(folder_path, source_label):
                folder = Path(folder_path)
                docs = []
                for file in folder.rglob("*"):
                    if(file.name == "dependencies.json"): # Skip dependencies.json file
                        continue
                    if file.is_file():
                        try:
                            with open(
                                file, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()

                                # Enhanced metadata
                                metadata = {
                                    "file_path": str(file),
                                    "source": source_label,
                                    "filename": file.name,
                                    "file_type": file.suffix,
                                    "creation_time": str(file.stat().st_ctime),
                                    "size": file.stat().st_size,
                                }

                                # Special handling for JSON files to improve retrieval
                                if file.suffix == ".json":
                                    try:
                                        json_data = json.loads(content)
                                        # For commit history files, add specific metadata
                                        if (
                                            file.name == "commit_history.json"
                                            or file.name == "repo_history.json"
                                        ):
                                            if "commits" in json_data:
                                                metadata["commit_count"] = len(
                                                    json_data.get("commits", [])
                                                )
                                                metadata["first_commit"] = (
                                                    json_data.get(
                                                        "first_commit_date", ""
                                                    )
                                                )
                                                metadata["last_commit"] = json_data.get(
                                                    "last_commit_date", ""
                                                )
                                                if "file_path" in json_data:
                                                    metadata["source_file"] = (
                                                        json_data.get("file_path", "")
                                                    )
                                    except:
                                        pass  # If JSON parsing fails, continue with standard metadata

                                doc = Document(
                                    page_content=content,
                                    metadata=metadata,
                                )
                                docs.append(doc)
                        except Exception as e:
                            logger.warning(f"Skipping {file} due to error: {e}")
                return docs

            def load_repo_folder(folder_path, source_label):
                folder = Path(folder_path)
                docs = []
                for file in folder.rglob("*"):
                    if file.is_file() and not is_binary_file(file):
                        try:
                            with open(
                                file, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                # Skip empty files or very large files
                                if (
                                    not content or len(content) > 100000
                                ):  # Skip files larger than 100KB
                                    continue

                                # Enhanced metadata for code files
                                rel_path = file.relative_to(folder)
                                metadata = {
                                    "file_path": str(file),
                                    "relative_path": str(rel_path),
                                    "source": source_label,
                                    "filename": file.name,
                                    "file_type": file.suffix,
                                    "directory": str(file.parent.relative_to(folder)),
                                }

                                # Additional metadata for code files
                                if file.suffix in [
                                    ".py",
                                    ".js",
                                    ".ts",
                                    ".jsx",
                                    ".tsx",
                                    ".java",
                                    ".cpp",
                                    ".c",
                                ]:
                                    # Simple heuristics to identify key elements
                                    imports = re.findall(
                                        r"^\s*(?:import|from|require)\s+.*$",
                                        content,
                                        re.MULTILINE,
                                    )
                                    functions = re.findall(
                                        r"^\s*(?:def|function|const\s+\w+\s*=\s*\(.*?\)\s*=>)\s+\w+",
                                        content,
                                        re.MULTILINE,
                                    )
                                    classes = re.findall(
                                        r"^\s*class\s+\w+", content, re.MULTILINE
                                    )

                                    metadata["imports_count"] = len(imports)
                                    metadata["functions_count"] = len(functions)
                                    metadata["classes_count"] = len(classes)
                                    metadata["contains_imports"] = len(imports) > 0
                                    metadata["contains_functions"] = len(functions) > 0
                                    metadata["contains_classes"] = len(classes) > 0

                                doc = Document(
                                    page_content=content,
                                    metadata=metadata,
                                )
                                docs.append(doc)
                        except Exception as e:
                            logger.warning(f"Skipping {file} due to error: {e}")
                return docs

            # Load documents from different sources
            summary_docs = load_folder(self.config.summaries_dir, "summary")
            commit_diff_docs = load_folder(self.config.git_history_dir, "commit_diff")
            repo_docs = load_repo_folder(repo_path, "repo_code")

            # Combine documents
            all_docs = summary_docs + commit_diff_docs + repo_docs
            logger.info(f"Loaded {len(all_docs)} documents for vector database")

            # Enhanced splitting strategy with overlap for better context preservation
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,  # Higher overlap to ensure context is preserved
                separators=["\n\n", "\n", " ", ""],  # More granular separators
                keep_separator=True,
            )
            split_docs = splitter.split_documents(all_docs)

            # Setup embeddings
            embeddings = HuggingFaceEmbeddings(model_name=self.config.embedding_model)

            # Create FAISS vector store
            db = FAISS.from_documents(split_docs, embedding=embeddings)

            # Save the database locally
            db.save_local(str(self.config.vector_db_dir))

            logger.info(
                f"Vector database created and saved to {self.config.vector_db_dir}"
            )
            self.state.mark_analysis_complete()
            return True, "Vector database created successfully"

        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
            return False, f"Error creating vector database: {e}"

    def initialize_retrieval_chain(self):
        """Initialize the enhanced retrieval chain for answering questions about the repository"""
        if not self.state.analysis_complete:
            return False, "Repository analysis not complete yet"

        logger.info("Initializing enhanced retrieval chain")

        try:
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain.chains import ConversationalRetrievalChain
            from langchain.memory import ConversationBufferMemory
            from langchain.prompts import PromptTemplate
            from langchain.retrievers import ContextualCompressionRetriever
            from langchain.retrievers.document_compressors import LLMChainExtractor

            # Load embeddings
            embeddings = HuggingFaceEmbeddings(model_name=self.config.embedding_model)

            # Load FAISS vectorstore safely
            db = FAISS.load_local(
                str(self.config.vector_db_dir),
                embeddings,
                allow_dangerous_deserialization=True,
            )

            # Create base retriever with increased k for more comprehensive results
            base_retriever = db.as_retriever(search_kwargs={"k": 10, "fetch_k": 25})

            # Create LLM chain extractor for contextual compression
            llm = self.get_llm(temperature=0.0)
            compressor = LLMChainExtractor.from_llm(llm)

            # Create contextual compression retriever
            retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=base_retriever
            )

            # Set up advanced prompt
            prompt = PromptTemplate(
                input_variables=["context", "chat_history", "question"],
                template="""
                You are a Git repository analysis assistant with advanced capabilities. You help users understand codebases by analyzing
                Git history, summarizing files, and answering questions about code changes and functionality. Also, ensure that in your response you output \\n for newlines to separate paragraphs and for every new subparagraph and subsections. Bulleted and numbered lists should have items always be separated by \\n. 
                
                When analyzing code repositories:
                1. For commit history queries, provide ALL relevant commit information chronologically
                2. For file dependency queries, show complete relationships between files
                3. For function/class queries, provide comprehensive information about their implementations
                4. For change analysis queries, compare changes across commits in detail
                5. When answering queries for changes for a specific file in a given commit, be sure to include all relevant changes in the response by interpreting the diffs in commit.

                Don't comment on facts that you are not fully sure of. 
                Use this comprehensive context to answer the user's query:
                {context}
                
                Conversation so far:
                {chat_history}
                
                Human: {question}
                Assistant:""",
            )

            # Set up memory
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True, output_key="answer"
            )

            # Create chain with additional parameters for more comprehensive retrieval
            retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.get_llm(),
                retriever=retriever,
                memory=memory,
                combine_docs_chain_kwargs={"prompt": prompt},
                return_source_documents=True,
                verbose=True,
                output_key="answer",
                max_tokens_limit=8000,  # Allow for larger context window
            )

            self.state.mark_vector_db_loaded()
            logger.info("Enhanced retrieval chain initialized successfully")
            return True, retrieval_chain

        except Exception as e:
            logger.error(f"Error initializing retrieval chain: {e}")
            return False, f"Error initializing retrieval chain: {e}"

    def run_analysis_workflow(self, repo_url):
        """
        Run the complete analysis workflow for a repository
        Returns: generator function that yields progress updates
        """

        def workflow_generator():
            yield "Starting repository analysis process...\n"
            time.sleep(0.5)

            # Step 1: Clone the repository
            yield "Step 1/4: Cloning repository...\n"
            success, repo_path = self.clone_repository(repo_url)
            if not success:
                yield f"Error: {repo_path}\n"
                return

            repo_name = repo_url.strip().split("/")[-1].replace(".git", "")
            yield f"Successfully cloned repository: {repo_name}\n"
            time.sleep(0.5)

            # Step 2: Analyze git history
            yield "Step 2/4: Analyzing Git history...\n"
            success, message = self.analyze_git_history()
            if not success:
                yield f"Error: {message}\n"
                return
            yield f"{message}\n"
            time.sleep(0.5)

            # Step 3: Summarize files
            yield "Step 3/4: Summarizing repository files...\n"
            success, message = self.summarize_repository_files()
            if not success:
                yield f"Error: {message}\n"
                return
            yield f"{message}\n"
            time.sleep(0.5)

            # Step 4: Create vector database
            yield "Step 4/4: Creating vector database for retrieval...\n"
            success, message = self.create_vector_database()
            if not success:
                yield f"Error: {message}\n"
                return
            yield f"{message}\n"
            time.sleep(0.5)

            yield "\nAnalysis complete! You can now ask questions about the repository."

        return workflow_generator
