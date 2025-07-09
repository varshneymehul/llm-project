# Codebase Evolution Insight Tool

Code assistants today are great at explaining what a piece of code does, but they often miss the context behind **why** it was written that way.  
This project aims to uncover the **reasoning and evolution** behind a codebase by analyzing its development history.

Rather than treating a repository as a static snapshot, this tool builds a structured knowledge graph from:

- Git commit history
- Pull requests and code reviews
- Issues and bug reports
- Developer discussions

This allows the system to answer deeper, history-aware questions like:

- **Why** was a certain implementation preferred?
- **What issue** led to a specific refactor?
- **Who** reviewed and influenced a major change?

---

##  **Problem Statement**

Most code Q&A tools today (e.g., RAG-based agents) only analyze the current codebase.  
They ignore the **temporal and causal history** — which often holds the key to understanding *why* things are the way they are.

---

## 🛠️ **Core Approach**

We construct a **Causal and Temporal Knowledge Graph** that connects:

- Commits → the files and functions they modify
- Pull requests → the issues they resolve
- Developers → the changes they authored or reviewed
- Concepts and bugs → where they’re discussed or fixed

This graph allows for meaningful traversals based on user questions.

---

##  **Key Entities and Relationships**

**Entities:**

- `File`, `Function`, `Commit`, `PullRequest`, `Issue`, `Developer`, `Concept`, `Bug`

**Relationships:**

- `MODIFIES`, `FIXES`, `AUTHORED_BY`, `RESOLVES`, `INTRODUCED_IN`, `DISCUSSES`

---

## **Architecture Overview**

1. **Data Ingestion**  
   - GitHub API or `git` CLI to fetch commits, PRs, and issues

2. **Entity Extraction**  
   - NLP models (e.g., spaCy, Hugging Face) to identify filenames, functions, concepts

3. **Relation Extraction**  
   - Rule-based + model-based extraction (e.g., "fixes #42", mentions of bugs)

4. **Graph Construction**  
   - Built using **Neo4j** or other graph DBs

5. **Query Answering**
   - Extracts entities from the user’s question
   - Traverses the graph for relevant commits, PRs, and issues
   - Passes results to an LLM to generate a final answer

---

##  **Example Workflow**

**User question:**  
> "Why was caching in `user_service.py` changed?"

**System flow:**
1. Find all commits modifying `user_service.py`
2. Trace related PRs, issues, and concept mentions like "caching"
3. Gather comments, discussions, commit messages
4. Use an LLM to summarize the full reasoning

---

##  **Tech Stack**

- **Languages & Tools**: Python, GitHub API, Neo4j
- **NLP Models**: spaCy, Hugging Face Transformers
- **Graph Traversal & Storage**: Cypher queries, Neo4j
- **Answer Generation**: LangChain, OpenAI or LLaMA 3

---

##  **Current Progress**

-  Git & GitHub data extraction
-  Basic rule-based entity + relation extraction
-  Graph construction using Neo4j
-  Graph-based retrieval pipeline
-  LLM-based natural language interface


