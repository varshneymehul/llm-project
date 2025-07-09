from langchain.evaluation import load_evaluator
from langchain_google_genai import ChatGoogleGenerativeAI

api_key  = "AIzaSyDpnAn5_EpwuJWkHZubXaQ3TsZeSTuqGGg"

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
)

# Define the accuracy criteria
# accuracy_criteria = {
#     "accuracy": """
# Score 1: The answer is completely unrelated to the reference.
# Score 3: The answer has minor relevance but does not align with the reference.
# Score 5: The answer has moderate relevance but contains inaccuracies.
# Score 7: The answer aligns with the reference but has minor errors or omissions.
# Score 10: The answer is completely accurate and aligns perfectly with the reference."""
# }

# accuracy_criteria = {
#     "accuracy": """
#     Score 0: "Completely fails in all aspects — inaccurate, irrelevant, unclear, unhelpful, and not grounded.",
#     Score 1: "Barely acceptable in any area; mostly hallucinated or confusing.",
#     Score 2: "Fails most metrics; might show a hint of relevance or clarity but still largely unhelpful or incorrect.",
#     Score 3: "Shows partial effort with moderate clarity or relevance, but lacking in accuracy and groundedness.",
#     Score 4: "Some metrics are met (e.g., relevance or clarity), but contains factual or grounding issues.",
#     Score 5: "A mixed response; reasonably clear or helpful, but flawed in accuracy or grounding.",
#     Score 6: "Above average — mostly accurate, fairly relevant, somewhat helpful, and grounded with minor clarity issues.",
#     Score 7: "Good response — accurate, relevant, grounded and fairly clear, though may lack depth or have small gaps.",
#     Score 8: "Very good — strong in atleast 4 metrics with minor imperfections.",
#     Score 9: "Nearly perfect — excels in all five metrics with negligible issues.",
#     Score 10: "Excellent — fully accurate, highly relevant, crystal clear, extremely helpful, and completely grounded." """

# }

accuracy_criteria = [
    {
        "metric": "Accuracy",
        "scores": {
            0: "Completely incorrect; contradicts the ground truth.",
            2: "Major factual errors, mostly wrong.",
            4: "Some correct points but largely inaccurate or misleading.",
            6: "Mostly accurate with minor factual errors.",
            8: "Accurate with negligible mistakes or phrasing inconsistencies.",
            10: "Fully accurate and matches the reference or correct answer."
        }
    },
    {
        "metric": "Relevance",
        "scores": {
            0: "Completely unrelated to the question or input.",
            2: "Off-topic, barely addresses the intent.",
            4: "Partially relevant but drifts from the main point.",
            6: "Mostly on-topic, but includes some tangents.",
            8: "Directly relevant, only minor deviations.",
            10: "Fully focused, answers exactly what was asked."
        }
    },
    {
        "metric": "Clarity",
        "scores": {
            0: "Incomprehensible or incoherent.",
            2: "Very hard to follow; confusing language or structure.",
            4: "Understandable with effort, but not clear.",
            6: "Generally clear but could be phrased better.",
            8: "Clear and well-structured explanation.",
            10: "Extremely clear, easy to understand even for a beginner."
        }
    },
    {
        "metric": "Helpfulness",
        "scores": {
            0: "Not helpful at all, possibly harmful or distracting.",
            2: "Slightly helpful, very little value.",
            4: "Somewhat helpful but misses key needs.",
            6: "Moderately helpful, mostly usable.",
            8: "Very helpful, provides value and insight.",
            10: "Extremely helpful and actionable for the user."
        }
    },
    {
        "metric": "Groundedness",
        "scores": {
            0: "Completely fabricated or hallucinated response.",
            2: "Largely made-up with little basis in input data.",
            4: "Includes both grounded and fabricated information.",
            6: "Mostly grounded with a few unsupported claims.",
            8: "Well-grounded, only very minor assumptions.",
            10: "Entirely based on and faithful to the input (code, context, files)."
        }
    }
]


# Load evaluator with Gemini model

queries1 = [
    "What is the purpose of this repository?",
    "How do I set up the project on my local machine?",
    "Where can I find the API documentation?",
    "Who should I contact if I encounter issues with the documentation?",
    "Are there any coding standards or best practices I need to follow?",
    "Which files in the repository have undergone the most changes in the past six months, and what types of changes (additions, deletions, refactors) were most common for each file?",
    "Can you identify any files that have frequent merge conflicts, and analyze the reasons behind these conflicts based on commit history and file ownership?",
    "List all major documentation structure changes (such as file moves, renames, or reorganizations of directories) in the last year, along with the commits and authors responsible for them.",
    "For the main documentation file (e.g., 'README.md' or 'index.md'), summarize the most significant content changes over time and explain how these changes impacted the onboarding process for new employees.",
    "Trace the evolution of a specific section or topic (for example, 'API Authentication') across all relevant files and commits, highlighting how the documentation and implementation have changed in response to feature updates or bug fixes.",
    "on what files does the file ByRating.jsx depend on?" 
]

