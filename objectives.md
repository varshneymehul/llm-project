Updated Plan
# Enhancing Git Repository Analysis with Advanced LLM Techniques

Before diving into the main report, here's a summary of key recommendations: Your project has strong potential for novelty by implementing a multi-agent system with specialized roles for repository analysis, incorporating graph-based structural representations of code evolution, and developing hybrid evaluation metrics that combine automated and human assessment techniques.

## Novelty Opportunities

Looking at your current project plan, there are several promising directions to add novelty beyond basic RAG implementation:

### Multi-Agent Collaborative System

Instead of a single agent, create a specialized team of LLM-powered agents that work together to analyze repositories from different perspectives:

- **Architect Agent**: Analyzes structural code changes and maintains a global understanding of the codebase architecture
- **Historian Agent**: Specializes in temporal patterns and evolutionary trends in the repository
- **Classifier Agent**: Categorizes commits by type and quality following conventional patterns[15]
- **Impact Analyzer Agent**: Traces how changes propagate through dependent components
- **Natural Language Interpreter**: Translates user queries into specific analysis tasks

This multi-agent approach mirrors successful implementations in fiction generation tools[9] and would represent a significant advancement over single-agent systems for code analysis.

### Graph-Based Repository Representation

Create a dynamic graph representation of code repositories where:

- Nodes represent code entities (functions, classes, variables)
- Edges represent relationships (calls, dependencies, imports)
- Temporal dimension captures evolution over time
- Apply Graph Neural Networks (GNNs) to analyze patterns[14][5]

Recent research on feature-wise linear modulation in GNNs could enhance your model's ability to understand relationships between code components[5].

### Commit Quality Analysis Framework

Develop a novel framework for assessing commit quality that goes beyond simple comparison with human-written messages:

- Automated classification of commits into standard types (feature, fix, docs, etc.)[15]
- Quality metrics for commit messages based on information content and explainability
- Correlation analysis between commit message quality and subsequent code maintenance efforts

Research shows LLMs can effectively classify commits, but complete automation requires sophisticated filtering techniques[8].

## Updated Feature Set

Based on your initial plan and the novelty suggestions, here's an enhanced feature set:

### Code Change Analysis
- Fine-grained AST-level diff analysis (beyond simple text diffs)
- Function boundary-aware change tracking
- Semantic change classification (not just syntactic)
- Detection of refactoring patterns vs. functional changes[1]

### Repository Structure Analysis
- Dependency graph construction and evolution tracking
- Module coupling and cohesion analysis over time
- Identification of architectural drift through commit history
- Visualization of structural changes using interactive graphs[14]

### Temporal Analysis
- Development velocity metrics by component/module
- Developer specialization patterns (who works on what)
- Bug introduction and resolution timelines
- Identification of development cycles and patterns[10]

### Natural Language Capabilities
- Causal explanation generation for code changes
- Context-aware answering of complex repository questions
- Custom prompting strategies optimized for code understanding
- Translation between technical and non-technical explanations

### Evaluation Capabilities
- Automated commit message quality assessment
- Comparison of generated explanations with ground truth
- Counterfactual analysis ("What if this change hadn't been made?")
- Generation of alternative implementation suggestions[1][8]

## Development Roadmap

To complete this project within 14 days, here's a structured roadmap:

### Days 1-2: Core Infrastructure Setup
- Set up Git data extraction pipeline for target repositories
- Implement basic diff parsing and commit message extraction
- Create initial dataset from selected open-source projects
- Design data structures for storing repository information[6][16]

### Days 3-5: Basic Analysis Features
- Implement function-level change detection
- Build commit message parser and classifier
- Create baseline LLM prompting strategies
- Develop initial evaluation metrics[3][12]

### Days 6-8: Advanced Analysis & Multi-Agent Framework
- Implement graph representation of code repositories
- Design and implement specialized agent roles
- Create agent communication protocol
- Build structural analysis components[5][14]

### Days 9-11: Integration & Refinement
- Integrate all components into cohesive system
- Implement user query interface
- Optimize prompting strategies based on initial results
- Refine evaluation metrics and testing framework[1][8]

