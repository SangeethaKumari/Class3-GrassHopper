import os
import nbformat
from nbconvert import HTMLExporter
from playwright.sync_api import sync_playwright

notebook_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/huggingface _may7/Full_Code_SuperKart_Model_Deployment_Notebook.ipynb"
html_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/huggingface _may7/Full_Code_SuperKart_Model_Deployment_Notebook.html"
pdf_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/huggingface _may7/Full_Code_SuperKart_Model_Deployment_Notebook.pdf"

print("1. Loading notebook...")
with open(notebook_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# Strip out widgets to prevent conversion crashes
if "widgets" in nb.get("metadata", {}):
    del nb["metadata"]["widgets"]

for cell in nb["cells"]:
    if "widgets" in cell.get("metadata", {}):
        del cell["metadata"]["widgets"]

print("2. Converting to HTML...")
html_exporter = HTMLExporter()
html_exporter.exclude_input_prompt = True
html_exporter.exclude_output_prompt = True
(body, resources) = html_exporter.from_notebook_node(nb)

# Save the temporary HTML file
with open(html_path, "w", encoding="utf-8") as f:
    f.write(body)

print("3. Rendering HTML to PDF using Playwright (Chromium)...")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load the HTML file we just created
        file_uri = f"file://{os.path.abspath(html_path)}"
        page.goto(file_uri)
        
        # Save to PDF
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        )
        browser.close()
        
    print(f"Success! PDF generated at: {pdf_path}")

finally:
    # Cleanup the temporary HTML file
    if os.path.exists(html_path):
        print(f"Success! html generated at: {html_path}")

        #os.remove(html_path)