ground_truths1 = [
    "The repository is bootstrapped using Create React App. It's intended to make a web app which gets information related to various books using apis and displays them by category ",
    "1. Clone the repo: `git clone https://github.com/codingfreshie/my_react_app.git && cd my_react_app`\n"
    "2. Install dependencies: `npm install`\n"
    "3. Start the development server: `npm start`",
    "There is no dedicated API documentation in this repo. It's a React front-end template using rapid apis.",
    "There is no specified maintainer. If issues arise, users should raise them through GitHub Issues or the owner of this repo who is neeharika.",
    "No explicit coding standards are documented. You can follow general React best practices, such as using functional components and consistent naming.",
    "There is only one commit in the repository, so no file has undergone multiple changes in the past six months.",
    "The repository has no history of merge conflicts due to minimal activity and a single initial commit.",
    "No major documentation structure changes have occurred since the repo only has one commit and the structure has remained static.",
    "The README.md file has not changed over time. There is no version history of content updates to analyze onboarding impact.",
    "The repository lacks any features like API Authentication or tracked section evolution. There are no commits that document the evolution of such a topic.",
    "usestate and fetch from react, and card.jsx"


]
                                                                                                
predictions1 = [
    "Based on the provided information, the repository appears to be for a React-based web application that displays and searches for books. The application allows users to view book details, add books to a favorites list, and sort books by rating. The project uses Create React App for its build process and likely includes a testing framework (possibly Jest). The exact purpose beyond this book display and search functionality is not explicitly stated in the available data.",
    "To set up this project on your local machine, you'll need to follow these steps. Since I don't have access to the complete package.json file, I'll provide general instructions assuming it's a standard Create React App project. If there are any deviations, you'll need to adjust accordingly based on the contents of your package.json. 1. Prerequisites: * Node.js and npm (or yarn): Make sure you have Node.js and npm (Node Package Manager) installed on your system. You can download them from https://nodejs.org/. Yarn is an alternative package manager; if you prefer it, install it according to its instructions. 2. Cloning the Repository: * Obtain the Git repository URL. * Open your terminal or command prompt. * Navigate to the directory where you want to clone the project. * Use the git clone command to clone the repository: git clone <repository_url> (Replace <repository_url> with the actual URL). 3. Installing Dependencies: * Navigate to the cloned project directory: cd <project_directory> * Install the project's dependencies using npm: npm install (Or use yarn install if you're using Yarn). This will install all the packages listed in package.json into the node_modules directory. 4. Starting the Development Server: * Once the dependencies are installed, start the development server using: npm start (Or yarn start). * This will usually open the application in your default web browser. If not, you'll find the URL in the terminal output. 5. (Optional) Running Tests: * If the project includes tests (which is likely given the use of Create React App), you can run them using: npm test (Or yarn test). Troubleshooting: * Dependency Errors: If you encounter errors during the npm install step, carefully examine the error messages. They often indicate missing dependencies or version conflicts. Try resolving these issues by checking your internet connection, ensuring you have the correct Node.js and npm versions, and potentially cleaning your npm cache (npm cache clean --force). * Port Conflicts: If the development server fails to start, it might be due to a port conflict. Try changing the port in the package.json scripts (if possible) or stopping any other applications that might be using the same port. These instructions provide a general outline. Refer to the project's README.md file (if available) for more specific setup instructions or any project-specific configurations.",
    "I'm sorry, but the provided text doesn't contain any information about API documentation. The text describes a React application that fetches data from an API, but it doesn't specify where the API documentation is located. To find the API documentation, you would need to: 1. Check the project's README.md file: A well-documented project will often include a link to the API documentation in its README file. 2. Look for comments in the code: The code itself might contain comments that point to the API documentation. Search for comments related to API calls or endpoints. 3. Examine the API calls in the code: The code likely makes calls to specific API endpoints. The URLs used in these calls might provide clues about the location of the API documentation. For example, if the code calls an endpoint like /api/v1/books, the documentation might be located at a URL like /api/v1/docs or a similar path. 4. Ask the project maintainers: If you can't find the documentation using the above methods, you can try contacting the project maintainers or developers to ask for a link to the API documentation. Without more information about the project or access to the project's codebase, I cannot provide a more specific answer.",
    "I apologize, but I need more information to answer your question. The provided text doesn't name any individuals or teams responsible for the project's documentation. To find out who to contact for documentation issues, you should: 1. Check the project's README.md file: The README often contains contact information for the project maintainers or a link to an issue tracker where you can report problems. 2. Look for a CONTRIBUTING.md file: This file usually outlines how to contribute to the project, including how to report bugs or request help with the documentation. 3. Examine the repository's metadata: The repository itself might have information about the owners or contributors, which could provide contact details. Look for information on the Git platform (like GitHub, GitLab, or Bitbucket). 4. Search for the project online: A quick web search for the project name might lead you to a website or forum where you can find contact information or report issues. Without access to the project's files or repository information, I cannot provide specific contact details.",
    "To determine the coding standards and best practices for this project, we need more information. However, based on the fact that it's a React application built with Create React App, we can make some educated guesses and suggest general best practices that are widely applicable: 1. JavaScript/JSX Best Practices: * Consistent Indentation and Formatting: Use a consistent indentation style (e.g., 2 spaces) throughout the codebase. Consider using a code formatter like Prettier to automatically enforce consistent formatting. * Meaningful Variable and Function Names: Choose descriptive names that clearly indicate the purpose of variables and functions. Follow a consistent naming convention (e.g., camelCase). * Avoid Global Variables: Minimize the use of global variables to improve code maintainability and reduce the risk of unintended side effects. Favor passing data through props or using state management solutions. * Modular Code: Break down the code into smaller, reusable components and functions. This improves code organization, readability, and testability. * Error Handling: Implement proper error handling mechanisms to gracefully handle potential errors and prevent unexpected crashes. Use try...catch blocks and handle errors appropriately. * Comments: Write clear and concise comments to explain complex logic or non-obvious code sections. Avoid redundant comments that simply restate the obvious. 2. React-Specific Best Practices: * Functional Components and Hooks: Prefer using functional components with hooks (useState, useEffect, etc.) over class components. Hooks provide a more concise and readable way to manage component state and side effects. * Props Drilling: Avoid passing props down through multiple levels of nested components. Consider using context API or a state management library (like Redux, Zustand, or Jotai) for managing state that needs to be accessed across multiple components. * Component Reusability: Design components to be reusable wherever possible. This reduces code duplication and improves maintainability. * State Management: Choose an appropriate state management solution based on the complexity of the application. For smaller applications, the Context API might suffice. For larger applications, a dedicated state management library is often necessary. * Testing: Write unit and integration tests to ensure the correctness and reliability of the code. Create React App typically uses Jest for testing. 3. General Software Engineering Best Practices: * Version Control: Use Git effectively to manage code changes, collaborate with others, and track the project's history. * Code Reviews: Conduct regular code reviews to identify potential bugs, improve code quality, and share knowledge among team members. * Documentation: Write clear and concise documentation to explain the project's architecture, functionality, and usage. * Continuous Integration/Continuous Deployment (CI/CD): If appropriate for the project's scale, set up a CI/CD pipeline to automate the build, testing, and deployment process. Finding Project-Specific Guidelines: The best way to determine the specific coding standards and best practices for this project is to: * Check the project's README.md file: This file often contains information about coding style guides, preferred tools, and other project-specific guidelines. * Look for a .editorconfig file: This file specifies editor settings for consistent code formatting. * Examine the existing codebase: Observe the coding style used in the existing code to get a sense of the project's conventions. Without access to the project's files, these general best practices are the most I can offer. Always prioritize readability, maintainability, and testability in your code.",
    "I cannot answer your question about the most changed files in the last six months and the types of changes because the provided context lacks the necessary Git history data. To answer this, I would need access to the repository's commit history, specifically the commit logs for the past six months. This data would allow me to identify which files had the most commits, and by analyzing the diffs within those commits, I could determine the types of changes (additions, deletions, modifications). The current information only provides a snapshot of the files present in the repository, not their change history over time.",
    "I cannot identify files with frequent merge conflicts and analyze the reasons for those conflicts. The provided context lacks the necessary data: the detailed Git commit history, including information about merge commits and the specific changes involved in those merges. To perform this analysis, I would need access to the repository's complete commit history, which would allow me to: 1. Identify Merge Commits: Locate all commits that are the result of merging branches. 2. Analyze Conflicted Files: For each merge commit, determine which files had merge conflicts. This information is typically included in the commit message or the commit's diff. 3. Examine Changes: Analyze the changes made in the branches that were merged to understand the nature of the conflicts. This would involve looking at the code changes in each branch to see where they diverged and caused conflicts. 4. Determine File Ownership: While Git doesn't explicitly track \"file ownership\" in the same way a project management system might, I could infer ownership based on the commit history. The developers who most frequently modified a file are likely the ones most responsible for its content. 5. Identify Common Conflict Reasons: By analyzing multiple merge conflicts involving the same files, I could identify patterns and common causes of conflicts, such as: * Simultaneous Changes in the Same Section of Code: Multiple developers modifying the same lines of code. * Conflicting Logic or Functionality: Changes that introduce incompatible logic or behavior. * Overlapping Feature Development: Features that affect the same parts of the codebase. * Lack of Communication or Coordination: Developers working on the same files without sufficient communication. Without access to the repository's commit history, I can only provide a general framework for how this analysis would be performed. The analysis requires detailed Git data beyond what's currently available.",
    "I cannot provide a list of major documentation structure changes (file moves, renames, directory reorganizations) in the last year, including associated commits and authors. The provided context lacks the necessary Git history data. To perform this analysis, I would need access to the repository's commit history for the past year. This history would need to include information about: * File Renames: Git records file renames, but I need access to the commit details to extract this information. * File Moves: Similar to renames, file moves are tracked in Git's history, but I need access to the commit data to identify them. * Directory Reorganizations: Changes to the directory structure are also recorded in the commit history. I need access to this data to list the changes. * Commit Information: For each change, I need the commit hash, author, date, and commit message to provide a complete record. The current information only provides a snapshot of the files present in the repository at some point in time, not their history or how the structure evolved. Therefore, I cannot fulfill this request without access to the repository's Git history.",
    "I cannot summarize the most significant content changes over time for the main documentation file (e.g., README.md or index.md) and explain how these changes impacted the onboarding process for new employees. The provided context lacks the necessary information: the complete history of changes to the documentation file(s). To perform this analysis, I would need access to the repository's commit history, specifically the commits that modified the main documentation file(s). For each commit, I would need: * The commit message: This often summarizes the changes made. * The diff: This shows the exact changes made to the file's content in each commit. * The commit author and date: This provides context for the changes. With this information, I could: 1. Identify Significant Changes: Analyze the diffs to identify major additions, deletions, or modifications to the documentation. This might include changes to the project's overview, setup instructions, usage examples, API documentation, or contribution guidelines. 2. Summarize Changes Over Time: Create a chronological summary of the most significant changes, highlighting the key improvements or updates to the documentation. 3. Assess Impact on Onboarding: Based on the changes, I could assess their impact on the onboarding process. For example: * Improved Clarity: Changes that improved the clarity or completeness of the documentation would likely make onboarding easier. * Added Complexity: Changes that introduced new concepts or complexities might make onboarding more challenging. * Missing Information: Gaps or omissions in the documentation could hinder the onboarding process. * Structural Changes: Reorganization of the documentation could impact how easily new employees find the information they need. Without access to the repository's commit history and the documentation files themselves, I cannot perform this analysis.",
    "I cannot trace the evolution of the \"API Authentication\" section across all relevant files and commits, highlighting how documentation and implementation changed in response to feature updates or bug fixes. The provided context lacks the necessary data: the complete commit history of the repository, including the contents of all files involved in API authentication (both code and documentation). To perform this analysis, I would need access to the repository's complete commit history, allowing me to: 1. Identify Relevant Files: Determine which files contain code related to API authentication (e.g., authentication services, controllers, routes, configuration files) and which files contain documentation related to API authentication (e.g., README files, API specifications, Wiki pages). 2. Trace Changes Over Time: For each relevant file, I would analyze the commit history to identify all commits that modified the file. This would involve examining the diffs for each commit to understand the nature of the changes. 3. Correlate Changes with Feature Updates and Bug Fixes: By examining the commit messages and the changes themselves, I would attempt to correlate the changes in the API authentication section with specific feature updates or bug fixes. This would involve looking for keywords in commit messages (e.g., \"bug fix,\" \"feature update,\" \"security improvement\") and analyzing the code changes to understand their impact on authentication. 4. Analyze Documentation Changes: I would pay close attention to changes in documentation files related to API authentication. This would help to understand how the documentation evolved in response to changes in the implementation. I would look for improvements in clarity, completeness, or accuracy of the documentation. 5. Identify Patterns: By analyzing the evolution of the API authentication section over time, I could identify patterns in how the system was developed and maintained. This might reveal insights into the development process, the team's approach to security, and the overall quality of the codebase. Without access to the repository's commit history and file contents, I cannot perform this detailed historical analysis. The analysis requires a comprehensive understanding of the project's evolution, which is not available in the current context.",
    "Based on the provided information, ByRating.jsx depends on at least the following files: * External Libraries (Implicit): ByRating.jsx uses useState and fetch, implying dependencies on React and potentially a polyfill for fetch if the target environment doesn't support it natively. These dependencies would be listed in package.json. * card.jsx (or similar): The description indicates that ByRating.jsx renders a list of book cards. This strongly suggests a dependency on a component named card (with a .jsx, .js, .ts, or .tsx extension). This component is responsible for rendering individual book cards. * Potentially other files: The exact dependencies might include additional files for styling (CSS), data processing, or error handling, but these are not explicitly mentioned. The provided data doesn't give a complete picture of all dependencies. A more thorough analysis would require access to the ByRating.jsx file itself to examine its import statements."
]