### Days 12-14: Evaluation & Documentation
- Conduct comprehensive evaluation using established benchmarks
- Perform user studies for qualitative assessment
- Document system architecture and findings
- Prepare academic paper draft and demonstration[10]

## Structural Analysis Components

The structural analysis elements will significantly enhance your project's novelty:

### Repository Structure Modeling
- Generate AST (Abstract Syntax Tree) for each code version
- Track structural changes at semantic level
- Model inheritance hierarchies and design patterns
- Analyze how structural properties correlate with development metrics[14]

### Commit Graph Analysis
- Build commit dependency graphs (which commit affects which)
- Identify critical path commits in feature development
- Detect structural fragility through change propagation analysis
- Apply GNN techniques to predict impact of potential changes[5]

### Code Quality Metrics Integration
- Correlate structural properties with established code quality metrics
- Track how refactoring commits affect structural complexity
- Identify patterns of technical debt accumulation and resolution
- Create structural health scores for different components[10][14]

### Temporal Pattern Recognition
- Analyze cyclical patterns in development activities
- Identify phases of exploration, consolidation, and refactoring
- Detect structural breaking points in repository evolution
- Model developer behavior patterns and their impact on code structure[10]

Recent research indicates LLMs have significantly impacted maintenance commits in open-source projects (51% increase), suggesting your structural analysis could reveal important patterns in how different types of changes affect repository health[10].

## Conclusion

The proposed enhancements transform your project from a simple RAG-based system to a sophisticated multi-agent framework incorporating advanced structural analysis. The combination of graph-based representation, temporal analysis, and specialized agents creates a novel approach to repository understanding that extends beyond current state-of-the-art.

By focusing on structural properties and their evolution over time, your system will provide insights that aren't possible with text-only analysis, addressing your instructor's requirement for novelty beyond RAG. The roadmap provides a realistic path to completion within your 14-day timeframe, prioritizing core components while allowing for progressive refinement.

