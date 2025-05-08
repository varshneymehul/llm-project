# Git Repository Analysis LLM Agent

This project provides an AI-powered Git repository analysis tool that can help developers understand codebases, track changes, and analyze repository evolution through natural language interactions.

## Features

- **Repository Analysis**: Clone and analyze any public GitHub repository
- **Git History Analysis**: Track function-level changes across Git commits
- **File Summarization**: Generate concise summaries for all files in the repository
- **Natural Language Querying**: Ask questions about the codebase in plain English
- **Integrated with RAG**: Uses Retrieval Augmented Generation to provide context-aware responses

## Architecture

- Django backend with REST API endpoints
- React frontend for user interaction
- LangChain for LLM workflows
- FAISS for vector storage and similarity search
- Gemini 1.5 Flash for natural language processing

## Directory Structure

```
project/
├── cloned_repos/          # Stores cloned repositories
├── summaries/             # Stores file summaries
├── git_file_history_output/ # Stores git history analysis
├── faiss_repo_knowledge/  # Vector database
├── views.py              # Django views (API endpoints)
├── urls.py               # URL routing
├── git_analysis_service.py # Git analysis service
├── utils.py              # Utility functions
└── requirements.txt      # Dependencies
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   API_KEY=your_gemini_api_key
   ```

## API Endpoints

- `/api/chat/` - Chat with the LLM agent
- `/api/health/` - Health check endpoint
- `/api/status/` - Get current repository status

## Usage Flow

1. Send a message containing a GitHub repository URL to analyze
2. The system will:
   - Clone the repository
   - Analyze Git history
   - Generate file summaries
   - Create a vector database
   - Initialize the retrieval system
3. Ask questions about the repository in natural language

## Example Queries

- "Why was the login function changed in the last commit?"
- "What are the main components of this repository?"
- "Explain how the authentication system works"
- "What changes were made to the database schema over time?"
- "What's the purpose of the utils.py file?"

## Requirements

- Python 3.8+
- Django 4.2+
- Internet connection for API access
- Google API key for Gemini access