queries2 = [
    "What is the purpose of this repository?",
    "How do I set up the project on my local machine?",
    "Where can I find the API documentation?",
    "Who should I contact if I encounter issues with the documentation?",
    "Are there any coding standards or best practices I need to follow?",
    "Which files in the repository have undergone the most changes in the past six months, and what types of changes (additions, deletions, refactors) were most common for each file?",
    "Can you identify any files that have frequent merge conflicts, and analyze the reasons behind these conflicts based on commit history and file ownership?",
    "List all major documentation structure changes (such as file moves, renames, or reorganizations of directories) in the last year, along with the commits and authors responsible for them.",
    "For the main documentation file (e.g., 'README.md' or 'index.md'), summarize the most significant content changes over time and explain how these changes impacted the onboarding process for new employees.",
    "give commit history of app/about/page.js",
    "what changes were made in the second commit in app/components/AboutUsCard.module.css" 
]

predictions2 = [
    "Based on the provided text, this repository appears to be related to BITSAA International Inc., a non-profit organization supporting Birla Institute of Technology & Science (BITS) Pilani. The text describes BITSAA's mission: raising funds for endowments and scholarships, promoting research and teaching, and fostering connections among alumni, students, faculty, and friends of the institute. There's also mention of making BITS alumni experiences accessible to current students. However, the included \"post-update\" hook script snippet suggests the repository itself is likely a technical resource, perhaps used for managing BITSAA's website or internal systems. The hook prepares a packed repository for use over \"dumb transports,\" indicating a focus on efficient data transfer, possibly for a distributed version control system like Git. The purpose of the repository's content is to support BITSAA's mission, but the repository's own purpose is to manage that content efficiently.",
    "I need the contents of the Git repository to answer how to set up this project locally. The previous response only gave me a description of the repository's purpose and a snippet of a post-update hook. To provide setup instructions, I need information such as: * Repository type: Is it a Git repository hosted on GitHub, GitLab, Bitbucket, or elsewhere? Knowing the hosting platform will determine the cloning method. * Repository URL: The URL is essential for cloning the repository. * Dependencies: Does the project have any dependencies (e.g., specific software versions, libraries, databases)? These need to be installed before the project can run. * Build instructions: Are there any build scripts (e.g., Makefile, setup.py, package.json) or instructions on how to build the project? * Run instructions: How do I run the project after it's been set up? Are there any configuration files or commands needed? * Operating system requirements: Does the project have specific operating system requirements (e.g., Windows, macOS, Linux)? Once you provide this information, I can give you precise setup instructions.",
    "I need access to the Git repository to answer your question. I cannot locate API documentation without access to the codebase's files and commit history. Please provide me with the repository's URL or a local path. Once provided, I can search for files commonly used for API documentation (e.g., README.md, docs/, a docs folder containing files like index.html, .rst files for Sphinx documentation, *.md files, etc.) and analyze their content to determine if they contain API specifications.",
    "I need access to the Git repository to answer your question. Without access to the codebase, I cannot determine who is responsible for maintaining the API documentation. The information might be found in: * A README.md file: Often contains contact information for reporting issues or links to issue trackers. * The repository's main website (if one exists): The website might have a \"Contact Us\" section or a link to an issue tracker. * The repository's issue tracker (e.g., GitHub Issues, GitLab Issues, Bitbucket Issues): This is the most likely place to report issues, even if the README doesn't explicitly state it. The issue tracker might also provide labels or assignees that indicate who is responsible for the documentation. * Within the API documentation itself: The documentation might contain a section on reporting issues or contacting support. Please provide me with the repository's URL or a local path so I can search for this information within the repository's files and commit history.",
    "I need access to the Git repository to answer your question. Without access to the codebase, I cannot determine the specific coding standards or best practices used in the project. However, I can suggest places to look for this information once you provide the repository: * A README.md file: Often contains a section describing coding style guidelines, preferred tools, or links to external style guides (e.g., PEP 8 for Python). * A CONTRIBUTING.md file: This file often outlines contribution guidelines, including coding standards and best practices that contributors should follow. * A .editorconfig file: This file specifies editor settings for consistent code formatting across different editors and IDEs. * A .stylelintrc (or similar) file: This file defines the rules for code style linting, indicating the preferred style for the project. * The project's issue tracker: Discussions about coding style or best practices might be found in issues or pull requests. * The project's commit history: Commit messages might contain references to style changes or the adoption of new best practices. I can analyze the commit history to identify such changes once you provide the repository. Please provide me with the repository's URL or a local path so I can search for this information within the repository's files and commit history.",
    "I need access to the Git repository to answer your question. Once you provide the repository's URL or local path, I can perform the following analysis: 1. Identify Files: I will traverse the repository's commit history for the past six months. 2. Track Changes: For each file, I will count the number of commits that modified it. I will analyze the diffs within those commits to categorize changes as: * Additions: Lines of code added. * Deletions: Lines of code removed. * Refactors: Changes that alter the code's structure or logic without significantly changing its functionality (this is more challenging to automatically detect perfectly and may require some heuristics). I will look for patterns like renaming variables, functions, or classes, moving code blocks, and changes to internal structure without altering the overall input/output behavior. 3. Rank Files: I will rank the files based on the total number of changes (additions + deletions) over the six-month period. 4. Report Results: My output will be a table or list showing: * File name * Total number of changes (additions + deletions) * Number of additions * Number of deletions * Dominant change type (additions, deletions, or refactors, based on which category has the highest count). If additions and deletions are roughly equal, I will indicate that as \"mixed\". Please provide the repository's URL or local path.",
    "I need access to the Git repository to answer your question. Once you provide the repository's URL or local path, I can perform the following analysis: 1. Identification of files with frequent merge conflicts: I will traverse the repository's commit history looking for commits containing messages indicating merge conflicts (e.g., \"Merge branch 'feature-x'\", \"Merge pull request #123\", or messages including the word \"conflict\"). I will also analyze the diffs of these commits to identify files that were modified in both branches being merged, indicating a conflict. I will count how frequently each file was involved in merge conflicts. 2. Analysis of the reasons for conflicts: For each file with frequent conflicts, I will analyze the commit history to try to determine the reasons for the conflicts. This might include: * Concurrent changes in the same section of code: If two or more developers modified the same part of a file simultaneously, a conflict is likely. I will analyze the diffs to identify the sections of code that caused the conflicts. * Naming conflicts: Conflicts can arise if files or functions are renamed differently in different branches. * Changes in code structure: Significant changes to a file's structure (e.g., adding or removing functions or classes) can lead to conflicts if done in parallel on different branches. * File ownership: I will attempt to identify the developers who modified each file most frequently. This can help determine if certain developers are more prone to causing conflicts due to a lack of communication or coordination. This information will be obtained from the commit history, looking at the username or email associated with each commit. 3. Reporting results: My output will be a report including: * A list of files ordered by the frequency of merge conflicts. * For each file, a summary of the likely reasons for the conflicts, based on the analysis of the commit history and file ownership. * If possible, I will identify the developers involved in frequent conflicts for each file. Please provide the URL or local path to the repository." ,
    "I need access to the Git repository to answer your question. Once you provide the repository's URL or local path, I can perform the following analysis: 1. Identify Documentation Files: I will first identify files likely to be part of the documentation. This includes files with common extensions like .md, .rst, .html, and files located in directories named docs, documentation, etc. 2. Analyze Commit History: I will then analyze the repository's commit history for the past year. For each commit, I will examine the diff to detect the following types of changes: * File Renames: I will identify commits that rename documentation files. * File Moves: I will identify commits that move documentation files to different directories. * Directory Reorganizations: I will detect commits that create, delete, or rename directories containing documentation files. This will involve analyzing the changes in directory structures. 3. Gather Commit Information: For each commit that involved a major documentation structure change (as defined above), I will extract the following information: * Commit Hash: The unique identifier for the commit. * Commit Message: The description of the changes made in the commit. * Author: The name and email address of the author of the commit. * Date: The date and time the commit was made. * Specific Changes: A detailed description of the file moves, renames, or directory reorganizations that occurred in the commit. 4. Report Results: My output will be a report summarizing the major documentation structure changes in the last year. The report will be organized chronologically and will include all the information gathered in step 3 for each relevant commit. Please provide the repository's URL or local path.",
    "i dont know",
    "need url",
    "need url"
]