Sources
[1] GitHub Repositories For Llm Projects - Restack https://www.restack.io/p/large-language-models-answer-github-repositories-cat-ai
[2] Git Diff Explained: A Complete Guide with Examples - DataCamp https://www.datacamp.com/tutorial/git-diff-guide
[3] How to create a custom Agent that reviews git commits? #26082 https://github.com/langchain-ai/langchain/discussions/26082
[4] Brij kishore Pandey - Git Mastery Roadmap - LinkedIn https://www.linkedin.com/posts/brijpandeyji_git-mastery-roadmap-from-novice-to-advanced-activity-7220027142682619904-K23G
[5] GNN-FiLM: Graph Neural Networks with Feature-wise Linear ... https://openreview.net/forum?id=HJe4Cp4KwH
[6] Git Commit | Atlassian Git Tutorial https://www.atlassian.com/git/tutorials/saving-changes/git-commit
[7] How to git diff on an Azure DevOps CI pipeline with more than one ... https://stackoverflow.com/questions/78750895/how-to-git-diff-on-an-azure-devops-ci-pipeline-with-more-than-one-repository
[8] Automated Commit Message Generation with Large Language Models https://arxiv.org/html/2404.14824v1
[9] KazKozDev/NovelGenerator: Fiction generator using LLM ... - GitHub https://github.com/KazKozDev/NovelGenerator
[10] [PDF] The Impact of Large Language Models on Open-source Innovation https://arxiv.org/pdf/2409.08379.pdf
[11] Git Diff and Patch – Full Handbook for Developers - freeCodeCamp https://www.freecodecamp.org/news/git-diff-and-patch/
[12] Git Commit Reviewer - CodeGPT Help Center https://help.codegpt.co/en/articles/9904351-git-commit-reviewer
[13] Gitflow Workflow | Atlassian Git Tutorial https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
[14] [PDF] Adversarial Robustness - Graph Neural Networks https://graph-neural-networks.github.io/static/file/chapter8.pdf
[15] Conventional Commits https://www.conventionalcommits.org/en/v1.0.0/
[16] Git Diff | Atlassian Git Tutorial https://www.atlassian.com/git/tutorials/saving-changes/git-diff
[17] Shubhamsaboo/awesome-llm-apps - GitHub https://github.com/Shubhamsaboo/awesome-llm-apps
[18] Awesome-LLM: a curated list of Large Language Model - GitHub https://github.com/Hannibal046/Awesome-LLM
[19] Are there any q/a based LLM tools which could take in a github repo ... https://www.reddit.com/r/LocalLLaMA/comments/1b9lxqh/are_there_any_qa_based_llm_tools_which_could_take/
[20] How to turn any GitHub repository into LLM-ready text | Avi Chawla https://www.linkedin.com/posts/avi-chawla_how-to-turn-any-github-repository-into-llm-ready-activity-7276944630451974145-voti
[21] 40 LLM Projects to Upgrade Your AI Skillset in 2025 - ProjectPro https://www.projectpro.io/article/llm-project-ideas/881
[22] Git diff - GeeksforGeeks https://www.geeksforgeeks.org/git-diff/
[23] Insights into your git commits: Git Commit Analyzer - DEV Community https://dev.to/leopfeiffer/insights-into-your-git-commits-git-commit-analyzer-o1o
[24] Advanced Structure for Data Analysis - The Turing Way https://book.the-turing-way.org/project-design/project-repo/project-repo-advanced
[25] Git: Understanding and Using 'git diff two files' - LabEx https://labex.io/tutorials/git-git-understanding-and-using-git-diff-two-files-391177
[26] Agents | GenAIScript - Microsoft Open Source https://microsoft.github.io/genaiscript/reference/scripts/agents/
[27] Data Structures and Algorithms Roadmap https://roadmap.sh/datastructures-and-algorithms
[28] git-diff Documentation - Git https://git-scm.com/docs/git-diff
[29] mlabonne/graph-neural-network-course - GitHub https://github.com/mlabonne/graph-neural-network-course
[30] pyg-team/pytorch_geometric: Graph Neural Network Library for ... https://github.com/pyg-team/pytorch_geometric
[31] Changes · Graph Neural Networks · Wiki · IDA-IR-Public / docs - GitLab https://git.dcs.gla.ac.uk/ida-ir-public/wiki/-/wikis/Graph-Neural-Networks/diff?version_id=c246304f53066a2fbeb11d6ad116553228a3bf80&view=parallel
[32] Similarity equivariant graph neural networks for homogenization of ... https://www.sciencedirect.com/science/article/pii/S0045782525001392
[33] An Empirical Study on Commit Message Generation using LLMs via ... https://arxiv.org/html/2502.18904v1
[34] Open-Source Book Creator with Multi-Agent AI - DEV Community https://dev.to/guerra2fernando/open-source-book-creator-with-multi-agent-ai-1bnl
[35] How to Write Better Git Commit Messages – A Step-By-Step Guide https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/
[36] yangziwen/diff-check: Incremental code analysis tools ... - GitHub https://github.com/yangziwen/diff-check
[37] Automated Commit Message Generation with Large Language Models https://ui.adsabs.harvard.edu/abs/2024arXiv240414824X/abstract
[38] Building a Novel Generator with the Agent Kit | Docs | Breadboard https://breadboard-ai.github.io/breadboard/docs/guides/novel-generator/
[39] Protocol to explain graph neural network predictions using an edge ... https://pmc.ncbi.nlm.nih.gov/articles/PMC9700376/


# Objectives
Plan for Evaluation along with Dataset:
• Dataset: Git history from popular open-source projects (e.g., TensorFlow, scikit-learn, pandas)
• Evaluation Tasks:
• Given a function and its change, evaluate if the model can explain the reason accurately
• Compare LLM-generated explanations with actual commit messages/PR comments
• Use a human-annotated set of 20 examples for precision, relevance, and factuality
• Apply both zero-shot and RAG-based prompting strategies
• Optional: Turing-style evaluation where humans guess if explanation is Al- or human-written

# List of Supported Features:
• Analyze function-level changes across Git commits
• Trace the origin and evolution of bugs
• Summarize the reason for a Pull Request
• Identify the impact of a commit across files/modules
• Generate causal change graphs and timeline summaries
• Natural language query support (e.g., "Why was this function changed?")
• RAG (Retrieval Augmented Generation) with embeddings of code, diffs, and PR comments

