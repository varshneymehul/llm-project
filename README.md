# Git Repository Analysis LLM Agent

An intelligent Git repository analysis tool that leverages AI to help developers understand, navigate, and track changes in codebases through natural language interactions.

## ✨ Features

- **Code Repository Analysis**: Clone and analyze any public GitHub repository
- **Natural Language Processing**: Interact with your codebase using plain English
- **Dependency Visualization**: Generate interactive graphs for both:
  - **Functional Dependencies**: See how functions relate to each other
  - **File Dependencies**: Visualize relationships between files
- **Git History Tracking**: 
  - Analyze commit history at the repository level
  - Track function-level changes across Git commits
  - View file modification patterns over time
- **File Summarization**: Generate concise summaries for all files in the repository
- **Smart Querying**: Ask questions about the codebase and get intelligent responses
- **Retrieval Augmented Generation (RAG)**: Context-aware responses backed by your actual code

## 🏗️ Architecture

- **Backend**: Django REST API framework
- **Frontend**: React for interactive user experience
- **LLM Integration**: LangChain for AI workflows
- **Vector Store**: FAISS for efficient similarity search
- **LLM Engine**: Gemini 1.5 Flash for natural language processing

## 📁 Directory Structure

```
project/
├── .git                    # Git repository
├── .venv                   # Virtual environment
├── backend/                # Django backend
│   ├── api/                # Django API app
│   │   ├── __pycache__/    # Python cache files
│   │   ├── migrations/     # Database migrations
│   │   ├── __init__.py     # Package initialization
│   │   ├── admin.py        # Admin configuration
│   │   ├── apps.py         # App configuration
│   │   ├── git_analysis_service.py # Git analysis service
│   │   ├── models.py       # Data models
│   │   ├── tests.py        # Tests
│   │   ├── urls.py         # URL routing
│   │   ├── utils.py        # Utility functions
│   │   └── views.py        # API endpoints
│   ├── backend/            # Django project settings
│   ├── cloned_repos/       # Stores cloned repositories
│   ├── faiss_repo_knowledge/ # Vector database
│   ├── git_file_history_output/ # Stores git history analysis
│   ├── summaries/          # Stores file summaries
│   ├── .gitignore          # Git ignore file
│   ├── db.sqlite3          # SQLite database
│   ├── manage.py           # Django management script
│   └── project_state.json  # Project state configuration
├── frontend/               # Frontend application
│   ├── .env                # Environment variables
│   ├── .gitignore          # Git ignore file
│   └── main.py             # Main frontend script
├── .env                    # Environment variables
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js and npm
- Git

### Backend Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/git-analysis-agent.git
   cd git-analysis-agent
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory with:
   ```
   API_KEY=your_gemini_api_key
   ```

5. **Start the backend server**
   ```bash
   cd backend
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend development server**
   ```bash
   npm start
   ```

## 🔑 Authentication

The application requires authentication to use. You can log in with the following credentials:

- **Username**: test_llm
- **Password**: 12345

## 🔌 API Endpoints

- `POST /api/chat/`: Chat with the LLM agent
- `GET /api/health/`: Health check endpoint
- `GET /api/status/`: Get current repository status
- `POST /api/reset-retrieval/`: Reset the retrieval chain
- `GET /api/graph-folders/`: List available graph folders
- `GET /api/graph-folders/<folder_name>/`: Get details for a specific graph folder
- `GET /api/graph-file/<folder>/<filename>`: Serve a specific graph file

## 📊 Usage Flow

1. **Login** using the provided credentials
2. **Submit a repository** by entering a GitHub URL
3. **Wait for analysis** to complete (progress will be shown)
4. **Explore the repository** through:
   - Dependency graphs (functional and file)
   - File summaries
   - Commit history visualization
5. **Ask questions** about the codebase in natural language

## 💬 Example Queries

- "Show me the most frequently modified files in this repository"
- "Which functions depend on the `authenticate` method?"
- "Explain how the authentication system works"
- "What changes were made to the database schema in the last 10 commits?"
- "What's the purpose of the utils.py file?"
- "Who contributed most to the frontend components?"
- "Visualize the file dependency graph for the authentication module"

## 🛠️ Troubleshooting

- **Backend connection issues**: Ensure the Django server is running on port 8000
- **Authentication failures**: Verify you're using the correct username and password
- **Analysis timeout**: Large repositories may take longer to analyze
- **Graph visualization issues**: Try refreshing the page or using a different browser

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
