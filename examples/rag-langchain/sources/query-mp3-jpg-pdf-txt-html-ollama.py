#!/usr/bin/env python

import argparse
import base64
import requests
import json
import subprocess
import os
import sys
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata

class ChatPDF:
    def __init__(self, model='mistral'):
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self.model = ChatOllama(model=model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template("""
            <s> [Instruction] You are an assistant tasked with answering questions based on the provided document. Utilize the context from the document to formulate your response. If the answer is not available within the document, indicate that the information is not available. Aim for responses that are direct, informative, and no longer than three sentences. [/Instruction] </s>
            [Instruction] Question: {question}
            Context: {context}
            Answer: [/Instruction]
        """)

    def ingest(self, file_path: str):
        file_type = file_path.split('.')[-1].lower()
        try:
            if file_type == 'pdf':
                docs = PyPDFLoader(file_path=file_path).load()
            elif file_type == 'html':
                docs = UnstructuredHTMLLoader(file_path=file_path).load()
            elif file_type == 'txt':
                docs = TextLoader(file_path=file_path).load()
            else:
                return "Unsupported file type"
        except Exception as e:
            return f"Failed to load document: {str(e)}"

        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.2,
            },
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())

    def ask(self, query: str):
        if not self.chain:
            return "Please, add a document first."

        try:
            return self.chain.invoke(query)
        except Exception as e:
            return f"Error during query processing: {str(e)}"

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None

