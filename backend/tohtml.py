import nbformat
from nbconvert import HTMLExporter

notebook_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/Full_Code_NLP_RAG_Project_Notebook.ipynb"

# Load notebook
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# REMOVE WIDGET METADATA (without touching your original notebook)
if "widgets" in nb["metadata"]:
    del nb["metadata"]["widgets"]

for cell in nb["cells"]:
    if "metadata" in cell and "widgets" in cell["metadata"]:
        del cell["metadata"]["widgets"]

# Convert to HTML
html_exporter = HTMLExporter()
html_exporter.exclude_input_prompt = True
html_exporter.exclude_output_prompt = True

(body, resources) = html_exporter.from_notebook_node(nb)

# Save file
with open("/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/Full_Code_NLP_RAG_Project_Notebook.html", "w", encoding="utf-8") as f:
    f.write(body)

print("HTML generated successfully!")