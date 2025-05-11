import networkx as nx
import matplotlib.pyplot as plt

# Sample data: Each commit modifies some files
# commit_file_map = {
#     'c1': ['file1.py', 'file2.py'],
#     'c2': ['file2.py', 'file3.py'],
#     'c3': ['file1.py', 'file3.py', 'file4.py'],
#     'c4': ['file4.py'],
#     'c5': ['file5.py'],
# }


commit_file_map = {
    "195eb03e80ec73123dc45ff4dc44d765918fed34": [
        "assets/img/logos/logo-ibm@2x.png",
        "assets/img/logos/rmit@2x.png",
        "assets/vid/A connected team discussing work in multiple channels in the Slack app.webm",
        "assets/img/logos/logo-xero@2x.png",
        "assets/img/google.jpg",
    ]
}

# Create a bipartite graph
B = nx.Graph()

# Add nodes with bipartite attributes
commits = list(commit_file_map.keys())
files = sorted(set(f for fs in commit_file_map.values() for f in fs))

B.add_nodes_from(commits, bipartite="commits")
B.add_nodes_from(files, bipartite="files")

# Add edges: commit modifies file
for commit, file_list in commit_file_map.items():
    for file in file_list:
        B.add_edge(commit, file)

# Visualize using layout that separates node types
pos = {}
pos.update((node, (1, i)) for i, node in enumerate(commits))  # commits on the left
pos.update((node, (2, i)) for i, node in enumerate(files))  # files on the right

plt.figure(figsize=(10, 6))
nx.draw(
    B,
    pos,
    with_labels=True,
    node_color=["skyblue" if n in commits else "lightgreen" for n in B.nodes],
    node_size=2000,
    edge_color="gray",
    font_size=10,
)
plt.title("Commit-File Bipartite Graph")
plt.axis("off")
plt.show()
