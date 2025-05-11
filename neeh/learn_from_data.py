
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
)

# Load documents from a folder
def load_folder(folder_path, source_label):
    folder = Path(folder_path)
    docs = []
    for file in folder.rglob('*'):
        if file.is_file():
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                doc = Document(
                    page_content=content,
                    metadata={"file_path": str(file), "source": source_label}
                )
                docs.append(doc)
    return docs

def load_repo_folder(folder_path, source_label):
    folder = Path(folder_path)
    docs = []
    for file in folder.rglob('*'):
        if file.is_file() and file.suffix not in ['.png', '.jpg', '.jpeg', '.gif', '.exe', '.dll', '.bin']:  # Skip binaries
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={"file_path": str(file), "source": source_label}
                    )
                    docs.append(doc)
            except Exception as e:
                print(f"Skipping {file} due to error: {e}")
    return docs

# Load both folders
summary_docs = load_folder('summaries', 'summary')
commit_diff_docs = load_folder('git_file_history_output', 'commit_diff')
repo_docs = load_repo_folder('/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/turning-ideas', 'repo_code')
# cloned_repo_docs = load_folder('lozad.js', 'cloned_repo')

# Combine documents
all_docs = summary_docs + commit_diff_docs + repo_docs
print(f"Loaded {len(all_docs)} documents.")

# Split into smaller chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_docs = splitter.split_documents(all_docs)

# Setup embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create FAISS vector store
db = FAISS.from_documents(split_docs, embedding=embeddings)

db.save_local("faiss_repo_knowledge")
# Create retriever
retriever = db.as_retriever(search_kwargs={"k": 5})

# Create QA system
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
