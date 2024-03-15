import argparse
import requests
import json

def interactive_mode(text):
    """Handle interactive mode where the user can input multiple questions."""
    print("Entering interactive mode with the transcribed text. Type 'exit' to quit.")
    while True:
        question = input("Enter your question: ")
        if question.lower() == 'exit':
            break
        else:
            # Assuming that 'text' should be included in the payload
            get_response(text=text, question=question)

def get_response(text, question, model='mistral'):
    """Send request to the Ollama API with the transcribed text and print the response."""
    # Prepare the API request payload, assuming 'prompt' needs both the text and the question
    prompt_format = f"{text}\n\n###\n\n{question}"
    payload = {
        "model": model,
        "prompt": prompt_format,
        "stream": False,
    }

    # Specify the Ollama API endpoint URL
    api_url = 'http://localhost:11434/api/generate'

    # Make the API request
    response = requests.post(api_url, json=payload)  # Use json=payload to automatically set Content-Type to application/json

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        json_response = response.json()
        print("Response from the model:", json_response.get("response"))
    else:
        print("Failed to get a response from the model, status code:", response.status_code)

def main():
    parser = argparse.ArgumentParser(description='Interact with the Ollama API using the transcribed text.')
    parser.add_argument('-t', '--text', required=True, help='The transcribed text to analyze and ask questions about')
    args = parser.parse_args()
    interactive_mode(args.text)

if __name__ == "__main__":
    main()