class ChatMode:
    def __init__(self, model='mistral'):
        self.model = model

    def get_response(self, question):
        """Send request to the Ollama API with the question and print the response."""
        payload = {
            "model": self.model,
            "prompt": question,
            "stream": False,
        }
        api_url = 'http://localhost:11434/api/generate'
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            json_response = response.json()
            print("Response from the model:", json_response.get("response"))
        else:
            print("Failed to get a response from the model, status code:", response.status_code)

    def interactive_mode(self):
        """Handle interactive mode where the user can input multiple questions."""
        print("Entering interactive mode. Type 'exit' to quit.")
        while True:
            question = input("Enter your question: ")
            if question.lower() == 'exit':
                break
            else:
                self.get_response(question=question)

    def quick_mode(self, question):
        """Handle quick mode where the user can input a single question."""
        print("Quick mode: processing your question.")
        self.get_response(question=question)

    def ollama_mode(self):
        """Start chat mode using `ollama run mistral`."""
        print("Starting Ollama Mistral in chat mode...")
        try:
            subprocess.run(["ollama", "run", "mistral"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to start Ollama Mistral in chat mode: {e}")

class ChatImage:
    def __init__(self, model='llava:13b'):
        self.model = model
        self.base64_image_string = None

    def encode_image_to_base64(self, image_path):
        """Encode the image to a base64-encoded string."""
        with open(image_path, "rb") as image_file:
            self.base64_image_string = base64.b64encode(image_file.read()).decode('utf-8')

    def get_response(self, question):
        """Send request to the API and print the response."""
        if not self.base64_image_string:
            print("Please provide an image using the 'encode_image_to_base64' method before asking a question.")
            return

        payload = {
            "model": self.model,
            "prompt": question,
            "stream": False,
            "images": [self.base64_image_string]
        }
        api_url = 'http://localhost:11434/api/generate'
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            json_response = response.json()
            print("Response from the model:", json_response.get("response"))
        else:
            print(f"Failed to get a response from the model, status code: {response.status_code}", file=sys.stderr)

    def interactive_mode(self):
        """Handle interactive mode where the user can input multiple questions."""
        print("Entering interactive mode. Type 'exit' to quit.")
        while True:
            question = input("Enter your question: ")
            if question.lower() == 'exit':
                break
            else:
                self.get_response(question)

class AudioTranscriber:
    def __init__(self, whisper_exe_path, model_path):
        self.whisper_exe_path = whisper_exe_path
        self.model_path = model_path

    def convert_mp3_to_wav(self, audio_file_path):
        # Construct the command to convert MP3 to WAV using ffmpeg
        wav_file_path = os.path.splitext(audio_file_path)[0] + '.wav'
        command = [
            'ffmpeg',
            '-i', audio_file_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            wav_file_path
        ]

        # Run the command to convert the audio file
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully converted {audio_file_path} to {wav_file_path}")
            return wav_file_path
        else:
            print("Error converting audio:", result.stderr, file=sys.stderr)
            return None

    def transcribe_audio(self, audio_file_path, output_format='text'):
        # Construct the command to run the Whisper CLI
        command = [
            self.whisper_exe_path + 'main',
            '-m', self.model_path,
            '-f', audio_file_path,
            '-oj',  # Output the result in a JSON file
        ]

        # Run the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Error transcribing audio:", result.stderr, file=sys.stderr)

    @staticmethod
    def download_model():
        print("To download the model, follow these steps:")
        print("1. Clone OpenAI whisper and whisper.cpp:")
        print("   git clone https://github.com/openai/whisper")
        print("   git clone https://github.com/ggerganov/whisper.cpp")
        print("2. Navigate to the models directory:")
        print("   cd whisper.cpp/models")
        print("3. Clone the model repositories:")
        print("   git clone https://huggingface.co/distil-whisper/distil-medium.en")
        print("   git clone https://huggingface.co/distil-whisper/distil-large-v2")
        print("4. Convert the models to ggml format:")
        print("   python3 ./convert-h5-to-ggml.py ./distil-medium.en/ ../../whisper .")
        print("   mv ggml-model.bin ggml-medium.en-distil.bin")
        print("   python3 ./convert-h5-to-ggml.py ./distil-large-v2/ ../../whisper .")
        print("   mv ggml-model.bin ggml-large-v2-distil.bin")
        print("After completing these steps, you will have the models in the required format.")

    def process_audio(self, audio_file_path):
        # Check if the model file exists
        if not os.path.exists(self.model_path):
            print(f"Model file not found: {self.model_path}")
            print("Please download the model first.")
            self.download_model()
            sys.exit(1)

        # Check if the input file is in MP3 format
        if audio_file_path.lower().endswith('.mp3'):
            # Convert MP3 to WAV
            wav_file_path = self.convert_mp3_to_wav(audio_file_path)
            if wav_file_path:
                # Transcribe the converted WAV file
                self.transcribe_audio(wav_file_path)
        else:
            # Transcribe the audio file directly
            self.transcribe_audio(audio_file_path)

class FileHandler:
    def __init__(self, whisper_path):
        self.whisper_path = whisper_path

    def handle_document(self, file_path, model, text):
        chat_document = ChatPDF(model=model)
        chat_document.ingest(file_path)

        if text:
            answer = chat_document.ask(text)
            print(f"Answer: {answer}")
        else:
            print("Document mode: type 'exit' to quit.")
            while True:
                question = input("Ask a question about the document: ")
                if question.lower() == 'exit':
                    break
                answer = chat_document.ask(question)
                print(f"Answer: {answer}")

        chat_document.clear()

    def handle_image(self, file_path, model, text):
        chat_image = ChatImage(model=model)
        chat_image.encode_image_to_base64(file_path)

        if text:
            # Single question mode
            chat_image.get_response(text)
        else:
            # Interactive mode
            chat_image.interactive_mode()

    def handle_audio(self, file_path, model):
        transcriber = AudioTranscriber(self.whisper_path, model)
        transcriber.process_audio(file_path)

    def handle_chat_mode(self, model, text):
        chat_mode = ChatMode(model=model)

        if text:
            chat_mode.quick_mode(text)
        else:
            chat_mode.ollama_mode()

def main():
    parser = argparse.ArgumentParser(description='Interact with the Ollama API, ask questions about a document, an image, or transcribe an audio file.')
    parser.add_argument('-f', '--file', help='Path to the file (e.g. pdf, html, txt, jpg, png, mp3, wav)')
    parser.add_argument('-t', '--text', help='Text input for the question or prompt')
    parser.add_argument('-m', '--model', type=str, help='Path to the model file (default: depends on file type)')
    parser.add_argument('-w', '--whisper-path', type=str, default='/Users/chenhao/Github/whisper.cpp/', help='Path to the Whisper executable directory (default: /Users/chenhao/Github/whisper.cpp/)')
    args = parser.parse_args()

    file_handler = FileHandler(args.whisper_path)

    if args.file:
        file_extension = args.file.split('.')[-1].lower()
        if file_extension in ['txt', 'html', 'pdf']:
            model = args.model or 'mistral'
            file_handler.handle_document(args.file, model, args.text)
        elif file_extension in ['jpg', 'png']:
            model = args.model or 'llava:13b'
            file_handler.handle_image(args.file, model, args.text)
        elif file_extension in ['mp3', 'wav']:
            model = args.model or '/Users/chenhao/Github/whisper.cpp/models/ggml-medium.en-distil.bin'
            file_handler.handle_audio(args.file, model)
        else:
            print("Unsupported file type. Please provide a file with a supported extension (txt, html, pdf, jpg, png, mp3, wav).")
    else:
        model = args.model or 'mistral'
        file_handler.handle_chat_mode(model, args.text)

if __name__ == "__main__":
    main()
