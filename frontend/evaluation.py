from langchain.evaluation import load_evaluator
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = "AIzaSyDpnAn5_EpwuJWkHZubXaQ3TsZeSTuqGGg"

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
            10: "Fully accurate and matches the reference or correct answer.",
        },
    },
    {
        "metric": "Relevance",
        "scores": {
            0: "Completely unrelated to the question or input.",
            2: "Off-topic, barely addresses the intent.",
            4: "Partially relevant but drifts from the main point.",
            6: "Mostly on-topic, but includes some tangents.",
            8: "Directly relevant, only minor deviations.",
            10: "Fully focused, answers exactly what was asked.",
        },
    },
    {
        "metric": "Clarity",
        "scores": {
            0: "Incomprehensible or incoherent.",
            2: "Very hard to follow; confusing language or structure.",
            4: "Understandable with effort, but not clear.",
            6: "Generally clear but could be phrased better.",
            8: "Clear and well-structured explanation.",
            10: "Extremely clear, easy to understand even for a beginner.",
        },
    },
    {
        "metric": "Helpfulness",
        "scores": {
            0: "Not helpful at all, possibly harmful or distracting.",
            2: "Slightly helpful, very little value.",
            4: "Somewhat helpful but misses key needs.",
            6: "Moderately helpful, mostly usable.",
            8: "Very helpful, provides value and insight.",
            10: "Extremely helpful and actionable for the user.",
        },
    },
    {
        "metric": "Groundedness",
        "scores": {
            0: "Completely fabricated or hallucinated response.",
            2: "Largely made-up with little basis in input data.",
            4: "Includes both grounded and fabricated information.",
            6: "Mostly grounded with a few unsupported claims.",
            8: "Well-grounded, only very minor assumptions.",
            10: "Entirely based on and faithful to the input (code, context, files).",
        },
    },
]


# Load evaluator with Gemini model

queries1 = [
    "List all classifiers available in scikit-learn.",
    "Explain how cross-validation is implemented in scikit-learn.",
    "Where can I find the official documentation for scikit-learn’s PCA?",
    "Who are the main contributors or maintainers of scikit-learn?",
    "What coding conventions are followed in the scikit-learn codebase?",
    "Which files have the most changes in the `sklearn` package recently, and what were the types of those changes?",
    "Identify modules that frequently cause merge conflicts in scikit-learn and provide reasoning based on commit data.",
    "Summarize the major restructuring or refactoring events in scikit-learn’s repository over the last year.",
    "Trace how the `train_test_split` function has evolved over time, highlighting major bug fixes or feature additions.",
    "What are the internal dependencies of `sklearn.ensemble.RandomForestClassifier`?",
]
ground_truths1 = [
    "Scikit-learn offers several classifiers, including SVC, RandomForestClassifier, KNeighborsClassifier, LogisticRegression, DecisionTreeClassifier, and others. These can be found under sklearn.linear_model, sklearn.ensemble, sklearn.svm, sklearn.tree, etc.",
    "Cross-validation in scikit-learn is implemented using utilities like `cross_val_score`, `cross_validate`, and `GridSearchCV`. These tools split the dataset into multiple folds and train/test the model across different splits to evaluate generalization performance.",
    "The official PCA documentation can be found at: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html",
    "Scikit-learn is primarily maintained by the core developers listed in the CONTRIBUTORS.rst file. Some prominent contributors include Olivier Grisel, Gaël Varoquaux, and Andreas Mueller.",
    "Scikit-learn follows PEP8 coding standards and enforces strict linting rules. Code style is automatically checked using tools like flake8 and black. The contributing guide further outlines expectations for test coverage, docstrings, and type annotations.",
    "`sklearn/ensemble/_forest.py` and `sklearn/model_selection/_split.py` are among the most frequently changed files recently. Most changes are bug fixes, doc improvements, and feature additions like enhanced warm-start support or improved input validation.",
    "Modules like `sklearn.model_selection` and `sklearn.ensemble` occasionally cause merge conflicts due to their high activity and central role in API changes. Conflicts arise mainly from simultaneous edits by contributors to overlapping functions like cross-validation splitters or ensemble methods.",
    "Major refactoring in the past year includes: modularization of ensemble methods into separate files, introduction of type hints across key interfaces, and a move toward consistent estimator validation using `_validate_data()` across the codebase.",
    "`train_test_split` was originally introduced in `sklearn.cross_validation`, but was moved to `sklearn.model_selection`. Over time, enhancements included stratified splitting, support for custom test sizes, and more robust input validation.",
    "`RandomForestClassifier` depends on internal modules like `_forest.py`, `utils/validation.py`, and indirectly on `base.py` for Estimator interface. It also uses `joblib` for parallel computation and `numpy` for array operations.",
]
predictions1 = []


queries = [queries1]
predictions = [predictions1]
ground_truths = [ground_truths1]
rows = 2
cols = 5

# Create a 3x4 2D array (list of lists) of empty lists
scores = [[[] for _ in range(cols)] for _ in range(rows)]


ground_scores = [
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
]
for j in range(rows):
    for i in range(cols):
        evaluator = load_evaluator(
            "labeled_score_string", criteria=accuracy_criteria[i], llm=llm
        )
        print(accuracy_criteria[i]["metric"])
        for query, prediction, reference in zip(
            queries[j], predictions[j], ground_truths[j]
        ):
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


for j in range(1):
    for i in range(5):
        print(accuracy_criteria[i]["metric"])
        print(scores[j][i])
    print("=" * 60)

with open("results.txt", "w") as f:
    for j in range(1):
        print("scores of repo: " + str(j + 1), file=f)
        for i in range(5):
            print(accuracy_criteria[i]["metric"], file=f)
            print(scores[j][i], file=f)
        print("=" * 60, file=f)
