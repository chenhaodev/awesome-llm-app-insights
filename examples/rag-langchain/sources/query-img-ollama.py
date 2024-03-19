import argparse
import base64
import requests
import json

def encode_image_to_base64(image_path):
    """Encode the image to a base64-encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def interactive_mode(model, base64_image_string):
    """Handle interactive mode where the user can input multiple questions."""
    print("Entering interactive mode. Type 'exit' to quit.")
    while True:
        question = input("Enter your question: ")
        if question.lower() == 'exit':
            break
        else:
            get_response(model, base64_image_string, question)

def get_response(model, base64_image_string, question):
    """Send request to the API and print the response."""
    # Prepare the API request payload
    payload = {
        "model": model,
        "prompt": question,
        "stream": False,
        "images": [base64_image_string]
    }

    # Specify the API endpoint URL
    api_url = 'http://localhost:11434/api/generate'

    # Make the API request
    response = requests.post(api_url, data=json.dumps(payload))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        json_response = response.json()
        print("Response from the model:", json_response.get("response"))
    else:
        print("Failed to get a response from the model, status code:", response.status_code)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Interact with the Ollama API to analyze images.')
    parser.add_argument('-f', '--filepath', required=True, help='File path of the image to analyze')
    parser.add_argument('-q', '--question', help='Question or prompt for the model')
    parser.add_argument('-m', '--model', default='llava:13b', help='Model to use (default: llava:13b)')
    args = parser.parse_args()

    # Convert the image to base64
    base64_image_string = encode_image_to_base64(args.filepath)

    if args.question:
        # Single question mode
        get_response(args.model, base64_image_string, args.question)
    else:
        # Interactive mode
        interactive_mode(args.model, base64_image_string)

if __name__ == "__main__":
    main()
