import os
import networkx as nx
import matplotlib.pyplot as plt

# Define color by file extension
EXTENSION_COLOR_MAP = {
    ".py": "skyblue",
    ".js": "lightgreen",
    ".html": "salmon",
    ".css": "violet",
    ".json": "khaki",
    ".ts": "lightgray",
}

def get_file_color(filename):
    ext = os.path.splitext(filename)[1]
    return EXTENSION_COLOR_MAP.get(ext, "white")

def draw_graph(G):
    plt.figure(figsize=(8, 6), constrained_layout=True)
    pos = nx.spring_layout(G, seed=42)
    node_colors = [G.nodes[n]["color"] for n in G.nodes]

    nx.draw(
        G,
        pos,
        with_labels=True,
        labels={n: os.path.basename(n) for n in G.nodes},
        node_color=node_colors,
        node_size=1200,
        edge_color="gray",
        font_size=9,
        arrows=True,
        linewidths=0.5,
    )

    plt.title("📁 File Dependency Graph (Sample Mock Project)")
    plt.show()

def create_sample_mock_graph():
    # Simulate file structure
    files = [
        "folder1/main.py",
        "folder2/utils.js",
        "folder3/index.html",
        "folder4/style.css",
        "folder5/helper.py",
        "folder6/app.js",
        "folder7/config.json"
    ]

    # Simulated dependencies (you can tweak these to create new relationships)
    dependencies = {
        "folder1/main.py": ["folder5/helper.py", "folder7/config.json"],
        "folder2/utils.js": ["folder6/app.js"],
        "folder3/index.html": ["folder4/style.css", "folder2/utils.js"],
        "folder5/helper.py": ["folder7/config.json"],
        "folder6/app.js": ["folder7/config.json"],
        "folder4/style.css": [],
        "folder7/config.json": [],
    }
    # files = [
    #     "package.json",
    #     "jsconfig.json",
    #     ".gitignore",
    #     "public/img/partners/ideafoundry.png",
    # ]

    # dependencies = {
    #     "public/img/journey/enterprises/1.jpg": [],
    #     "public/img/journey/enterprises/3.jpg": [],
    #     "public/img/journey/enterprises/4.jpg": [],
    #     "package.json": [],
    #     ".gitignore": [],

    # }

    # Build graph
    G = nx.DiGraph()
    for file in files:
        G.add_node(file, color=get_file_color(file))

    for src, deps in dependencies.items():
        for dest in deps:
            G.add_edge(src, dest)

    return G

# Run it!
G = create_sample_mock_graph()
draw_graph(G)