ground_truths2 =[
    "The repository is a personal project by Mehul Varshney, related to web development .It is a website for a club named Embryo in Bits Pilani.",
    "clone the repo and folow standard procedures",
    "no specific api documentation is provided",
    "the owner of the repo-Mehul varshney",
    "nothing in specfic",
    "few css changes ",
    "no merge conflicts so far",
    "none so far",
    "The README.md file has not changed over time. There is no version history of content updates to analyze onboarding impact.",
    """
    {
    "file_path": "app/about/page.js",
    "file_name": "page.js",
    "file_extension": ".js",
    "commit_count": 2,
    "first_commit_date": "2024-04-16T20:28:33+05:30",
    "last_commit_date": "2024-08-11T17:09:13+05:30",
    "commits": [
        {
        "commit_time": "2024-04-16T20:28:33+05:30",
        "commit_hash": "6e3886ef2cefc506f6436f11c0bb5537e685a9b1",
        "commit_message": "first commit",
        "author": "Mehul Varshney <varshneymehul5@gmail.com>",
        "change_summary": {
            "lines_added": 61,
            "lines_removed": 0,
            "additions": [
            "import AboutUsCard from \"./components/AboutUsCard\";",
            "const About = () => {",
            "return (",
            "<main className=\"mx-12 md:mx-16 items-center justify-between dark:text-white\">",
            "<h1 className=\"text-4xl md:text-7xl p-12 text-center font-serif\">",
            "ABOUT",
            "</h1>",
            "<p className=\"dark:text-white  my-4 text-xs md:text-lg  \">",
            "Embryo is a forum for on-line, live and interactive lectures, run by",
            "students and faculties of BITS-Pilani. It was conceived and initiated by",
            "a group of 6 BITS Pilani Alumni in the Silicon Valley in 2006 with an",
            "aim to transform classroom education. Since February, 2006, more than",
            "200 lectures have been successfully conducted in areas as wide ranging",
            "as Entrepreneurship, Black Holes, Solar Cells, Science of Smell,",
            "Naxalism, Rain water harvesting,Storage Networks, PSOCs, Process",
            "Control. In August 2010, Embryo 2.0 was launched. Since then we have",
            "conducted a series of lectures. The lecturer works closely with the",
            "course faculty and in a few cases, the lecture content is subject to",
            "evaluative components. The knowledge of the alumni has thus become an",
            "integral part of the BITS curriculum.",
            "</p>",
            "<AboutUsCard",
            "title={\"VISION\"}",
            "content={\"Enrich the learning experience at BITS Pilani.\"}",
            "/>",
            "<AboutUsCard",
            "title={\"MISSION\"}",
            "content={",
            "\"To make the academic and industrial experience of the BITS alumni accessible to on-campus students through lectures, collaborative research projects, and exposure to current research trends around the world.\"",
            "}",
            "/>",
            "<AboutUsCard",
            "title={\"WHY EMBRYO?\"}",
            "content={",
            "\"Although there is no alternative to 'in person' classroom teaching, any University in the world is limited by its on-campus human resources and available expertise. Often, a lecture or two in the right area by the right person can change the course of one's career. Embryo proposes to free education from the barriers of distance, time and human resources. Leveraging web-based technologies, Embryo acts as a bridge between the knowledge seekers (students), and the potential speakers. Such a powerful method truly realizes the dream of border less classrooms and bottomless learning resources.\"",
            "}",
            "/>",
            "",
            "<AboutUsCard",
            "title={\"AVAILABLE INFRASTRUCTURE\"}",
            "content={",
            "\"With the advent of BITS Connect2.0 , we now have state of the art telepresence solutions across all campuses thus making the experience even richer.\"",
            "}",
            "/>",
            "<AboutUsCard",
            "title={\"ABOUT BITS PILANI\"}",
            "content={",
            "\"Birla Institute of Technology and Science (BITS), Pilani is a Leading University in India offering degrees in Engineering, Management, Pharmacy, Sciences, Engineering Technology, Information Systems, General Studies, Finance etc presently at Pilani, Dubai, Goa and Hyderabad campuses. BITS Pilani also offers an array of work integrated learning programmes for HRD of a vast spectrum of Indian corporates.\"",
            "}",
            "/>",
            "<AboutUsCard",
            "title={\"ABOUT BITSAA\"}",
            "content={",
            "\"BITSAA International Inc. is a not-for-profit organization. The primary purpose of BITSAA International is to engage in charitable and educational activities by raising funds for setting up endowments, creating scholarships, rewarding teaching and research and generally promoting the development of resources at Birla Institute of Technology & Science at Pilani. BITSAA International also aims to strengthen the ties, friendship and communications amongst former students, current students, faculty and friends of the Institute. BITSAA International provides a number of channels for people to stay connected with each other and the Birla Institute of Technology & Science.\"",
            "}",
            "/>",
            "</main>",
            ");",
            "};",
            "",
            "export default About;"
            ],
            "deletions": [],
            "modifications": [],
            "functions_added": [],
            "functions_modified": [],
            "functions_removed": [],
            "change_type": "addition",
            "classes_added": [],
            "classes_removed": [],
            "imports_added": [
            "AboutUsCard"
            ],
            "imports_removed": []
        },
        "cumulative_state": {
            "functions": [],
            "classes": [],
            "imports": [
            "AboutUsCard"
            ]
        }
        },
        {
        "commit_time": "2024-08-11T17:09:13+05:30",
        "commit_hash": "3b5698569f1db2f6b17b5413b7eaf5d6b5cf8453",
        "commit_message": "fix bugs on homepage",
        "author": "Mehul Varshney <varshneymehul5@gmail.com>",
        "change_summary": {
            "lines_added": 2,
            "lines_removed": 2,
            "additions": [
            "<main className=\"mx-12 pb-4 md:mx-16 items-center justify-between dark:text-white\">",
            "<p className=\"dark:text-white  my-4 text-xs md:text-lg text-justify\">"
            ],
            "deletions": [
            "<main className=\"mx-12 md:mx-16 items-center justify-between dark:text-white\">",
            "<p className=\"dark:text-white  my-4 text-xs md:text-lg  \">"
            ],
            "modifications": [],
            "functions_added": [],
            "functions_modified": [],
            "functions_removed": [],
            "change_type": "modification",
            "classes_added": [],
            "classes_removed": [],
            "imports_added": [],
            "imports_removed": []
        },
        "cumulative_state": {
            "functions": [],
            "classes": [],
            "imports": [
            "AboutUsCard"
            ]
        },
        "evolution": {
            "new_functions": [],
            "new_classes": [],
            "new_imports": []
        }
        }
    ]
    }
    """,
    " fix colours,\"additions\": [\"font-size: 1.5rem;\",\"font-size: 1rem;\"],\"deletions\": [\"font-size: 1.25rem;\",\"\",\"font-size: 0.75rem;\"],",

]


