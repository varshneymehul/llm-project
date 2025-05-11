from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
# api_key = os.getenv("API_KEY")
api_key = "AIzaSyDpnAn5_EpwuJWkHZubXaQ3TsZeSTuqGGg"
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
)

# Load embeddings (same model as used while saving)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS vectorstore safely
db = FAISS.load_local(
    "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/backend/faiss_repo_knowledge",
    embeddings,
    allow_dangerous_deserialization=True,
)

# Make retriever
retriever = db.as_retriever(search_kwargs={"k": 5})

# Set up prompt
prompt = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template="""
    You are a chatbot having a conversation with a human.
    The user has generated file summaries for all the files inside a Github repository.
    You have access to these summaries using a retrieval system.

    Use this context to help answer the user's query:
    {context}

    Conversation so far:
    {chat_history}
    Human: {question}
    Chatbot:""",
)
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Set up chain
from langchain.chains import RetrievalQA

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": prompt},
)

prompt = f"""
    You are a codebase analyst. Given high-level commit embeddings or descriptions of a repository, infer a possible directory structure and list of files in the project. Your output must be a valid Python list of file paths (strings), formatted exactly like:\
    files = [
    "folder1/main.py",
    "folder2/utils.js",
    ...
]

"""

response = qa_chain.invoke({"question": prompt})
print("\nAnswer:", response["answer"])

prompt = """
    You are a codebase reasoning agent. Given commit-level embeddings (or clusters of files frequently committed together), identify the likely file dependency relationships. Return a Python dictionary in the format:
    dependencies = {
    "fileA": ["fileB", "fileC"],  # fileA depends on fileB and fileC
    ...
}
"""

response = qa_chain.invoke({"question": prompt})
print("\nAnswer:", response["answer"])

prompt = """
    You are a code analysis assistant.

Given the Python code below, return a dictionary in the format:
function_calls = {
    'function_A': ['function_B', 'function_C'],
    'function_B': [],
    ...
}

This dictionary should include:
- All defined functions as keys.
- All the functions each function calls (within the same file) as values.
- Functions that are never called by others must still be included (e.g., dead code).
- Do NOT include built-in or external library calls.

Example:
>>> Code:
def main():
    load_data()
    process_data()
    save_results()

def load_data():
    read_file()

def process_data():
    clean_data()
    analyze_data()

def clean_data():
    pass

def analyze_data():
    generate_report()

def generate_report():
    pass

def read_file():
    pass

def save_results():
    pass

def unused_function():
    pass

<<< Output:
function_calls = {
    'main': ['load_data', 'process_data', 'save_results'],
    'load_data': ['read_file'],
    'process_data': ['clean_data', 'analyze_data'],
    'analyze_data': ['generate_report'],
    'clean_data': [],
    'read_file': [],
    'save_results': [],
    'generate_report': [],
    'unused_function': []
}


"""

response = qa_chain.invoke({"question": prompt})
print("\nAnswer:", response["answer"])

prompt = """
    You are a codebase reasoning agent. Given commit-level embeddings (or clusters of files frequently committed together), identify the likely file dependency relationships. Return a Python dictionary in the format:
    commit_file_map = {
    'c1': ['file1.py', 'file2.py'],
    'c2': ['file2.py', 'file3.py'],
    'c3': ['file1.py', 'file3.py', 'file4.py'],
    'c4': ['file4.py'],
    'c5': ['file5.py'],
    ...
}
}
"""

response = qa_chain.invoke({"question": prompt})
print("\nAnswer:", response["answer"])
