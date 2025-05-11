import networkx as nx
import matplotlib.pyplot as plt

# Define a sample function call structure
function_calls = {
    'main': ['load_data', 'process_data', 'save_results'],
    'load_data': ['read_file'],
    'process_data': ['clean_data', 'analyze_data'],
    'analyze_data': ['generate_report'],
    'clean_data': [],
    'read_file': [],
    'save_results': [],
    'generate_report': [],
    'unused_function': []  # dead code (no incoming edges)
}

# function_calls = {
#     #  This response is based on the provided package.json snippets.  Since no Python code was provided,
#     #  I cannot analyze function calls within a Python file.  The following is a placeholder
#     #  demonstrating the requested format, based on the Javascript package dependencies.

#     'installDependencies': ['resolveDependencies', 'downloadPackages'],
#     'resolveDependencies': ['checkVersionCompatibility'],
#     'downloadPackages': [],
#     'checkVersionCompatibility': [],
#     'buildProject': ['installDependencies', 'compileCode'],
#     'compileCode': [],
#     'runTests': ['buildProject'],
#     'deploy': ['runTests']
# }

# Create a directed graph
call_graph = nx.DiGraph()

# Add edges based on the call structure
for caller, callees in function_calls.items():
    for callee in callees:
        call_graph.add_edge(caller, callee)
    if not callees:
        call_graph.add_node(caller)  # Ensure leaf nodes are added too

# Draw the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(call_graph)
nx.draw(call_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10, arrows=True)
plt.title("Function Call Graph")
plt.show()