queries = [queries1,queries2]
predictions = [predictions1,predictions2]
ground_truths = [ground_truths1,ground_truths2]
rows = 2
cols = 5

# Create a 3x4 2D array (list of lists) of empty lists
scores = [[[] for _ in range(cols)] for _ in range(rows)]


ground_scores =[[10,10,10,10,10,10,10,10,10,10,10],[10,10,10,10,10,10,10,10,10,10,10]]
for j in range(rows):
    for i in range(cols):
        evaluator = load_evaluator(
            "labeled_score_string", criteria=accuracy_criteria[i], llm=llm
        )
        print(accuracy_criteria[i]["metric"])
        for query, prediction, reference in zip(queries[j], predictions[j], ground_truths[j]):
            try:
                eval_result = evaluator.evaluate_strings(
                    prediction=prediction,
                    reference=reference,
                    input=query,
                )
                scores[j][i].append(eval_result["score"])
                print(f"Query: {query}")
                # print(f"Prediction: {prediction}")
                # print(f"Ground Truth: {reference}")
                print("Score: " + str(eval_result["score"]))
                # print("Reasoning: " + eval_result["reasoning"])
                print("=" * 60)
            except Exception as e:
                print(f"Query: {query}")
                print("Score: " + str(0))
                scores[j][i].append(0)
                print("=" * 60)
        

for j in range(2):
    for i in range(5):
        print(accuracy_criteria[i]["metric"])
        print(scores[j][i])
    print("=" * 60)

with open("results.txt", "w") as f:
    for j in range(2):
        print("scores of repo: "+str(j+1), file=f)
        for i in range(5):
            print(accuracy_criteria[i]["metric"], file=f)
            print(scores[j][i], file=f)
        print("=" * 60, file=f)
