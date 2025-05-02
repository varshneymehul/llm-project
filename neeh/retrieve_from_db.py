from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
)

# Load embeddings (same model as used while saving)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS vectorstore safely
db = FAISS.load_local(
    "faiss_repo_knowledge", embeddings, allow_dangerous_deserialization=True
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

flag = True
while flag:
    user_input = input("\nAsk about your repo: ")
    if user_input == "stop":
        flag = False
        continue

    # QA chain requires invoking with query, otherwise it will fail; context is being provided by the retriever and the history is being maintained by ConversationBufferMemory
    response = qa_chain.invoke({"question": user_input})
    print("\nAnswer:", response["answer"])
