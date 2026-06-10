import requests
import json

def test_codegemma_ollama():
    """
    Simpler script to call CodeGemma via local Ollama API.
    Zero complex dependencies (uses standard requests library).
    """
    model_name = "codegemma:7b"
    url = "http://localhost:11434/api/generate"
    
    prompt = "Write a Python function to find the maximum of three numbers."
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    print(f"--- Calling CodeGemma via Ollama (Local) ---")
    print(f"Prompt: {prompt}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\n--- Answer ---")
            print(result.get("response", "No response field found."))
        elif response.status_code == 404:
            print(f"\nError: Model '{model_name}' not found.")
            print(f"Tip: Run 'ollama pull {model_name}' in your terminal first.")
        else:
            print(f"\nError: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to Ollama.")
        print("Tip: Make sure the Ollama app is running on your machine.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    test_codegemma_ollama()
