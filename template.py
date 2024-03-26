#!/usr/bin/env python

import argparse
import requests
import subprocess

def get_input_text():
    """Function to get the input text. Adjust this method to obtain the text as needed."""
    # Placeholder for text input, adjust this method as needed.
    return "Please replace this text with the actual input method."

def interactive_mode():
    """Handle interactive mode where the user can input multiple questions."""
    text = get_input_text()
    print("Entering interactive mode. Type 'exit' to quit.")
    while True:
        question = input("Enter your question: ")
        if question.lower() == 'exit':
            break
        else:
            get_response(text=text, question=question)

def quick_mode(question):
    """Handle quick mode where the user can input a single question."""
    text = get_input_text()
    print("Quick mode: processing your question.")
    get_response(text=text, question=question)

def ollama_mode():
    """Start chat mode using `ollama run mistral`."""
    print("Starting Ollama Mistral in chat mode...")
    try:
        subprocess.run(["ollama", "run", "mistral"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Ollama Mistral in chat mode: {e}")

def get_response(text, question, model='mistral'):
    """Send request to the Ollama API with the transcribed text and print the response."""
    prompt_format = f"{text}\n\n###\n\n{question}"
    payload = {
        "model": model,
        "prompt": prompt_format,
        "stream": False,
    }
    api_url = 'http://localhost:11434/api/generate'
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        json_response = response.json()
        print("Response from the model:", json_response.get("response"))
    else:
        print("Failed to get a response from the model, status code:", response.status_code)

def main():
    parser = argparse.ArgumentParser(description='Interact with the Ollama API or start Ollama Mistral in chat mode. Reminder: You need to install Ollama before running this CLI.')
    parser.add_argument('-q', '--question', help='Ask a single question in quick mode')
    parser.add_argument('-o', '--ollama', action='store_true', help='Start Ollama Mistral in chat mode')
    args = parser.parse_args()

    if args.ollama:
        ollama_mode()
    elif args.question:
        quick_mode(args.question)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
