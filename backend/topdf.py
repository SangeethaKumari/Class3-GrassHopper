from playwright.sync_api import sync_playwright
import os

html_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/Full_Code_NLP_RAG_Project_Notebook.html"
pdf_path = "/Users/sangeetha/Supportvector2026/llm/projects/llmclassprojects/Class3-GrassHopper/backend/Full_Code_NLP_RAG_Project_Notebook.pdf"

print("Starting PDF conversion... this may take a few seconds.")

# Use Playwright to render the HTML and save it as PDF
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # We must load via file:// protocol
    file_uri = f"file://{os.path.abspath(html_path)}"
    
    page.goto(file_uri)
    
    # Save to PDF (A4 format with background colors)
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
    )
    
    browser.close()

print(f"Success! PDF saved to: {pdf_path}")
