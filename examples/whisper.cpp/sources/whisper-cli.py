#!/usr/bin/env python

import os
import argparse
import subprocess
import sys

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

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper.')

    # Add the arguments
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the audio file')
    parser.add_argument('-m', '--model', type=str, default='/Users/chenhao/Github/whisper.cpp/models/ggml-medium.en-distil.bin', help='Path to the model file (default: /Users/chenhao/Github/whisper.cpp/models/ggml-medium.en-distil.bin)')
    parser.add_argument('-w', '--whisper-path', type=str, default='/Users/chenhao/Github/whisper.cpp/', help='Path to the Whisper executable directory (default: /Users/chenhao/Github/whisper.cpp/)')

    # Execute the parse_args() method
    args = parser.parse_args()

    # Create an instance of AudioTranscriber
    transcriber = AudioTranscriber(args.whisper_path, args.model)

    # Process the audio file
    transcriber.process_audio(args.file)