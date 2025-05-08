import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.tools import tool
from langchain_community.chat_models import ChatOpenAI  # or ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
import subprocess

from langchain_google_genai import ChatGoogleGenerativeAI

# Load API keys
load_dotenv()
api_key = os.getenv("API_KEY")

# Setup LLM (swap ChatOpenAI with ChatGoogleGenerativeAI if using Gemini)
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0,
)
# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# Tool: Clone Git repo
@tool
def clone_repo(url: str) -> str:
    """Clones the Git repository from the given URL into the 'cloned_repos' directory."""
    try:
        if not url.startswith("http"):
            return "Please provide a valid Git repository URL."
        os.makedirs("cloned_repos", exist_ok=True)
        repo_name = url.strip().split("/")[-1].replace(".git", "")
        dest_path = os.path.join("cloned_repos", repo_name)
        if os.path.exists(dest_path):
            return f"Repository already cloned at {dest_path}"
        subprocess.run(["git", "clone", url, dest_path], check=True)
        return f"Successfully cloned repository to: {dest_path}"
    except subprocess.CalledProcessError as e:
        return f"Error cloning repository: {e}"


# Register tools
tools = [clone_repo]

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory,
)

# --- Chat loop ---
print("🤖 Hello! I can help you clone GitHub repos. Type 'exit' to quit.")
while True:
    query = input("You: ")
    if query.lower() in ["exit", "quit"]:
        break
    response = agent.run(query)
    print("Agent:", response)
