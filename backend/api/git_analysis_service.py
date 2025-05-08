import subprocess
import logging
import time
import json
import os
from pathlib import Path
from git import Repo
from collections import defaultdict
import re

from .utils import GitAnalysisConfig, GitProjectState, is_binary_file
from langchain_google_genai import ChatGoogleGenerativeAI

# Set up logging
logger = logging.getLogger(__name__)

# Load configuration
config = GitAnalysisConfig()


class GitAnalysisService:
    """Service for Git repository analysis"""

    def __init__(self):
        self.config = GitAnalysisConfig()
        self.state = GitProjectState()
        self._setup_intent_classifier()

    def _setup_intent_classifier(self):
        """Setup the intent classifier to determine if a message is requesting git analysis"""
        self.intent_llm = self.get_llm(temperature=0.1)

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
            print(response)
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
        """Analyze git history of the current repository"""
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
                
            file_commit_data = defaultdict(list)

            # Safe folder name maker
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
                        diff_text = repo.git.diff(
                            NULL_TREE, commit.hexsha, "--", file_path
                        )
                    else:
                        diff_text = repo.git.diff(
                            parents[0].hexsha, commit.hexsha, "--", file_path
                        )

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
                full_folder_path = self.config.git_history_dir / safe_name
                full_folder_path.mkdir(exist_ok=True)

                # Save JSON file
                json_path = full_folder_path / "commit_history.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(commits, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Git history analysis complete. Output saved to: {self.config.git_history_dir}"
            )
            return (
                True,
                f"Git history analysis complete. Found history for {len(file_commit_data)} files.",
            )

        except Exception as e:
            logger.error(f"Error analyzing git history: {e}")
            return False, f"Error analyzing git history: {e}"

    def summarize_repository_files(self):
        """Summarize all files in the current repository"""
        if not self.state.current_repo_path:
            return False, "No repository currently loaded"

        repo_path = self.state.current_repo_path
        logger.info(f"Starting file summarization for repository: {repo_path}")

        # Clear previous summaries
        summary_file = self.config.summaries_dir / "summaries.txt"
        if summary_file.exists():
            summary_file.unlink()

        try:
            llm = self.get_llm()
            summaries = {}

            def get_file_content(file_path):
                """Reads the content of a file."""
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    return file.read()

            def summarize_file(file_content):
                prompt = (
                    "You are a helpful assistant. Provide concise summaries of the text. "
                    "If the file contains any code write about every function present in the file, "
                    "else describe the file contents clearly like how you would explain it to a 5 year old"
                    "\n\n" + file_content
                )

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

            # Walk through the repo directory
            repo_path_obj = Path(repo_path)
            for root, dirs, files in os.walk(repo_path_obj):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for filename in files:
                    file_path = Path(root) / filename

                    # Skip binary files and other non-text files
                    if is_binary_file(file_path):
                        continue

                    try:
                        # Read the file content
                        file_content = get_file_content(file_path)

                        # Skip empty files or very large files
                        if (
                            not file_content or len(file_content) > 100000
                        ):  # Skip files larger than 100KB
                            continue

                        # Get the summary of the content
                        summary = summarize_file(file_content)
                        time.sleep(
                            1.5
                        )  # Add delay between API calls to avoid rate limiting

                        # Store the summary in the dictionary with relative file path
                        relative_path = str(file_path.relative_to(repo_path_obj))
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

            logger.info(
                f"Summarization complete. Created summaries for {len(summaries)} files."
            )
            return (
                True,
                f"Summarization complete. Created summaries for {len(summaries)} files.",
            )

        except Exception as e:
            logger.error(f"Error summarizing repository files: {e}")
            return False, f"Error summarizing repository files: {e}"

    def create_vector_database(self):
        """Create a vector database from repository files, summaries, and git history"""
        if not self.state.current_repo_path:
            return False, "No repository currently loaded"

        repo_path = self.state.current_repo_path
        logger.info("Starting vector database creation")

        try:
            from langchain.docstore.document import Document
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings

            # Load documents from folders
            def load_folder(folder_path, source_label):
                folder = Path(folder_path)
                docs = []
                for file in folder.rglob("*"):
                    if file.is_file():
                        try:
                            with open(
                                file, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read()
                                doc = Document(
                                    page_content=content,
                                    metadata={
                                        "file_path": str(file),
                                        "source": source_label,
                                    },
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

                                doc = Document(
                                    page_content=content,
                                    metadata={
                                        "file_path": str(file),
                                        "source": source_label,
                                    },
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

            # Split into smaller chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
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
        """Initialize the retrieval chain for answering questions about the repository"""
        if not self.state.analysis_complete:
            return False, "Repository analysis not complete yet"

        logger.info("Initializing retrieval chain")

        try:
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain.chains import ConversationalRetrievalChain
            from langchain.memory import ConversationBufferMemory
            from langchain.prompts import PromptTemplate

            # Load embeddings
            embeddings = HuggingFaceEmbeddings(model_name=self.config.embedding_model)

            # Load FAISS vectorstore safely
            db = FAISS.load_local(
                str(self.config.vector_db_dir),
                embeddings,
                allow_dangerous_deserialization=True,
            )

            # Create retriever
            retriever = db.as_retriever(search_kwargs={"k": 5})

            # Set up prompt
            prompt = PromptTemplate(
                input_variables=["context", "chat_history", "question"],
                template="""
                You are a Git repository analysis assistant. You help users understand codebases by analyzing
                Git history, summarizing files, and answering questions about code changes and functionality.
                
                Use this context to help answer the user's query:
                {context}
                
                Conversation so far:
                {chat_history}
                Human: {question}
                Assistant:""",
            )

            # Set up memory
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )

            # Create chain
            retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.get_llm(),
                retriever=retriever,
                memory=memory,
                combine_docs_chain_kwargs={"prompt": prompt},
            )

            self.state.mark_vector_db_loaded()
            logger.info("Retrieval chain initialized successfully")
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

            # Initialize retrieval chain
            yield "Initializing question answering system...\n"
            success, _ = self.initialize_retrieval_chain()
            if not success:
                yield f"Error: Failed to initialize question answering system\n"
                return

            yield "\nAnalysis complete! You can now ask questions about the repository."

        return workflow_generator
